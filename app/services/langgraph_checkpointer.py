"""
LangGraph PostgreSQL checkpointer (async-compatible).

AsyncPostgresSaver provides async-compatible checkpoint persistence to PostgreSQL.

IMPORTANT: AsyncPostgresSaver.from_conn_string() is an ASYNC CONTEXT MANAGER.
It does not return the checkpointer directly—it returns a context manager that
yields the checkpointer when entered.

Usage (typically in app/main.py lifespan):
    async with get_checkpointer() as checkpointer:
        await checkpointer.setup()  # Initialize (creates tables)
        # Store checkpointer for use: app.state.checkpointer = checkpointer
        # Build graph: app.state.graph = build_graph(checkpointer)
        # Context manager cleanup happens automatically on exit
"""

from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import DATABASE_URL


def get_postgres_uri() -> str:
    """
    Convert SQLAlchemy async URL into psycopg URL.
    
    SQLAlchemy format: postgresql+asyncpg://user:password@host/dbname
    LangGraph format: postgresql://user:password@host/dbname
    """
    return DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql://",
        1,
    )


def get_checkpointer_context_manager():
    """
    Get AsyncPostgresSaver as an async context manager.
    
    Returns:
        Async context manager that yields AsyncPostgresSaver on enter.
        
    Pattern:
        async with get_checkpointer_context_manager() as checkpointer:
            await checkpointer.setup()
            # Use checkpointer
            # Cleanup happens automatically on exit
    
    Note:
        from_conn_string() is NOT an async function; it returns the context manager
        synchronously. The actual connection happens when entering the context.
    """
    postgres_uri = get_postgres_uri()
    return AsyncPostgresSaver.from_conn_string(postgres_uri)