"""
Modelo para logs de execução do sistema multiagente.
"""

from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class ExecutionLog(Base):
    """Modelo para armazenar logs de execução do sistema multiagente."""
    
    __tablename__ = "execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Dados da execução
    input_text = Column(Text, nullable=False)
    output_narrative = Column(Text, nullable=False)
    execution_time = Column(Float, nullable=False)  # em segundos
    
    # Agentes utilizados
    agents_used = Column(JSON, nullable=False, default=list)
    
    # Status da execução
    success = Column(Boolean, nullable=False, default=True)
    
    # Metadados adicionais
    execution_metadata = Column(JSON, nullable=True, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExecutionLog(id={self.id}, user_id={self.user_id}, success={self.success})>"