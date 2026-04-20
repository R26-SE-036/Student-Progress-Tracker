import React from 'react';

export default function TriggerCard({ errorType, loading, onGenerateLesson }) {
  return (
    <div className="cg-card TriggerCard fadeIn" style={{ textAlign: 'center', padding: '50px 30px' }}>
      <div style={{ fontSize: '3rem', marginBottom: '15px' }}>⚠️</div>
      <h2 className="cg-title-section cg-text-danger">Struggle Pattern Detected</h2>
      <p className="cg-text-muted" style={{ fontSize: '1.05rem', marginBottom: '35px', maxWidth: '600px', margin: '0 auto 35px' }}>
        We noticed repeated logical issues regarding <strong style={{color: '#EDEDED'}}>{errorType}</strong> in your active coding session. 
        Let's take a quick micro-lesson to master this concept.
      </p>
      <button onClick={onGenerateLesson} disabled={loading} className="cg-btn cg-btn-success">
        {loading ? (
          <><span className="spinner">⌛</span> Analyzing Code Context...</>
        ) : (
          "Start Interactive Lesson"
        )}
      </button>
    </div>
  );
}