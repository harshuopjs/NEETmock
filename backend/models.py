from sqlalchemy import Column, Integer, String, Float
from database import Base

class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(String, primary_key=True, index=True) # UUID
    start_time = Column(Float) # UTC timestamp
    end_time = Column(Float) # UTC timestamp
    current_question_id = Column(Integer, default=0) # Index, not db ID
    question_start_time = Column(Float) # UTC timestamp for current question
    duration_seconds = Column(Integer)
    
class Question(Base):
    __tablename__ = "questions"


    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    question_text = Column(String)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_option = Column(String)
    image_path = Column(String, nullable=True)
    year = Column(Integer)
    source_id = Column(String, unique=True, index=True, nullable=True)
