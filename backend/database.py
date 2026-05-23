from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./closira.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(String, primary_key=True, index=True, default=lambda: f"enq_{uuid.uuid4().hex[:8]}")
    channel = Column(String, index=True)
    customer_name = Column(String)
    message = Column(String)
    status = Column(String, default="new")
    sop_matched = Column(String, nullable=True)
    suggested_response = Column(String, nullable=True)
    escalation_reason = Column(String, nullable=True)
    follow_up_time = Column(DateTime, nullable=True)
    follow_up_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
