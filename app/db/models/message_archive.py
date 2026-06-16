"""Message archive model for storing archived conversation messages."""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.models.base import Base


class MessageArchive(Base):
    """
    Stores archived conversation messages.
    
    When active conversation state exceeds a certain message count (e.g., 10),
    older messages are archived to keep checkpoint state bounded.
    """
    __tablename__ = "message_archives"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, nullable=False, index=True)
    session_id = Column(String(128), nullable=False, index=True)
    thread_id = Column(String(256), nullable=False, index=True)  # business_id:session_id
    
    # Message content
    role = Column(String(50), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    archived_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MessageArchive(thread_id={self.thread_id}, role={self.role}, archived_at={self.archived_at})>"
