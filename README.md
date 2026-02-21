# NEET 2026 Mock Test Platform

A full-stack web application designed for students to take NEET practice tests. The platform features an automated PDF question parser, a timed exam interface, and a rank predictor.

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+**
- **Node.js & npm**

---

### 1. Setup Backend
The backend is built with FastAPI and SQLite.

```bash
cd backend
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```
The backend will be running at `http://localhost:8000`.

### 2. Setup Frontend
The frontend is built with React and Vite.

```bash
cd frontend
# Install dependencies
npm install

# Start the dev server
npm run dev
```
The frontend will be running at `http://localhost:5173`.

---

## 🛠 Usage Instructions

### Loading Questions
1. Place your NEET question PDFs or text files in the `backend/previousyear/` directory.
2. Trigger the parser via API:
   ```bash
   curl -X POST http://localhost:8000/api/parse-pdfs
   ```
   *Note: You can also use tools like Postman to trigger this endpoint.*

### Taking a Test
1. Select your desired subject and duration on the Home screen.
2. Click **Start Test** to enter the exam interface.
3. Use **Keyboard Shortcuts** for faster navigation:
   - `A`, `B`, `C`, `D`: Select options.
   - `Arrow Right`: Next question.
   - `Arrow Left`: Previous question.

---

## ✨ Key Features
- **Intelligent Parser**: Automatically extracts questions, options, and images from PDFs and formatted text blocks.
- **Timed Interface**: Global exam timer and per-question persistence.
- **NEET Pattern**: Supports Section A and Section B logic (only first 10 attempted in Section B are graded).
- **Rank Predictor**: Estimates your All India Rank based on your score and historical data.
- **Responsive Design**: Clean 2-column layout that works on desktop and mobile.
- **Subjective Support**: Auto-detects questions without options and provides a text input area.

## 📞 Support
For any issues or inquiries, please contact:
- **Email**: founder@kridavista.in
- **Phone**: 9971959892
