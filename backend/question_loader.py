import os
import re
from models import Question
from database import SessionLocal

PREVIOUS_YEAR_FOLDER = "previousyear"

def clean_text(text):
    if not text:
        return ""
    # Remove PDF artifacts if any remain
    text = text.replace("(cid:150)", "-").replace("(cid:215)", "x").replace("(cid:176)", "°")
    # Simplify whitespace
    text = " ".join(text.split())
    return text.strip()

def parse_block(block_text, year):
    """
    Parses a single question block.
    """
    lines = block_text.strip().split('\n')
    if not lines:
        return None
        
    # Extract ID (first line usually contains the rest of ID line if split by [ID:)
    # But since we split by [ID:, the ID might be at the start of the block text or passed in.
    # Actually, proper splitting usually removes the delimiter.
    # Let's handle the split carefully in the main loop.
    
    # We will use regex to find fields within the block
    # Structure:
    # ID: ... (Already handled by split)
    # Subject: ...
    # Question: ...
    # A. ...
    # B. ...
    # C. ...
    # D. ...
    # Answer: ...
    
    # We'll use dotall regex to capture multi-line content
    # Updated regex to handle both multiline and single-line (space separated) formats
    
    # Subject: from "Subject:" to "Question:"
    subject_match = re.search(r"Subject:\s*(.*?)(?=\s+Question:|\nQuestion:)", block_text, re.DOTALL | re.IGNORECASE)
    # If standard block, subject might not be explicitly tagged if we rely on file context, 
    # but our format requires it or we default. 
    # Actually, the user input has "Subject: ..." so this should work.
    # Fallback to general if not found, or maybe look for just "Question:" if subject is missing?
    # But let's stick to the prompt structure.
    subject = clean_text(subject_match.group(1)) if subject_match else "General"
    
    # Question: from "Question:" to "A."
    q_match = re.search(r"Question:\s*(.*?)(?=\s+A\.|\nA\.)", block_text, re.DOTALL | re.IGNORECASE)
    if not q_match:
        return None
    question_text = clean_text(q_match.group(1))
    
    # Options
    # Use lookahead for " LETTER." preceded by whitespace/newline
    a_match = re.search(r"A\.\s*(.*?)(?=\s+B\.|\nB\.)", block_text, re.DOTALL)
    b_match = re.search(r"B\.\s*(.*?)(?=\s+C\.|\nC\.)", block_text, re.DOTALL)
    c_match = re.search(r"C\.\s*(.*?)(?=\s+D\.|\nD\.)", block_text, re.DOTALL)
    
    # D ends at "Answer:" or end of string. 
    # matched group(1) will be stripped by clean_text later.
    d_match = re.search(r"D\.\s*(.*?)(?=\s*Answer:|\s*$)", block_text, re.DOTALL | re.IGNORECASE)
    
    if not (a_match and b_match and c_match and d_match):
        return None
        
    opt_a = clean_text(a_match.group(1))
    opt_b = clean_text(b_match.group(1))
    opt_c = clean_text(c_match.group(1))
    opt_d = clean_text(d_match.group(1))
    
    # Answer
    ans_match = re.search(r"Answer:\s*([A-D])", block_text, re.IGNORECASE)
    if not ans_match:
        return None
    answer = ans_match.group(1).upper()
    
    return {
        "subject": subject,
        "question_text": question_text,
        "option_a": opt_a,
        "option_b": opt_b,
        "option_c": opt_c,
        "option_d": opt_d,
        "correct_option": answer,
        "year": year
    }

def load_questions_from_text():
    if not os.path.exists(PREVIOUS_YEAR_FOLDER):
        print(f"Folder {PREVIOUS_YEAR_FOLDER} not found.")
        return

    # Ensure DB tables exist (since we might have deleted the DB file)
    from database import engine, Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # We do NOT clear existing questions anymore if we want to deduplicate against them.
    # But for clean state as per previous phase, maybe we should?
    # User said "Prevent duplicate insertion using question ID".
    # This implies we should check existence.
    
    total_added = 0
    total_skipped = 0
    total_duplicates = 0
    seen_ids = set()
    
    for filename in os.listdir(PREVIOUS_YEAR_FOLDER):
        if not filename.endswith(".txt"):
            continue
            
        file_path = os.path.join(PREVIOUS_YEAR_FOLDER, filename)
        
        # Extract year
        try:
            year = int(re.search(r'\d{4}', filename).group())
        except:
            year = 2026

        print(f"Processing {filename} (Year: {year})...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Split by [ID:
        raw_blocks = re.split(r"\[ID:", content)
        
        file_added = 0
        
        for block in raw_blocks:
            if not block.strip():
                continue
            
            if "]" not in block:
                continue
                
            closing_bracket_index = block.find("]")
            id_str = block[:closing_bracket_index].strip() 
            
            # Construct strict source_id unique key
            # user provided example: 2022-100
            # If id_str is "2022-100", use that.
            source_id = id_str
            
            # Check if exists in DB or in current session
            if source_id in seen_ids:
                print(f"Skipping duplicate ID (in-batch): {source_id}")
                total_duplicates += 1
                continue

            exists = db.query(Question).filter(Question.source_id == source_id).first()
            if exists:
                print(f"Skipping duplicate ID (in-db): {source_id}")
                total_duplicates += 1
                continue
                
            seen_ids.add(source_id)
            
            real_content = block[closing_bracket_index+1:]
            
            parsed_q = parse_block(real_content, year)
            
            if parsed_q:
                parsed_q['source_id'] = source_id
                q = Question(**parsed_q)
                db.add(q)
                file_added += 1
            else:
                total_skipped += 1
                print(f"Skipped invalid block with ID: {source_id}")
        
        print(f"File {filename}: Added {file_added} questions.")
        total_added += file_added
        
    db.commit()
    db.close()
    print(f"Done. Added: {total_added}. Skipped: {total_skipped}. Duplicates: {total_duplicates}")
    return {
        "total_added": total_added,
        "total_skipped": total_skipped,
        "total_duplicates": total_duplicates
    }

if __name__ == "__main__":
    load_questions_from_text()
