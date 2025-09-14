from typing import Annotated

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from models import User, Feedback
from services import get_conn, get_or_create_user, create_feedback, list_feedback


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
async def healthcheck():
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


@app.get('/feedback')
async def get_feedbacks(username: str) -> list[Feedback]:
    conn = await get_conn()
    try:
        return list_feedback(username)
    finally:
        await conn.close()
    

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
