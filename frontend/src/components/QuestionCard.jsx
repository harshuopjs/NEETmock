import React from 'react';
import './QuestionCard.css';

const QuestionCard = ({ question, selectedOption, onSelectOption }) => {
    console.log("Rendering Question:", question);

    const { id, question_text, option_a, option_b, option_c, option_d, image_path, year, subject } = question;

    // Fallback for snake_case vs camelCase if needed
    const getOptionText = (key_snake, key_camel) => {
        const text = question[key_snake] || question[key_camel];
        if (!text) {
            console.warn(`Missing text for option ${key_snake}/${key_camel} in question ${id}`);
            return "Missing Option Text";
        }
        return text;
    };

    const options = [
        { label: 'A', text: getOptionText('option_a', 'optionA') },
        { label: 'B', text: getOptionText('option_b', 'optionB') },
        { label: 'C', text: getOptionText('option_c', 'optionC') },
        { label: 'D', text: getOptionText('option_d', 'optionD') },
    ];

    // Check if it's a subjective question (no options)
    const isSubjective = !question.option_a && !question.option_b && !question.option_c && !question.option_d;

    return (
        <div className="question-card">
            <div className="question-header">
                <span className="subject-tag">
                    {subject} {question.subsection && question.subsection !== subject ? `(${question.subsection})` : ""}
                </span>
                {question.section && (
                    <span className="section-tag" style={{ marginLeft: '10px', backgroundColor: '#e67e22', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem' }}>
                        Section {question.section}
                    </span>
                )}
            </div>

            <div className="question-body">
                <p className="question-text">{question_text}</p>
                {image_path && (
                    <div className="question-image">
                        <img src={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${image_path}`} alt="Question Diagram" />
                    </div>
                )}
            </div>

            {isSubjective ? (
                <div className="subjective-input-container">
                    <label className="subjective-label">Your Answer (Subjective):</label>
                    <textarea
                        className="subjective-textarea"
                        value={selectedOption || ''}
                        onChange={(e) => onSelectOption(id, e.target.value)}
                        placeholder="Type your answer here..."
                        rows={5}
                    />
                    <p className="subjective-note">Note: This question is for practice and will not be auto-graded.</p>
                </div>
            ) : (
                <div className="options-grid">
                    {options.map((opt) => (
                        <div
                            key={opt.label}
                            className={`option-item ${selectedOption === opt.label ? 'selected' : ''}`}
                            onClick={() => onSelectOption(id, opt.label)}
                        >
                            <span className="option-label">{opt.label}</span>
                            <span className="option-text">{opt.text}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default QuestionCard;
