import React, { useState, useEffect, useRef } from 'react';
import TestSetup from './components/TestSetup';
import QuestionCard from './components/QuestionCard';
import Timer from './components/Timer';
import Result from './components/Result';
import './App.css';

function App() {
  const [gameState, setGameState] = useState('setup'); // setup, test, result
  const [testConfig, setTestConfig] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // { questionId: selectedOption }
  const [sessionId, setSessionId] = useState(null);

  // Timers (synced from backend)
  const [globalTimeLeft, setGlobalTimeLeft] = useState(0); // seconds
  const [questionTimeLeft, setQuestionTimeLeft] = useState(60); // seconds

  const [loading, setLoading] = useState(false);

  const timerRef = useRef(null);

  const startTest = async (config) => {
    setLoading(true);
    setTestConfig(config);
    try {
      // 1. Fetch Questions
      const qResponse = await fetch(`http://localhost:8000/api/questions?subject=${config.subject}&duration=${config.duration}`);
      const qData = await qResponse.json();
      setQuestions(qData);

      // 2. Start Session on Backend
      const sResponse = await fetch('http://localhost:8000/api/start-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration: config.duration, subject: config.subject })
      });
      const sData = await sResponse.json();
      setSessionId(sData.session_id);

      setGameState('test');
    } catch (error) {
      console.error("Failed to start test", error);
      alert("Failed to start test. Check backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (questionId, option) => {
    // Check Section B Limit (Max 10 per subsection)
    const currentQ = questions.find(q => q.id === questionId);

    if (currentQ && currentQ.section === 'B') {
      // Group by Subsection (e.g., Botany, Zoology, Physics, Chemistry)
      const sub = currentQ.subsection || currentQ.subject;

      // Count attempts in this specific Subsection's Section B
      const attemptsCount = questions.filter(q =>
        (q.subsection || q.subject) === sub &&
        q.section === 'B' &&
        answers[q.id]
      ).length;

      // If selecting a NEW option for an unattempted question, and already reached limit
      if (!answers[questionId] && attemptsCount >= 10) {
        alert(`You can only attempt 10 questions in ${sub} Section B. Please clear an existing answer to attempt this one.`);
        return;
      }
    }

    setAnswers(prev => ({
      ...prev,
      [questionId]: option
    }));
  };

  // Sync Status from Backend
  const syncStatus = async () => {
    if (!sessionId) return;
    try {
      const response = await fetch(`http://localhost:8000/api/test-status/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setGlobalTimeLeft(Math.floor(data.remaining_exam_seconds));
        setQuestionTimeLeft(Math.floor(data.remaining_question_seconds));

        if (!data.is_active || data.remaining_exam_seconds <= 0) {
          finishTest();
        }

        // Handle Question Auto-Move? 
        // If backend says question time is 0, we should move next?
        if (data.remaining_question_seconds <= 0) {
          handleNext(true); // IsAuto = true
        }
      }
    } catch (e) {
      console.error("Sync failed", e);
    }
  };

  // Timer Interval (Local tick + Sync)
  useEffect(() => {
    if (gameState !== 'test' || !sessionId) return;

    // Update local every second
    const interval = setInterval(() => {
      setGlobalTimeLeft((p) => Math.max(0, p - 1));
      setQuestionTimeLeft((p) => {
        if (p <= 1) {
          // Time up for question
          handleNext(true);
          return 60; // Reset visual immediately just in case
        }
        return p - 1;
      });
    }, 1000);

    // Sync with server every 5 seconds
    const syncInterval = setInterval(syncStatus, 5000);

    // Initial Sync
    syncStatus();

    return () => {
      clearInterval(interval);
      clearInterval(syncInterval);
    };
  }, [gameState, sessionId]);

  const updateBackendIndex = async (newIndex) => {
    if (!sessionId) return;
    try {
      await fetch(`http://localhost:8000/api/update-question-index?session_id=${sessionId}&new_index=${newIndex}`, { method: 'POST' });
      // Reset local question timer visual immediately to feel responsive
      setQuestionTimeLeft(60);
      syncStatus(); // Sync to get exact server time
    } catch (e) {
      console.error(e);
    }
  };

  // Keyboard Navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (gameState !== 'test' || questions.length === 0) return;

      const currentQId = questions[currentQuestionIndex].id;

      switch (e.key.toUpperCase()) {
        case 'A': handleOptionSelect(currentQId, 'A'); break;
        case 'B': handleOptionSelect(currentQId, 'B'); break;
        case 'C': handleOptionSelect(currentQId, 'C'); break;
        case 'D': handleOptionSelect(currentQId, 'D'); break;
        case 'ARROWLEFT': handlePrev(); break;
        case 'ARROWRIGHT': handleNext(); break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [gameState, questions, currentQuestionIndex]);

  const handleNext = (auto = false) => {
    if (currentQuestionIndex < questions.length - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);
      updateBackendIndex(nextIndex);
    } else {
      finishTest();
    }
  };

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      const prevIndex = currentQuestionIndex - 1;
      setCurrentQuestionIndex(prevIndex);
      updateBackendIndex(prevIndex);
    }
  };

  const finishTest = () => {
    setGameState('result');
    setSessionId(null);
  };

  const calculateResults = () => {
    let correct = 0;
    let wrong = 0;
    let unattempted = 0;
    let totalScore = 0;
    let subjectiveCount = 0;
    let validQuestionsCount = 0;
    const sectionBAttempts = {}; // Track Section B attempts per subsection

    questions.forEach(q => {
      // Check if subjective
      const isSubjective = !q.option_a && !q.option_b && !q.option_c && !q.option_d;

      if (isSubjective) {
        subjectiveCount++;
        return; // Skip subjective questions for scoring
      }

      validQuestionsCount++;

      const userAnswer = answers[q.id];
      const sub = q.subsection || q.subject;

      let isCounted = true;

      if (q.section === 'B') {
        if (!sectionBAttempts[sub]) sectionBAttempts[sub] = 0;

        if (userAnswer) {
          sectionBAttempts[sub]++;
          if (sectionBAttempts[sub] > 10) {
            isCounted = false; // Ignore > 10
          }
        }
      }

      if (isCounted) {
        if (!userAnswer) {
          unattempted++;
        } else if (userAnswer === q.correct_option) {
          correct++;
          totalScore += 4;
        } else {
          wrong++;
          totalScore -= 1;
        }
      }
    });

    const possibleMarks = 720; // Fixed for Full Mock? Or calc based on valid questions?
    // Start with 180 * 4 = 720. 
    // If individual subject, 40 * 4 = 160.

    // Better: Calculate valid max marks based on test config
    let maxQuestions = 0;
    if (questions.length === 200) maxQuestions = 180;
    else maxQuestions = validQuestionsCount; // Use valid count, excluding subjective

    return {
      correct,
      wrong,
      unattempted,
      totalScore,
      possibleMarks: maxQuestions * 4,
      totalQuestions: validQuestionsCount,
      subjectiveCount
    };
  };

  const formatTime = (seconds) => {
    if (seconds < 0) seconds = 0;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  if (loading) return <div className="loading">Generating Mock Paper...</div>;

  return (
    <div className="app-container">
      {gameState === 'setup' && <TestSetup onStart={startTest} />}

      {gameState === 'test' && questions.length > 0 && (
        <div className="test-interface">
          <div className="test-header">
            <div className="global-timer">Exam Time: {formatTime(globalTimeLeft)}</div>
            <div className="question-timer" style={{
              color: questionTimeLeft < 10 ? 'red' : 'inherit',
              fontWeight: 'bold',
              border: questionTimeLeft < 10 ? '2px solid red' : '1px solid #ccc',
              padding: '5px 10px',
              borderRadius: '5px'
            }}>
              Question Time: {formatTime(questionTimeLeft)}
            </div>
            <div className="progress">Question {currentQuestionIndex + 1} / {questions.length}</div>
          </div>

          <QuestionCard
            question={questions[currentQuestionIndex]}
            selectedOption={answers[questions[currentQuestionIndex].id]}
            onSelectOption={handleOptionSelect}
          />

          <div className="controls">
            <button
              className="nav-btn prev-btn"
              onClick={handlePrev}
              disabled={currentQuestionIndex === 0}
            >
              Previous
            </button>
            <button className="nav-btn next-btn" onClick={() => handleNext()}>
              {currentQuestionIndex === questions.length - 1 ? 'Finish & Submit' : 'Next'}
            </button>
          </div>
        </div>
      )}

      {gameState === 'result' && (
        <Result results={calculateResults()} onRestart={() => {
          setGameState('setup');
          setAnswers({});
          setCurrentQuestionIndex(0);
        }} />
      )}
    </div>
  );
}

export default App;
