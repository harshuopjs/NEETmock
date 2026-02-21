import React, { useEffect, useState } from 'react';

const Result = ({ results, onRestart }) => {
    if (!results) {
        return <div className="result-container error">Error: No results to display. Please restart the test.</div>;
    }

    const {
        totalScore = 0,
        correct = 0,
        wrong = 0,
        unattempted = 0,
        possibleMarks = 720,
        totalQuestions = 0
    } = results;

    const [rankData, setRankData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchRank = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/rank-estimate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ score: totalScore, total_marks: possibleMarks })
                });
                if (!response.ok) throw new Error("Failed to fetch rank");
                const data = await response.json();
                setRankData(data);
            } catch (e) {
                console.error("Rank fetch failed", e);
                setError("Could not retrieve rank estimate.");
            }
        };
        fetchRank();
    }, [totalScore, possibleMarks]);

    const percentage = Math.round((totalScore / possibleMarks) * 100);

    return (
        <div className="result-container">
            <h1>Test Analysis</h1>

            <div className="score-overview">
                <div className="score-card">
                    <h2>Your Score</h2>
                    <div className="score-value">{totalScore} <span className="total-marks">/ {possibleMarks}</span></div>
                    <div className={`score-badge ${percentage >= 50 ? 'pass' : 'fail'}`}>
                        {percentage}%
                    </div>
                </div>
            </div>

            {rankData ? (
                <div className="rank-card">
                    <h3>Predicted All India Rank</h3>
                    <div className="rank-range">{rankData.rank_range}</div>
                    <div className="rank-band">Performance: {rankData.performance_band}</div>
                    <p className="disclaimer">*Based on historical trends. Normalized to 720 scale: {rankData.normalized_score}</p>
                </div>
            ) : (
                <div className="rank-loading" style={{ padding: '20px', textAlign: 'center' }}>
                    {error ? <p style={{ color: 'red' }}>{error}</p> : <p>Calculating Rank...</p>}
                </div>
            )}

            <div className="stats-grid">
                <div className="stat-card total">
                    <h3>Total Questions</h3>
                    <p>{totalQuestions}</p>
                </div>
                <div className="stat-card correct">
                    <h3>Correct</h3>
                    <p>{correct}</p>
                </div>
                <div className="stat-card wrong">
                    <h3>Wrong</h3>
                    <p>{wrong}</p>
                </div>
                <div className="stat-card unattempted">
                    <h3>Skipped</h3>
                    <p>{unattempted}</p>
                </div>
            </div>

            <button onClick={onRestart} className="restart-btn">Take Another Mock Test</button>

            <div className="support-section" style={{
                marginTop: '40px',
                paddingTop: '30px',
                borderTop: '2px solid #e0e0e0',
                textAlign: 'center'
            }}>
                <h3 style={{ marginBottom: '16px', color: '#424242' }}>Need Help?</h3>
                <p style={{ fontSize: '1rem', marginBottom: '12px' }}>For any issues, contact us:</p>
                <p style={{ fontSize: '1rem', marginBottom: '8px' }}>
                    <strong>Email:</strong> <a href="mailto:founder@kridavista.in" style={{ color: '#1976d2' }}>founder@kridavista.in</a>
                </p>
                <p style={{ fontSize: '1rem' }}>
                    <strong>Business Number:</strong> 9971959892
                </p>
            </div>
        </div>
    );
};

export default Result;
