import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

export default function MicroLesson({ lessonData, onStartQuiz }) {
  const mermaidRef = useRef(null);

  useEffect(() => {
    if (lessonData && lessonData.mermaidDiagram && mermaidRef.current) {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark', // Changed back to dark to match Slate theme
        securityLevel: 'loose',
      });

      setTimeout(() => {
        try {
          mermaidRef.current.removeAttribute('data-processed');
          mermaid.run({ nodes: [mermaidRef.current] });
        } catch (error) {
          console.error("Mermaid Render Error:", error);
        }
      }, 100);
    }
  }, [lessonData]);

  return (
    <div className="fadeIn MicroLesson">
      <div className="cg-card" style={{ padding: '0', overflow: 'hidden' }}>
        
        <div style={{ backgroundColor: '#0F172A', padding: '20px 30px', borderBottom: '1px solid #334155' }}>
          <h3 className="cg-title-content" style={{ color: '#3B82F6', margin: 0, fontSize: '1.3rem' }}>
            {lessonData.title || "Understanding Your Logic Error"}
          </h3>
        </div>

        <div style={{ padding: '40px 30px', display: 'flex', flexDirection: 'column', gap: '30px' }}>
          
          <div>
            <h4 className="cg-title-content cg-text-danger">The Core Issue</h4>
            <p className="cg-text-muted">{lessonData.issue}</p>
          </div>

          <div>
            <h4 className="cg-title-content" style={{ color: '#A78BFA' }}>Concept Breakdown</h4>
            <p className="cg-text-muted">{lessonData.explanation}</p>
          </div>

          {/* DYNAMIC AI GENERATED DIAGRAM */}
          {lessonData.mermaidDiagram && (
            <div>
              <h4 className="cg-title-content" style={{ color: '#34D399' }}>Visual Concept Model</h4>
              <div 
                className="mermaid" 
                ref={mermaidRef} 
                style={{ 
                  backgroundColor: '#0F172A', 
                  padding: '20px', 
                  borderRadius: '8px', 
                  border: '1px solid #334155',
                  textAlign: 'center',
                  marginTop: '10px',
                  overflowX: 'auto'
                }}
              >
                {lessonData.mermaidDiagram.replace(/\\n/g, '\n')}
              </div>
            </div>
          )}

          {lessonData.exampleCode && (
            <div>
              <h4 className="cg-title-content">Implementation Guide</h4>
              <div className="cg-code-block">
                {lessonData.exampleCode}
              </div>
            </div>
          )}

          {(lessonData.videoUrl || lessonData.referenceLink) && (
            <div style={{ backgroundColor: '#0F172A', padding: '20px', borderRadius: '8px', border: '1px solid #334155' }}>
              <h4 className="cg-title-content" style={{ color: '#F8FAFC', marginBottom: '15px' }}>📚 Recommended Resources</h4>
              <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
                {lessonData.videoUrl && (
                  <a href={lessonData.videoUrl} target="_blank" rel="noopener noreferrer" className="cg-resource-link">
                    ▶️ Watch Video Tutorial
                  </a>
                )}
                {lessonData.referenceLink && (
                  <a href={lessonData.referenceLink} target="_blank" rel="noopener noreferrer" className="cg-resource-link">
                    🌐 Read Documentation
                  </a>
                )}
              </div>
            </div>
          )}

          <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', padding: '20px', borderRadius: '8px', borderLeft: '4px solid #F59E0B' }}>
            <h4 className="cg-title-content cg-text-warning" style={{ fontSize: '1rem', color: '#FBBF24' }}>Code Guru Pro Tip</h4>
            <p className="cg-text-muted" style={{ margin: 0, fontStyle: 'italic', fontSize: '0.95rem', color: '#FDE68A' }}>{lessonData.hint}</p>
          </div>
          
        </div>
      </div>

      <div style={{ marginTop: '30px', textAlign: 'right' }}>
        <button onClick={onStartQuiz} className="cg-btn cg-btn-primary">
          Verify Knowledge →
        </button>
      </div>
    </div>
  );
}