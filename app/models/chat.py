# Modelo ORM para chat_interactions
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import VECTOR

from app.database import Base

class ChatInteraction(Base):
    __tablename__ = "chat_interactions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    sector = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    answer = Column(Text)
    operator_name = Column(String(100))
    validated_by = Column(String(20), default="pending")
    embedding = Column(VECTOR(1536))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
