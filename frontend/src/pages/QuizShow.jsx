// frontend/src/pages/QuizShow.jsx
import React, { useState } from "react";
import { quizQuestions } from "../data/quizQuestions";
import "./QuizShow.css";

export default function QuizShow() {
    const [category, setCategory] = useState(null); 
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [showScore, setShowScore] = useState(false);
    const [selectedOption, setSelectedOption] = useState(null);

    const startGame = (selectedCategory) => {
        const allQuestions = [...quizQuestions[selectedCategory]];
        const shuffled = allQuestions.sort(() => 0.5 - Math.random());
        const selected5 = shuffled.slice(0, 5);

        setQuestions(selected5);
        setCategory(selectedCategory);
        setCurrentQuestionIndex(0);
        setScore(0);
        setShowScore(false);
        setSelectedOption(null);
    };

    const handleOptionClick = (option) => {
        if (selectedOption) return;

        const currentQ = questions[currentQuestionIndex];
        const correct = option === currentQ.correctAns;

        setSelectedOption(option);

        if (correct) {
            setScore(score + 1);
        }

        setTimeout(() => {
            const nextQuestion = currentQuestionIndex + 1;
            if (nextQuestion < questions.length) {
                setCurrentQuestionIndex(nextQuestion);
                setSelectedOption(null);
            } else {
                setShowScore(true);
            }
        }, 1000);
    };

    const resetGame = () => {
        setCategory(null);
        setQuestions([]);
        setScore(0);
        setShowScore(false);
    };

    // 1. Kategori Seçim Ekranı
    if (!category) {
        return (
            <div className="quiz-page">
                <div className="quiz-bg-overlay"></div>
                <div className="quiz-container neon-border">
                    <h1>
                        <span style={{ color: '#ff9900' }}>QuizShow</span> 🧠
                    </h1>
                    <p style={{ fontWeight: 'bold', color: '#fff' }}>Haftalık bilgini test etmeye hazır mısın?</p>

                    <div className="category-cards">
                        {/* YERLİ */}
                        <div className="category-card local" onClick={() => startGame("local")}>
                            <div className="card-title">YERLİ FİLMLER</div>
                            <div className="card-icons">
                                🎭 🎥
                            </div>
                        </div>

                        {/* YABANCI */}
                        <div className="category-card foreign" onClick={() => startGame("foreign")}>
                            <div className="card-title">YABANCI FİLMLER</div>
                            <div className="card-icons">
                                🍿 🎬 🌍
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // 2. Sonuç Ekranı
    if (showScore) {
        return (
            <div className="quiz-page">
                <div className="quiz-bg-overlay"></div>
                <div className="quiz-container">
                    <h2>🎉 Oyun Bitti! 🎉</h2>
                    <div className="score-board">
                        <p>Toplam Skorun</p>
                        <div className="score-circle">
                            {score} / {questions.length}
                        </div>
                    </div>

                    <p className="score-message">
                        {score === 5 ? "Mükemmel! Tam bir film gurususun! 🏆" :
                            score >= 3 ? "Güzel iş! Biraz daha izlemelisin. 🍿" :
                                "Daha çok film izlemen lazım... 🎬"}
                    </p>

                    <button className="btn-restart" onClick={resetGame}>
                        🔄 Tekrar Oyna
                    </button>
                </div>
            </div>
        );
    }

    // 3. Soru Ekranı
    const currentQ = questions[currentQuestionIndex];

    return (
        <div className="quiz-page">
            <div className="quiz-bg-overlay"></div>
            <div className="quiz-container">
                <div className="quiz-header">
                    <span className="q-count">Soru {currentQuestionIndex + 1} / {questions.length}</span>
                    <button className="btn-exit" onClick={resetGame}>Çıkış</button>
                </div>

                <div className="question-card">
                    <h3>{currentQ.text}</h3>

                    <div className="options-grid">
                        {currentQ.options.map((option, index) => {
                            let btnClass = "btn-option";
                            if (selectedOption) {
                                if (option === currentQ.correctAns) btnClass += " correct";
                                else if (option === selectedOption) btnClass += " wrong";
                            }

                            return (
                                <button
                                    key={index}
                                    className={btnClass}
                                    onClick={() => handleOptionClick(option)}
                                    disabled={selectedOption !== null}
                                >
                                    {option}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
