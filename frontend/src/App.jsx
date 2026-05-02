import { useState } from 'react';
import axios from 'axios';
import TriggerCard from './components/TriggerCard';
import MicroLesson from './components/MicroLesson';
import ValidationQuiz from './components/ValidationQuiz';
import StudentDashboard from './components/StudentDashboard';
import './App.css';

function App() {
  const [currentPhase, setCurrentPhase] = useState("trigger");
  const [lessonData, setLessonData] = useState(null);
  const [loading, setLoading] = useState(false);

  const studentId = "user_0bcc693e70f0487da5a56117f923c73e";
  const errorType = "OFF_BY_ONE_LOOP_BOUNDARY";
  const conceptTag = "loop_boundaries";
  const codeSnippet = "for (int i = 0; i <= arr.length; i++) { ... }";

  const generatePersonalizedLesson = () => {
    setLoading(true);
    
    const errorPayload = { 
      student_id: studentId, 
      error_type: errorType, 
      error_count: 3, 
      concept_tag: conceptTag,
      code_snippet: codeSnippet 
    };

    axios.post('http://127.0.0.1:8000/api/struggle/detect', errorPayload)
      .then(response => {
        if (response.data.lesson_content) {
          setLessonData({
            title: response.data.lesson_title || "Mastering the Concept",
            issue: response.data.lesson_content.issue,
            explanation: response.data.lesson_content.explanation,
            hint: response.data.lesson_content.hint,
            exampleCode: response.data.lesson_content.exampleCode,
            videoUrl: response.data.lesson_content.videoUrl, 
            referenceLink: response.data.lesson_content.referenceLink,
            // 👇 මේක තමයි කලින් අඩු වෙලා තිබ්බේ
            mermaidDiagram: response.data.lesson_content.mermaidDiagram
          });
          setCurrentPhase("lesson");
        }
        setLoading(false);
      })
      .catch(error => {
        console.error("API Error:", error);
        setLoading(false);
      });
  };

  const goHome = () => {
    setCurrentPhase("trigger");
    setLessonData(null);
  };

  return (
    <div className="App-container">
      <header className="cg-header cg-flex-between">
        <div>
          <h1 className="cg-title-main">Code Guru Study Guider</h1>
          <p className="cg-subtitle">ID: <span style={{fontFamily: 'Fira Code', color: '#0066FF'}}>{studentId.substring(0, 8)}</span></p>
        </div>
        
        <div>
          {currentPhase !== "dashboard" && (
            <button onClick={() => setCurrentPhase("dashboard")} className="cg-btn cg-btn-outline">
              <span style={{marginRight: '8px'}}>📊</span> Analytics
            </button>
          )}
        </div>
      </header>
      
      <div className="cg-content-wrapper">
        {currentPhase === "trigger" && (
          <TriggerCard errorType={errorType} loading={loading} onGenerateLesson={generatePersonalizedLesson} />
        )}
        {currentPhase === "lesson" && lessonData && (
          <MicroLesson lessonData={lessonData} onStartQuiz={() => setCurrentPhase("quiz")} />
        )}
        {currentPhase === "quiz" && (
          <ValidationQuiz studentId={studentId} errorType={errorType} codeSnippet={codeSnippet} />
        )}
        {currentPhase === "dashboard" && (
          <StudentDashboard studentId={studentId} onBack={goHome} />
        )}
      </div>
    </div>
  );
}

export default App;