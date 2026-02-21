import pdfplumber
import fitz  # PyMuPDF
import re
import os
from models import Question
from database import SessionLocal
import shutil

UPLOAD_FOLDER = "../previousyear"
IMAGE_FOLDER = "static/images"

# Regex Patterns
# Q_START: Matches "1.", "1)", "Q1."
Q_START_PATTERN = re.compile(r'^\s*(\d+)[\.\)]\s+') 
# OPT_START: Matches "(A)", "(a)", "A.", "A)", "(1)", "1." at start of line or after some space
OPT_START_PATTERN = re.compile(r'^\s*[\(\[]?([A-Da-d1-4])[\)\]\.]\s+')

def extract_images_from_page(doc, page_num, year, subject):
    """
    Extract images from a PDF page using PyMuPDF.
    Returns a list of image paths relative to static folder.
    """
    page = doc.load_page(page_num)
    image_list = page.get_images(full=True)
    saved_images = []

    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        
        image_filename = f"{year}_{subject}_p{page_num+1}_i{img_index}.{image_ext}"
        image_path = os.path.join(IMAGE_FOLDER, image_filename)
        
        with open(image_path, "wb") as f:
            f.write(image_bytes)
            
        saved_images.append(f"/static/images/{image_filename}")
        
    return saved_images

def clean_text(text):
    text = text.replace("(cid:150)", "-").replace("(cid:215)", "x").replace("(cid:176)", "°")
    return " ".join(text.split()).strip()

def parse_pdf(file_path):
    filename = os.path.basename(file_path)
    try:
        year = int(re.search(r'\d{4}', filename).group())
    except:
        year = 2026

    print(f"Parsing {filename} for year {year}...")
    
    db = SessionLocal()
    
    # State Machine Variables
    current_question = None
    questions_buffer = [] # Store fully parsed questions before adding to DB
    
    # Text Extraction
    full_lines = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_lines.extend(text.split('\n'))

    # Processing Loop
    # States: FIND_Q, IN_Q, IN_OPT_A, IN_OPT_B, IN_OPT_C, IN_OPT_D
    state = "FIND_Q"
    
    current_q_data = {
        "text": [],
        "options": {"A": [], "B": [], "C": [], "D": []},
        "year": year,
        "subject": "Unknown" # Will refine later
    }
    
    # Helper to finalize mapping options (A,B,C,D or 1,2,3,4)
    def map_option_label(label):
        label = label.upper()
        if label in ['1', 'A']: return 'A'
        if label in ['2', 'B']: return 'B'
        if label in ['3', 'C']: return 'C'
        if label in ['4', 'D']: return 'D'
        return None

    current_opt = None # 'A', 'B', 'C', 'D'

    # Determine Subject Ranges (Heuristic) based on typical NEET pattern
    def get_subject(q_idx):
        if q_idx <= 50: return "Physics"
        if q_idx <= 100: return "Chemistry"
        return "Biology"

    question_count = 0

    def save_current_question():
        nonlocal question_count
        # Validate
        q_text = clean_text(" ".join(current_q_data["text"]))
        opt_a = clean_text(" ".join(current_q_data["options"]["A"]))
        opt_b = clean_text(" ".join(current_q_data["options"]["B"]))
        opt_c = clean_text(" ".join(current_q_data["options"]["C"]))
        opt_d = clean_text(" ".join(current_q_data["options"]["D"]))

        if q_text and opt_a and opt_b and opt_c and opt_d:
            # Create object
            q = Question(
                subject=get_subject(question_count),
                question_text=q_text,
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_option='A', # Placeholder
                year=year
            )
            db.add(q)
            question_count += 1
            return True
        return False

    for line in full_lines:
        line = line.strip()
        if not line: continue
        
        # Check for new question start
        q_match = Q_START_PATTERN.match(line)
        if q_match:
            # If we were processing a question, save it
            if state != "FIND_Q":
                save_current_question()
            
            # Start new question
            state = "IN_Q"
            current_q_data = {
                "text": [Q_START_PATTERN.sub("", line)], # Remove "1."
                "options": {"A": [], "B": [], "C": [], "D": []},
            }
            current_opt = None
            continue

        # Check for Option start
        opt_match = OPT_START_PATTERN.match(line)
        if opt_match and state != "FIND_Q":
            label = map_option_label(opt_match.group(1))
            if label:
                state = f"IN_OPT_{label}"
                current_opt = label
                current_q_data["options"][label].append(OPT_START_PATTERN.sub("", line))
                continue
        
        # Append text to current state
        if state == "IN_Q":
            current_q_data["text"].append(line)
        elif state.startswith("IN_OPT_"):
            current_q_data["options"][current_opt].append(line)

    # Save last question
    if state != "FIND_Q":
        save_current_question()
        
    db.commit()
    db.close()
    print(f"Added {question_count} questions from {filename}")

def parse_all_pdfs():
    # Clear existing questions for clean start? (Optional, maybe just append)
    # For dev, let's clear to avoid duplicates if re-parsing same files
    # db = SessionLocal()
    # db.query(Question).delete()
    # db.commit()
    # db.close()

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created {UPLOAD_FOLDER}. Place PDFs here.")
        return

    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".pdf"):
            parse_pdf(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == "__main__":
    parse_all_pdfs()
