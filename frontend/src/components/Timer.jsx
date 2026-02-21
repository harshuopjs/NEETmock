import React, { useEffect, useState } from 'react';

const Timer = ({ duration, onTimeUp }) => {
    const [timeLeft, setTimeLeft] = useState(duration);

    useEffect(() => {
        if (timeLeft <= 0) {
            onTimeUp();
            return;
        }

        const timerId = setInterval(() => {
            setTimeLeft((prev) => prev - 1);
        }, 1000);

        return () => clearInterval(timerId);
    }, [timeLeft, onTimeUp]);

    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    };

    return (
        <div className={`timer ${timeLeft < 60 ? 'warning' : ''}`} style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            color: timeLeft < 60 ? '#d32f2f' : '#2e7d32',
            textAlign: 'center',
            marginBottom: '1rem',
            padding: '10px',
            border: timeLeft < 60 ? '2px solid #d32f2f' : '2px solid transparent',
            borderRadius: '8px',
            backgroundColor: timeLeft < 60 ? '#ffebee' : 'transparent',
            transition: 'all 0.3s ease'
        }}>
            Time Remaining: {formatTime(timeLeft)}
        </div>
    );
};

export default Timer;
