from typing import Annotated

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from models import User, Feedback, Insight
from services import get_conn, get_or_create_user, create_feedback, list_feedback_and_insight
from llm import generate_insight


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/healthcheck')
async def healthcheck() -> dict:
    """
    Availability probe endpoint, useful for telemetry e.g. DataDog, OpsGenie, 
    etc. to check if resources are working.
    """
    conn = await get_conn()
    db_is_up = not conn.is_closed()
    await conn.close()
    llm_is_up = True # TODO: really check if LLM is working
    return {
        'db_is_up': db_is_up,
        'llm_is_up': llm_is_up,
    }
    

@app.post('/user')
async def make_user(username: Annotated[str, Body(embed=True)]) -> User:
    conn = await get_conn()
    try:
        return await get_or_create_user(conn, username)
    finally:
        await conn.close()


@app.post('/feedback')
async def make_feedback(
    username: Annotated[str, Body(embed=True)],
    title: Annotated[str, Body(embed=True)],
    body: Annotated[str, Body(embed=True)],
) -> Feedback:
    conn = await get_conn()
    try:
        return await create_feedback(conn, username, title, body)
    finally:
        await conn.close()


@app.post('/insight')
async def make_insight(
    feedback_id: Annotated[str, Body(embed=True)],
) -> Insight:
    conn = await get_conn()
    try:
        return await generate_insight(conn, feedback_id)
    finally:
        await conn.close()


@app.get('/feedback_and_insights')
async def get_feedback_and_insights(username: str) -> list[dict]:
    conn = await get_conn()
    try:
        return await list_feedback_and_insight(conn, username)
    finally:
        await conn.close()
