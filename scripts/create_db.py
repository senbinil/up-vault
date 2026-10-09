import asyncio

import psycopg
from psycopg import sql
from sqlalchemy import make_url

from up_vault.config import settings


async def create_database() -> None:
    database_url = make_url(settings.database_url)
    database_name = database_url.database

    if not database_name:
        raise ValueError("Database name is missing from the DATABASE_URL")

    # psycopg expects libpq conninfo syntax, so drop the SQLAlchemy driver suffix.
    admin_url = make_url(settings.database_admin_url).set(drivername="postgresql")
    conninfo = admin_url.render_as_string(hide_password=False)

    async with (
        await psycopg.AsyncConnection.connect(
            conninfo,
            autocommit=True,
        ) as conn,
        conn.cursor() as cursor,
    ):
        await cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (database_name,),
        )
        if await cursor.fetchone():
            print(f"Database '{database_name}' already exists.")
            return

        await cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
        )
        print(f"Database '{database_name}' created successfully.")


if __name__ == "__main__":
    asyncio.run(create_database())
