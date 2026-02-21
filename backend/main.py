from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from database import engine, SessionLocal, Base
import models
import os
from typing import List, Optional
from question_loader import load_questions_from_text

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ESHA's NEET 2026")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for images
os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to ESHA's NEET 2026 API"}

@app.post("/api/load-questions")
def trigger_loading(background_tasks: BackgroundTasks):
    background_tasks.add_task(load_questions_from_text)
    return {"message": "Question loading started in background"}

from rank_predictor import predict_rank
from pydantic import BaseModel

class RankRequest(BaseModel):
    score: int
    total_marks: int

@app.post("/api/rank-estimate")
def get_rank_estimate(request: RankRequest):
    return predict_rank(request.score, request.total_marks)

import time
import uuid
from pydantic import BaseModel

class StartTestRequest(BaseModel):
    duration: int # seconds
    subject: str

class TestStatusResponse(BaseModel):
    session_id: str
    remaining_exam_seconds: float
    current_question_index: int
    remaining_question_seconds: float
    is_active: bool

# In-memory store for active sessions (for simplicity, or use DB if you prefer persistence across server restarts)
# BUT user asked for DB model, so let's use the DB model `TestSession`.

@app.post("/api/start-test")
def start_test(request: StartTestRequest, db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    start_time = time.time()
    end_time = start_time + request.duration
    
    session = models.TestSession(
        id=session_id,
        start_time=start_time,
        end_time=end_time,
        current_question_id=0, # Start at index 0
        question_start_time=start_time, # First question starts now
        duration_seconds=request.duration
    )
    db.add(session)
    db.commit()
    
    return {"session_id": session_id}

@app.get("/api/test-status/{session_id}")
def get_test_status(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    current_time = time.time()
    remaining_exam = max(0, session.end_time - current_time)
    
    # Question timer logic (60s limit)
    # If 60s passed, should frontend auto-trigger next? 
    # Or strict server check? 
    # For now, just calculation.
    
    q_elapsed = current_time - session.question_start_time
    remaining_question = max(0, 60 - q_elapsed)
    
    return {
        "session_id": session.id,
        "remaining_exam_seconds": remaining_exam,
        "current_question_index": session.current_question_id,
        "remaining_question_seconds": remaining_question,
        "is_active": remaining_exam > 0
    }

@app.post("/api/update-question-index")
def update_question_index(session_id: str, new_index: int, db: Session = Depends(get_db)):
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.current_question_id = new_index
    session.question_start_time = time.time() # Reset question timer
    db.commit()
    return {"message": "Updated"}

class QuestionResponse(BaseModel):
    id: int
    subject: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    image_path: Optional[str] = None
    section: Optional[str] = "A" 
    subsection: Optional[str] = None 
    
    class Config:
        orm_mode = True

@app.get("/api/questions", response_model=List[QuestionResponse])
def get_questions(
    subject: str = "Full NEET", 
    limit: int = 50, 
    duration: int = 10800, 
    db: Session = Depends(get_db)
):
    questions = []
    
    if subject == "Full NEET":
        # FULL NEET PATTERN: 200 Questions
        # Physics: 50 (35 A + 15 B)
        # Chemistry: 50 (35 A + 15 B)
        # Biology: 100 (Botany 35A+15B, Zoology 35A+15B)
        
        def fetch_and_tag(subj, count_a, count_b, sub=None):
            pool = db.query(models.Question).filter(models.Question.subject == subj).order_by(func.random()).limit(count_a + count_b).all()
            tagged = []
            for i, q in enumerate(pool):
                q.section = "A" if i < count_a else "B"
                q.subsection = sub if sub else subj
                tagged.append(q)
            return tagged

        questions.extend(fetch_and_tag("Physics", 35, 15))
        questions.extend(fetch_and_tag("Chemistry", 35, 15))
        
        bio_pool = db.query(models.Question).filter(models.Question.subject == "Biology").order_by(func.random()).limit(100).all()
        botany = bio_pool[:50]
        zoology = bio_pool[50:]
        
        for i, q in enumerate(botany):
            q.section = "A" if i < 35 else "B"
            q.subsection = "Botany"
            
        for i, q in enumerate(zoology):
            q.section = "A" if i < 35 else "B"
            q.subsection = "Zoology"
            
        questions.extend(botany)
        questions.extend(zoology)
        
    else:
        # INDIVIDUAL SUBJECT: 40 Qs, No Sections
        # Wait, user said "Individual: 40 Qs, simple".
        pool = db.query(models.Question).filter(models.Question.subject == subject).order_by(func.random()).limit(40).all()
        for q in pool:
            q.section = "A"
            q.subsection = subject
        questions.extend(pool)
    
    return questions

@app.get("/api/subjects")
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(models.Question.subject).distinct().all()
    return [s[0] for s in subjects]

class ClearQuestionsRequest(BaseModel):
    confirm: bool

@app.post("/api/clear-questions")
def clear_questions(request: ClearQuestionsRequest, db: Session = Depends(get_db)):
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Confirmation required to clear questions")
    
    try:
        db.query(models.Question).delete()
        db.commit()
        print("All questions removed from database.")
        return {"status": "success", "message": "All questions cleared from database"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reload-questions")
def reload_questions(request: ClearQuestionsRequest, db: Session = Depends(get_db)):
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Confirmation required to reload questions")
        
    try:
        # 1. Clear
        db.query(models.Question).delete()
        db.commit()
        print("All questions removed from database.")
        
        # 2. Reload
        # load_questions_from_text creates its own session, so we don't need to pass db
        print("Reloading questions from .txt files...")
        stats = load_questions_from_text()
        
        return {
            "status": "success", 
            "message": "Questions cleared and reloaded", 
            "total_loaded": stats.get("total_added", 0) if stats else 0,
            "stats": stats
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
