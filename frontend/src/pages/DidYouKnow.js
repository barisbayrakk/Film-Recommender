
import React, { useState } from 'react';
import './DidYouKnow.css'; // We will create this CSS

export default function DidYouKnow() {
    const [fact, setFact] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchFact = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/trivia/random');
            if (res.ok) {
                const data = await res.json();
                setFact(data.fact);
            } else {
                setFact("Bir hata oluştu, lütfen tekrar deneyin.");
            }
        } catch (err) {
            console.error(err);
            setFact("Sunucuya bağlanılamadı.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="did-you-know-container">
            <div className="content-wrapper">
                <div className="top-section">
                    <h1 className="title">Keşif Odası 🧭</h1>
                    <p className="subtitle">
                        Sinema dünyasının en ilginç, şaşırtıcı ve az bilinen gerçeklerini keşfetmeye hazır mısın?
                    </p>
                </div>

                <div className="bottom-section">
                    <div className="card-display">
                        {fact ? (
                            <div className="fact-card enter-animation" key={fact}>
                                <p className="fact-text">“{fact}”</p>
                            </div>
                        ) : (
                            <div className="placeholder-card">
                                <p>Öğrenmek için butona tıkla!</p>
                            </div>
                        )}
                    </div>

                    <button className="learn-btn" onClick={fetchFact} disabled={loading}>
                        {loading ? 'Yükleniyor...' : 'Yeni Bir Bilgi Öğren! 🎲'}
                    </button>
                </div>
            </div>
        </div>
    );
}
