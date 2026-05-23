import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at     = Column(DateTime, server_default=func.now())
    strategy       = Column(String(50))
    symbols        = Column(ARRAY(String))
    short_period   = Column(Integer)
    long_period    = Column(Integer)
    initial_capital = Column(Float)
    status         = Column(String(20), default="pending")
    stats          = Column(JSONB, nullable=True)
    equity_curve   = Column(JSONB, nullable=True)