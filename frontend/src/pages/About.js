import React from "react";
import "./About.css";

export default function About() {
  return (
    <div className="about-page">
      
      <section className="about-hero">
        <div className="hero-content">
          <h1 className="hero-title fade-in-up">Sinemanın Yeni Çağı</h1>
          <p className="hero-subtitle fade-in-up delay-1">
            Yapay zeka destekli kişisel film asistanınla tanış.
            <br />
            Senin zevkini öğrenen, hisseden ve anlayan bir deneyim.
          </p>
        </div>
        <div className="hero-glow"></div>
      </section>


      {/* FEATURES GRID */}
      <section className="features-section">
        <h2 className="section-header fade-in-up delay-3">Neden FilmRec?</h2>

        <div className="features-grid">
          <div className="feature-card glass-card fade-in-up delay-4">
            <div className="icon-box">🧠</div>
            <h3>Yapay Zeka Destekli</h3>
            <p>Siz izledikçe gelişen, zevkinizi öğrenen deep-learning algoritmaları.</p>
          </div>

          <div className="feature-card glass-card fade-in-up delay-5">
            <div className="icon-box">✨</div>
            <h3>Kişiselleştirilmiş</h3>
            <p>Sadece popüler olanı değil, sizin gerçekten seveceğiniz gizli cevherleri bulur.</p>
          </div>

          <div className="feature-card glass-card fade-in-up delay-6">
            <div className="icon-box">💬</div>
            <h3>Canlı Topluluk</h3>
            <p>Film tutkunlarıyla tartışın, listeler oluşturun ve deneyimlerinizi paylaşın.</p>
          </div>

          <div className="feature-card glass-card fade-in-up delay-7">
            <div className="icon-box">🔍</div>
            <h3>Detaylı Analiz</h3>
            <p>Oyuncular, yönetmenler ve detaylı vizyon bilgileri parmaklarınızın ucunda.</p>
          </div>
        </div>
      </section>

      {/* FOOTER QUOTE */}
      <section className="quote-section fade-in-up delay-8">
        <blockquote>
          "Sinema, hayatın sıkıcı kısımlarının kesilip atılmış halidir."
        </blockquote>
        <cite>- Alfred Hitchcock</cite>
      </section>
    </div>
  );
}
