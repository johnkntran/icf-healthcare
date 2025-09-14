import time
import string
import random
import uuid
import os
import binascii

import asyncpg
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.store.base import BaseStore
from langgraph.store.postgres.aio import AsyncPostgresStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer

from models import LLMModel, Feedback, LLMInsight, Insight
from utils import write_temp_tokens, read_temp_tokens
from services import get_conn, create_insight, get_feedback


class State(MessagesState):
    model: LLMModel
    feedback: Feedback
    insight: LLMInsight | None 


class TokenAsyncHandler(AsyncCallbackHandler):
    """
    When using structured output, you lose the raw LLM response, 
    which contains token information. You need this callback handler to
    access the raw response again and retrieve metadata, such as tokens used.
    """
    async def on_llm_end(self, llm_result: LLMResult, **kwargs) -> None:
        tokens = llm_result.generations[0][0].message.usage_metadata['total_tokens']
        write_temp_tokens(tokens)


llms = {
    LLMModel.CLAUDE_3_7_SONNET: init_chat_model('anthropic:claude-3-7-sonnet-20250219', callbacks=[TokenAsyncHandler()]).with_structured_output(LLMInsight),
    LLMModel.GPT_O4_MINI: init_chat_model('openai:o4-mini', callbacks=[TokenAsyncHandler()]).with_structured_output(LLMInsight),
}

async def step1(state: State) -> dict:
    messages = state['messages']
    feedback = state['feedback'].model_dump()
    messages.append(SystemMessage(
        'You are an healthcare business assistant helping out with analyzing user '
        'feedback for an EHR and producing an "insight" summary. Please scrub any PII '
        '(e.g. name, SSN, phone number, address) you encounter during the course of '
        'your analysis and replace the PII with the word "[redacted]" in your summary.'
    ))
    messages.append(HumanMessage(
        'Can you analyze the following feedback and generate an insight summary?'
        f"\n\n--------------------\n\n{feedback['title'] + '\n\n' + feedback['body']}"
    ))
    return {'messages': messages}


async def step2(state: State) -> dict:
    messages = state['messages']
    llm = llms[state['model']]
    t1 = time.time()
    insight = await llm.ainvoke(messages)
    t2 = time.time()
    insight.tokens = read_temp_tokens()
    insight.latency = t2 - t1
    return {'insight': insight}


async def step3(state: State, config: RunnableConfig, *, store: BaseStore) -> None:
    llm_insight = state['insight']
    feedback = state['feedback']
    llm_insight.feedback_id = feedback.id
    conn = await get_conn()
    try:
        insight = await create_insight(conn, llm_insight)
    finally:
        await conn.close()


builder = StateGraph(state_schema=State)
builder.add_node('step1', step1)
builder.add_node('step2', step2)
builder.add_node('step3', step3)
builder.add_edge(START, 'step1')
builder.add_edge('step1', 'step2')
builder.add_edge('step2', 'step3')
builder.add_edge('step3', END)


DATABASE_URL = os.environ['DATABASE_URL']
ENCRYPTION_KEY = binascii.a2b_hex(os.environ['LANGGRAPH_ENCRYPTION_KEY'])
serde = EncryptedSerializer.from_pycryptodome_aes(key=ENCRYPTION_KEY)

async def generate_insight(
    conn: asyncpg.connection.Connection, 
    feedback_id: str,
) -> Insight:
    async with (
        AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer, 
        AsyncPostgresStore.from_conn_string(DATABASE_URL) as store,
    ):
        checkpointer.serde = serde
        await store.setup()
        await checkpointer.setup()
        thread_id = str(uuid.uuid4())
        user_id = ''.join(random.sample(string.ascii_letters, 10))
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        graph = builder.compile(checkpointer=checkpointer, store=store)
        feedback = await get_feedback(conn, feedback_id)
        state = {
            "messages": [],
            "model": LLMModel.CLAUDE_3_7_SONNET, # Just use Claude for now, we can expose this in FastAPI later
            'feedback': feedback,
            'insight': None,
        }
        graph_resp = await graph.ainvoke(state, config)
        llm_insight = graph_resp['insight']
        return Insight(
            feedback=feedback, 
            sentiment=llm_insight.sentiment,
            key_topics=llm_insight.key_topics,
            action_required=llm_insight.action_required,
            summary=llm_insight.summary,
            tokens=llm_insight.tokens,
            latency=llm_insight.latency,
        )