import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager

async def create_tables(conn):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id VARCHAR(128) PRIMARY KEY,
            user_name VARCHAR(128) NOT NULL,
            password VARCHAR(128) NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP
        );
    ''')

async def init_pg(app):
    pool = await asyncpg.create_pool(
        host=app['config']['postgres']['host'],
        port=app['config']['postgres']['port'],
        database=app['config']['postgres']['database'],
        user=app['config']['postgres']['user'],
        password=app['config']['postgres']['password'],
        min_size=app['config']['postgres']['min_size'],
        max_size=app['config']['postgres']['max_size']
    )

    async with pool.acquire() as conn:
        await create_tables(conn)

    app['db_pool'] = pool

async def close_pg(app):
    await app['db_pool'].close()

@asynccontextmanager
async def get_db():
    db: Pool = app['db_pool']
    async with db.acquire() as conn:
        async with conn.transaction():
            yield conn

async def create_session(session_id: str, user_id: int, start_time: datetime):
    async with get_db() as conn:
        await conn.execute(
            'INSERT INTO sessions (session_id, user_id, start_time) VALUES ($1, $2, $3);',
            session_id, user_id, start_time
        )

async def get_session(session_id: str):
    async with get_db() as conn:
        row = await conn.fetchrow(
            'SELECT * FROM sessions WHERE session_id = $1;', session_id
        )
        if row is not None:
            return dict(row)
        else:
            return None

async def update_session(session_id: str, end_time: datetime):
    async with get_db() as conn:
        await conn.execute(
            'UPDATE sessions SET end_time = $2 WHERE session_id = $1;', session_id, end_time
        )
