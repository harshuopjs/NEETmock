import React, { useState } from 'react';
import './TestSetup.css'; // Import new CSS file

const TestSetup = ({ onStart }) => {
    // Controlled components with empty initial state
    const [duration, setDuration] = useState("");
    const [subject, setSubject] = useState("");

    // Greeting Logic
    const hour = new Date().getHours();
    let greeting = 'Good Morning';
    if (hour >= 12 && hour < 17) greeting = 'Good Afternoon';
    else if (hour >= 17 && hour < 21) greeting = 'Good Evening';
    else if (hour >= 21 || hour < 5) greeting = 'Good Night';

    // Date Logic
    const today = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const todayDate = today.toLocaleDateString('en-US', options);

    // NEET Countdown Logic (3 May 2026)
    const neetDate = new Date('2026-05-03T00:00:00');
    const diffTime = neetDate - today;
    const daysLeft = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    const handleSubmit = (e) => {
        e.preventDefault();
        if (duration && subject) {
            onStart({ duration: Number(duration), subject });
        }
    };

    return (
        <div className="setup-container-wrapper">
            <div className="setup-card">
                <div className="setup-header">
                    <h1>ESHA's NEET 2026</h1>
                    <p className="subtitle">Mock Test Portal</p>
                </div>

                <div className="greeting-box">
                    <h2>{greeting}, welcome back!</h2>
                    <p className="date-text">{todayDate}</p>
                    <div className="countdown-text">
                        {daysLeft > 0 ? `${daysLeft} days left for NEET 2026` : "NEET 2026 is over."}
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="setup-form">
                    <div className="form-group">
                        <label>Exam Duration</label>
                        <select
                            value={duration}
                            onChange={(e) => setDuration(e.target.value)}
                            className="styled-select"
                        >
                            <option value="" disabled>Select duration</option>
                            <option value="12000">Full Mock (3h 20m)</option>
                            <option value="10800">3 Hours</option>
                            <option value="7200">2 Hours</option>
                            <option value="3600">1 Hour</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Subject Focus</label>
                        <select
                            value={subject}
                            onChange={(e) => {
                                const val = e.target.value;
                                setSubject(val);
                                // Auto-select fit duration if full neet? User asked for validation instead.
                                // Let's keep it simple: User selects both.
                                if (val === 'Full NEET' && !duration) setDuration("12000");
                            }}
                            className="styled-select"
                        >
                            <option value="" disabled>Select subject</option>
                            <option value="Full NEET">Full NEET (Physics + Chemistry + Biology)</option>
                            <option value="Physics">Physics</option>
                            <option value="Chemistry">Chemistry</option>
                            <option value="Biology">Biology</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        className="start-btn-modern"
                        disabled={!duration || !subject}
                    >
                        Start Test
                    </button>
                </form>
            </div>
        </div>
    );
};

export default TestSetup;
