"""
Message archival service for bounded conversation state.

Implements state trimming policy:
- Keep last ~10 turns (20 messages) in active state
- Archive older messages to message_archive table
- Track archived message count in checkpoint state
"""

from typing import Optional
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from app.db.session import AsyncSessionLocal
from app.db.models.message_archive import MessageArchive


# Configuration for state trimming
ACTIVE_MESSAGE_LIMIT = 20  # Keep last 20 messages (~10 turns) in active state
ARCHIVE_MESSAGE_BATCH_SIZE = 10  # Archive 10 old messages at a time


async def archive_old_messages(
    business_id: int,
    session_id: str,
    thread_id: str,
    messages: list[BaseMessage],
    archived_message_count: int = 0,
) -> tuple[list[BaseMessage], int]:
    """
    Trim messages to ACTIVE_MESSAGE_LIMIT and archive older messages.
    
    Args:
        business_id: Business ID
        session_id: Session ID
        thread_id: Thread ID (business_id:session_id)
        messages: List of active messages
        archived_message_count: Count of previously archived messages
    
    Returns:
        (trimmed_messages, new_archived_count)
    """
    
    if len(messages) <= ACTIVE_MESSAGE_LIMIT:
        # No trimming needed
        return messages, archived_message_count
    
    # Calculate how many messages to archive
    num_to_archive = len(messages) - ACTIVE_MESSAGE_LIMIT
    messages_to_archive = messages[:num_to_archive]
    remaining_messages = messages[num_to_archive:]
    
    # Archive old messages to database
    try:
        async with AsyncSessionLocal() as session:
            archive_rows = []
            
            for msg in messages_to_archive:
                # Determine message role
                if isinstance(msg, HumanMessage):
                    role = "user"
                elif isinstance(msg, AIMessage):
                    role = "assistant"
                elif isinstance(msg, SystemMessage):
                    role = "system"
                elif isinstance(msg, ToolMessage):
                    role = "tool"
                else:
                    role = "other"
                
                # Extract content
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                
                archive_rows.append({
                    "business_id": business_id,
                    "session_id": session_id,
                    "thread_id": thread_id,
                    "role": role,
                    "content": content,
                    "created_at": datetime.utcnow(),
                    "archived_at": datetime.utcnow(),
                })
            
            # Batch insert archived messages
            if archive_rows:
                await session.execute(
                    insert(MessageArchive).values(archive_rows)
                )
                await session.commit()
    
    except Exception as e:
        # Log but don't fail - archival is optional
        print(f"Warning: Failed to archive messages: {e}")
    
    return remaining_messages, archived_message_count + num_to_archive


async def get_archived_messages(
    business_id: int,
    session_id: str,
    limit: Optional[int] = None,
    offset: int = 0,
) -> list[dict]:
    """
    Retrieve archived messages for a conversation.
    
    Args:
        business_id: Business ID
        session_id: Session ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
    
    Returns:
        List of archived message dictionaries
    """
    
    try:
        async with AsyncSessionLocal() as session:
            query = select(MessageArchive).where(
                (MessageArchive.business_id == business_id) &
                (MessageArchive.session_id == session_id)
            ).order_by(MessageArchive.created_at)
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            result = await session.execute(query)
            archived = result.scalars().all()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "archived_at": msg.archived_at.isoformat() if msg.archived_at else None,
                }
                for msg in archived
            ]
    
    except Exception as e:
        print(f"Warning: Failed to retrieve archived messages: {e}")
        return []


async def get_message_statistics(
    business_id: int,
    session_id: str,
) -> dict:
    """
    Get statistics about archived messages for a conversation.
    
    Returns:
        {
            "archived_count": int,
            "earliest_archived": datetime,
            "latest_archived": datetime,
        }
    """
    
    try:
        async with AsyncSessionLocal() as session:
            # Get count
            count_query = select(MessageArchive).where(
                (MessageArchive.business_id == business_id) &
                (MessageArchive.session_id == session_id)
            )
            count_result = await session.execute(count_query)
            count = len(count_result.scalars().all())
            
            if count == 0:
                return {
                    "archived_count": 0,
                    "earliest_archived": None,
                    "latest_archived": None,
                }
            
            # Get earliest and latest
            earliest_query = select(MessageArchive).where(
                (MessageArchive.business_id == business_id) &
                (MessageArchive.session_id == session_id)
            ).order_by(MessageArchive.created_at).limit(1)
            
            latest_query = select(MessageArchive).where(
                (MessageArchive.business_id == business_id) &
                (MessageArchive.session_id == session_id)
            ).order_by(MessageArchive.created_at.desc()).limit(1)
            
            earliest_result = await session.execute(earliest_query)
            latest_result = await session.execute(latest_query)
            
            earliest = earliest_result.scalars().first()
            latest = latest_result.scalars().first()
            
            return {
                "archived_count": count,
                "earliest_archived": earliest.created_at.isoformat() if earliest else None,
                "latest_archived": latest.created_at.isoformat() if latest else None,
            }
    
    except Exception as e:
        print(f"Warning: Failed to get message statistics: {e}")
        return {
            "archived_count": 0,
            "earliest_archived": None,
            "latest_archived": None,
        }
