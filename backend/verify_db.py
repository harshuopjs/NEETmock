from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Question, Base
from database import SessionLocal

db = SessionLocal()

from sqlalchemy import func

# Count by Subject
results = db.query(Question.subject, func.count(Question.id)).group_by(Question.subject).all()
print("Questions per Subject:")
for subject, count in results:
    print(f"{subject}: {count}")

db.close()
