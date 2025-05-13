import asyncio

import orjson
from sqlalchemy import UniqueConstraint, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from uuid6 import uuid7

from src.infrastructure.base.repository.base import SQLAlchemyRepository
from src.infrastructure.base.repository.user_reader import BaseUserReader
from src.infrastructure.base.repository.user_writer import BaseUserWriter
from src.infrastructure.db.models import BaseModel
from src.infrastructure.db.uow import SQLAlchemyUoW


async def test_same_session_for_uow_writer_reader(di_container):
    async with di_container() as c:
        uow = await c.get(SQLAlchemyUoW)
        user_reader = await c.get(BaseUserReader)
        user_writer = await c.get(BaseUserWriter)
        sqlrepo = await c.get(SQLAlchemyRepository)

        assert isinstance(uow, SQLAlchemyUoW)
        assert isinstance(uow._session, AsyncSession)

        assert isinstance(user_reader, SQLAlchemyRepository)
        assert isinstance(user_writer, SQLAlchemyRepository)

        assert user_reader._session == uow._session
        assert sqlrepo._session == uow._session


async def test_database_connection_establishment(di_container):
    """Test database connection can be established properly"""
    engine = await di_container.get(AsyncEngine)

    # Verify engine is created and can connect to the database
    assert engine is not None

    # Test simple query execution
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        row = result.scalar()
        assert row == 1


async def test_database_schema_existence(di_container):
    """Test that all expected tables exist in the database"""
    engine = await di_container.get(AsyncEngine)

    async with engine.connect() as conn:
        # Get all table names in the database
        result = await conn.execute(
            text(
                "SELECT table_name "
                "FROM information_schema.tables "
                "WHERE table_schema='public'"
            )
        )
        tables = [row[0] for row in result.fetchall()]

        # Verify expected tables exist
        assert "user" in tables


async def test_database_user_column_definitions(di_container):
    """Test that table columns match expected definitions"""
    engine = await di_container.get(AsyncEngine)

    async with engine.connect() as conn:
        # Check user table columns
        result = await conn.execute(
            text(
                "SELECT column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_name = 'user'"
            )
        )
        columns = {row[0]: row[1] for row in result.fetchall()}

        assert "id" in columns
        assert "username" in columns
        assert "email" in columns
        assert "hashed_password" in columns
        assert "deleted_at" in columns
        assert "version" in columns

        assert columns.get("deleted_at") == "timestamp with time zone"
        assert columns["username"] in ("character varying", "varchar")


async def test_database_constraints(di_container):
    """Test database constraints are properly defined"""
    metadata = BaseModel.metadata

    # Get the User model table definition
    user_table = metadata.tables["user"]

    # Verify primary key constraint
    assert len(user_table.primary_key.columns) == 1
    assert "id" in [col.name for col in user_table.primary_key.columns]

    # Verify unique constraints
    unique_constraints = [
        const for const in user_table.constraints if isinstance(const, UniqueConstraint)
    ]
    assert any(
        "username" in [col.name for col in const.columns]
        for const in unique_constraints
    )

    assert any(
        "id" in [col.name for col in const.columns] for const in unique_constraints
    )


async def test_transaction_isolation(di_container):
    values = dict(
        id=str(uuid7()),
        username="isolation_test",
        email="isolation_test@test.py",
        hashed_pass=orjson.dumps("asdasdasdasd22SD"),
        version=1,
    )
    async with di_container() as c:
        # Create two separate UoWs to test isolation
        uow1 = await c.get(SQLAlchemyUoW)
        # Start a transaction in first session but don't commit
        await uow1._session.execute(
            text(
                """
                INSERT INTO "user" (id, username, email, hashed_password, version)
                VALUES (:id, :username, :email, :hashed_pass, :version)
                """
            ),
            values,
        )

    async with di_container() as c:
        uow2 = await c.get(SQLAlchemyUoW)
        # In a second session, should not see the uncommitted data
        result = await uow2._session.execute(
            text(
                """
                SELECT username
                FROM "user"
                WHERE username = :username
                """
            ),
            dict(username="isolation_test"),
        )
        assert result.rowcount == 0


async def test_database_connection_pool(di_container):
    """Test database connection pooling works correctly"""
    engine = await di_container.get(AsyncEngine)

    # Check pool configuration
    assert engine.pool.size is not None
    assert engine.pool._max_overflow is not None

    # Simulate multiple simultaneous connections to test pool
    async def execute_query():
        async with engine.connect() as conn:
            await conn.execute(text("SELECT pg_sleep(0.1)"))
            return True

    # Run multiple queries concurrently
    tasks = [asyncio.create_task(execute_query()) for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # All should complete successfully
    assert all(results)
