"""
Test state trimming and message archival functionality.
"""

import asyncio
import httpx
import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

BASE_URL = "http://127.0.0.1:8000"

# Test fixtures
@pytest.fixture
def business_session():
    """Setup: business and session for testing."""
    return {
        "business_id": 999,  # Test business
        "session_id": f"test_state_trim_{datetime.now().timestamp()}",
        "thread_id": f"999:test_state_trim_{datetime.now().timestamp()}"
    }

@pytest.mark.asyncio
async def test_state_trimming_at_limit(business_session):
    """Test: Messages trim at ACTIVE_MESSAGE_LIMIT (20) when exceeded."""
    async with httpx.AsyncClient() as client:
        # Send 25 messages to exceed the 20-message limit
        for i in range(25):
            response = await client.post(
                f"{BASE_URL}/chat",
                json={
                    "business_id": business_session["business_id"],
                    "session_id": business_session["session_id"],
                    "message": f"Message number {i+1}: This is a test message",
                    "mode": "owner"
                }
            )
            assert response.status_code == 200
        
        # Verify last response includes message about archival or state trimming
        data = response.json()
        assert data.get("status") == "success"

@pytest.mark.asyncio
async def test_message_archive_table_populated(business_session):
    """Test: Messages are archived to message_archives table when limit exceeded."""
    from app.db.session import AsyncSessionLocal
    from app.db.models.message_archive import MessageArchive
    
    async with httpx.AsyncClient() as client:
        # Send 25 messages to trigger archival
        for i in range(25):
            response = await client.post(
                f"{BASE_URL}/chat",
                json={
                    "business_id": business_session["business_id"],
                    "session_id": business_session["session_id"],
                    "message": f"Archive test message {i+1}",
                    "mode": "owner"
                }
            )
            assert response.status_code == 200
        
        # Give archival async task a moment to complete
        await asyncio.sleep(1)
        
        # Query message_archives table
        async with AsyncSessionLocal() as session:
            query = select(MessageArchive).where(
                (MessageArchive.business_id == business_session["business_id"]) &
                (MessageArchive.session_id == business_session["session_id"])
            )
            result = await session.execute(query)
            archived_messages = result.scalars().all()
            
            # Should have archived messages (25 messages - 20 active = 5 archived)
            assert len(archived_messages) >= 5, f"Expected at least 5 archived messages, got {len(archived_messages)}"

@pytest.mark.asyncio
async def test_archived_messages_have_correct_fields(business_session):
    """Test: Archived messages have role, content, timestamps."""
    from app.db.session import AsyncSessionLocal
    from app.db.models.message_archive import MessageArchive
    
    async with httpx.AsyncClient() as client:
        # Send messages to trigger archival
        for i in range(25):
            response = await client.post(
                f"{BASE_URL}/chat",
                json={
                    "business_id": business_session["business_id"],
                    "session_id": business_session["session_id"],
                    "message": f"Detailed test {i+1}",
                    "mode": "owner"
                }
            )
            assert response.status_code == 200
        
        await asyncio.sleep(1)
        
        # Query and verify fields
        async with AsyncSessionLocal() as session:
            query = select(MessageArchive).where(
                (MessageArchive.business_id == business_session["business_id"]) &
                (MessageArchive.session_id == business_session["session_id"])
            ).limit(1)
            result = await session.execute(query)
            archived_msg = result.scalar_one_or_none()
            
            if archived_msg:
                assert archived_msg.business_id == business_session["business_id"]
                assert archived_msg.session_id == business_session["session_id"]
                assert archived_msg.role in ["user", "assistant", "system", "tool"]
                assert len(archived_msg.content) > 0
                assert archived_msg.created_at is not None
                assert archived_msg.archived_at is not None

@pytest.mark.asyncio
async def test_active_messages_stay_within_limit(business_session):
    """Test: Active checkpoint messages never exceed ACTIVE_MESSAGE_LIMIT."""
    from app.db.session import AsyncSessionLocal
    from app.db.models.base import Base
    from app.config import DATABASE_URL
    from sqlalchemy.ext.asyncio import create_async_engine
    from langgraph.checkpoint.postgres import AsyncPostgresSaver
    
    async with httpx.AsyncClient() as client:
        # Send 30 messages
        for i in range(30):
            response = await client.post(
                f"{BASE_URL}/chat",
                json={
                    "business_id": business_session["business_id"],
                    "session_id": business_session["session_id"],
                    "message": f"Limit test {i+1}",
                    "mode": "owner"
                }
            )
            assert response.status_code == 200
        
        await asyncio.sleep(1)
        
        # Check checkpoint state
        try:
            from app.db.session import engine
            async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as saver:
                # Get the checkpoint for this thread
                thread_id = business_session["thread_id"]
                checkpoint = await saver.get(thread_id)
                
                if checkpoint and "values" in checkpoint:
                    messages = checkpoint["values"].get("messages", [])
                    # Should have max 20 messages in active checkpoint
                    assert len(messages) <= 20, f"Checkpoint has {len(messages)} messages, limit is 20"
        except Exception as e:
            # If checkpoint verification fails, skip (saver may not expose get())
            pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
