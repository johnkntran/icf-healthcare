import os
import uuid
import datetime

import asyncpg
import pydantic

from models import User, Feedback, Insight, LLMInsight
from encryption import encrypt


async def get_conn() -> asyncpg.connection.Connection:
    DATABASE_URL = os.environ['DATABASE_URL']
    return await asyncpg.connect(dsn=DATABASE_URL)


async def get_or_create_user(
    conn: asyncpg.connection.Connection,
    username: str,
) -> User:
    # Better to raise 400 explicitly, assertion for now (500) as convenience
    assert len(username) < 255, 'Username too long, must be less than 255 chars' 
    async with conn.transaction() as t:
        user_id = str(uuid.uuid4())
        statement = 'INSERT INTO healthcare_user VALUES($1, $2);'
        args = (user_id, username)
        try:
            result = await conn.execute(statement, *args)
        except asyncpg.exceptions.UniqueViolationError:
            await conn.reset() # Username already exists
    user = await conn.fetchrow('SELECT * FROM healthcare_user WHERE username = $1', username)
    return User(**dict(user.items()))


async def create_feedback(
    conn: asyncpg.connection.Connection,
    username: str,
    title: str,
    body: str,
) -> Feedback:
    async with conn.transaction() as t:
        feedback_id = str(uuid.uuid4())
        title_enc, title_nonce = encrypt(title) # Encrypt at rest the title 
        body_enc, body_nonce = encrypt(body) # ... and body 
        created = datetime.datetime.now(tz=datetime.timezone.utc)
        updated = datetime.datetime.now(tz=datetime.timezone.utc)
        sql = '''
            INSERT INTO healthcare_feedback VALUES
            ($1, (SELECT id FROM healthcare_user WHERE username = $2), $3, $4, $5, $6, $7, $8)
            ;
        '''
        args = (feedback_id, username, title_enc, title_nonce, body_enc, body_nonce, created, updated)
        result = await conn.execute(sql, *args)
        data = await conn.fetchrow('''
            SELECT f.id AS feedback_id, u.id AS user_id, *
            FROM healthcare_feedback AS f
            INNER JOIN healthcare_user AS u
              ON f.user_id = u.id
            WHERE f.id = $1;
        ''', feedback_id)
    user = User(id=data['user_id'], username=data['username'])
    feedback = Feedback(
        id=data['feedback_id'],
        user=user,
        title=data['title'],
        title_nonce=data['title_nonce'],
        body=data['body'],
        body_nonce=data['body_nonce'],
        created=data['created'],
        updated=data['updated'],
    )
    return feedback


async def get_feedback(
    conn: asyncpg.connection.Connection, 
    feedback_id: str,
) -> Feedback:
    async with conn.transaction() as t:
        data = await conn.fetchrow('''
            SELECT f.id AS feedback_id, u.id AS user_id, *
            FROM healthcare_feedback AS f
            INNER JOIN healthcare_user AS u
              ON f.user_id = u.id
            WHERE f.id = $1;
        ''', feedback_id)
    return Feedback(
        id=data['feedback_id'],
        user=User(id=data['user_id'], username=data['username']),
        title=data['title'],
        title_nonce=data['title_nonce'],
        body=data['body'],
        body_nonce=data['body_nonce'],
        created=data['created'],
        updated=data['updated'],
    )


async def create_insight(
    conn: asyncpg.connection.Connection, 
    llm_insight: LLMInsight,
) -> Insight:
    async with conn.transaction() as t:
        sql = '''
            INSERT INTO healthcare_insight VALUES ($1, $2, $3, $4, $5, $6, $7)
        '''
        args = (
            str(llm_insight.feedback_id), 
            llm_insight.sentiment, 
            llm_insight.key_topics, 
            llm_insight.action_required, 
            llm_insight.summary, 
            llm_insight.tokens, 
            llm_insight.latency,
        )
        result = await conn.execute(sql, *args)
        data = await conn.fetchrow('''
            SELECT 
              f.id AS feedback_id, 
              u.id AS user_id,
              i.feedback_id AS insight_id,
              *
            FROM healthcare_feedback AS f
            INNER JOIN healthcare_user AS u
              ON f.user_id = u.id
            INNER JOIN healthcare_insight AS i
              ON f.id = i.feedback_id
            WHERE f.id = $1;
        ''', str(llm_insight.feedback_id))
    user = User(id=data['user_id'], username=data['username'])
    feedback = Feedback(
        id=data['feedback_id'],
        user=user,
        title=data['title'],
        title_nonce=data['title_nonce'],
        body=data['body'],
        body_nonce=data['body_nonce'],
        created=data['created'],
        updated=data['updated'],
    )
    insight = Insight(
        feedback=feedback,
        sentiment=data['sentiment'],
        key_topics=data['key_topics'],
        action_required=data['action_required'],
        summary=data['summary'],
        tokens=data['tokens'],
        latency=data['latency'],
    )
    return insight


async def list_feedback_and_insight(
    conn: asyncpg.connection.Connection, 
    username: str,
) -> list[dict]:
    async with conn.transaction() as t:
        rows = await conn.fetch('''
            SELECT 
              f.id AS fdbck_id, 
              u.id AS user_id,
              i.feedback_id AS insight_id,
              *
            FROM healthcare_feedback AS f
            INNER JOIN healthcare_user AS u
              ON f.user_id = u.id
            LEFT JOIN healthcare_insight AS i
              ON f.id = i.feedback_id
            WHERE u.username = $1;
        ''', username)
    results = []
    for row in rows:
        feedback = Feedback(
            id=row['fdbck_id'],
            user=User(id=row['user_id'], username=row['username']),
            title=row['title'],
            title_nonce=row['title_nonce'],
            body=row['body'],
            body_nonce=row['body_nonce'],
            created=row['created'],
            updated=row['updated'],
        )
        if row['insight_id']:
            insight = Insight(
                feedback=feedback,
                sentiment=row['sentiment'],
                key_topics=row['key_topics'],
                action_required=row['action_required'],
                summary=row['summary'],
                tokens=row['tokens'],
                latency=row['latency'],
            )
        else:
            insight = None
        results.append({
            'feedback': feedback.model_dump(),
            'insight': insight.model_dump() if insight else None,
        })
    return results