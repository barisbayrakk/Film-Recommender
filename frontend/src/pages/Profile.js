import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../api";
import { useNavigate } from "react-router-dom";
import "./Profile.css";

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [watchedMovies, setWatchedMovies] = useState([]);
  const [messages, setMessages] = useState([]);
  const [myReviews, setMyReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  const AVATAR_OPTIONS = [
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Felix",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Aneka",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Milo",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Lola",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Abby",
    "https://api.dicebear.com/7.x/avataaars/svg?seed=Scooter",
    "https://api.dicebear.com/7.x/avataaars/svg?seed=Midnight",
    "https://api.dicebear.com/7.x/bottts/svg?seed=Caleb",
  ];

  useEffect(() => {
    if (!user) return;
    loadData();
  }, [user]);

  async function loadData() {
    setLoading(true);
    try {
      
      const res = await fetch("http://localhost:8000/user/collections", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      if (res.ok) {
        const data = await res.json();
        setWatchedMovies(Array.isArray(data.watched) ? data.watched : []);
      }

    
      const msgs = await apiFetch("/contact/my-messages");
      setMessages(msgs);

      
      const revs = await apiFetch("/reviews/my-reviews");
      setMyReviews(Array.isArray(revs) ? revs : []);
    } catch (error) {
      console.error("Profile load error:", error);
    } finally {
      setLoading(false);
    }
  }

  const handleAvatarSelect = async (url) => {
    try {
      await apiFetch("/auth/avatar", {
        method: "PUT",
        body: { avatar_url: url }
      });
      alert("Profil fotoğrafı güncellendi!");
      window.location.reload();
    } catch (err) {
      alert("Hata: " + (err.detail || err.message));
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("Hesabınızı silmek istediğinize emin misiniz? Bu işlem geri alınamaz!")) return;
    try {
      await apiFetch("/auth/me", { method: "DELETE" });
      logout();
      navigate("/");
    } catch (err) {
      alert("Hata: " + err.message);
    }
  };

  if (!user) return <div className="profile-loading">Lütfen giriş yapın.</div>;
  if (loading) return <div className="profile-loading">Yükleniyor...</div>;

  return (
    <div className="profile-page">

      
      <div className="profile-header-card glass-panel fade-in-up">
        <div className="profile-cover"></div>
        <div className="profile-info-content">
          <div className="avatar-section">
            <img
              src={user.avatar_url || "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"}
              alt="Avatar"
              className="main-avatar"
            />
            <div className="avatar-selector">
              {AVATAR_OPTIONS.map((url, i) => (
                <img
                  key={i}
                  src={url}
                  onClick={() => handleAvatarSelect(url)}
                  className={`avatar-option ${user.avatar_url === url ? "active" : ""}`}
                  alt="avatar-opt"
                />
              ))}
            </div>
          </div>

          <div className="user-text">
            <h1 className="user-name">{user.name || user.username}</h1>
            <p className="user-email">{user.email}</p>
            <div className="user-badges">
              <span className="badge member-badge">Üye</span>
              {user.is_verified && <span className="badge verified-badge">Doğrulanmış</span>}
              <span className="badge stats-badge">{watchedMovies.length} Film İzledi</span>
            </div>
            <button onClick={handleDeleteAccount} className="delete-account-btn">Hesabı Sil</button>
          </div>
        </div>
      </div>

      
      <section className="profile-section fade-in-up delay-1">
        <h2 className="section-title">Yorumlarım</h2>
        {myReviews.length === 0 ? (
          <div className="empty-message-box">Henüz hiç yorum yapmadın.</div>
        ) : (
          <div className="messages-list">
            {myReviews.map(r => (
              <div key={r.id} className="message-card glass-panel" onClick={() => navigate(`/movies/${r.movie.id}`)} style={{ cursor: 'pointer' }}>
                <div className="message-header">
                  <span className="msg-from">{r.movie.title}</span>
                  <span className="msg-date">{new Date(r.created_at).toLocaleDateString()}</span>
                </div>
                <p className="msg-body">"{r.text}"</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="profile-section fade-in-up delay-1">
        <h2 className="section-title">İletişim Mesajlarım</h2>

        {messages.length === 0 ? (
          <div className="empty-message-box">Henüz gönderdiğin bir mesaj yok.</div>
        ) : (
          <div className="messages-list">
            {messages.map(m => (
              <div key={m.id} className="message-card glass-panel">
                <div className="message-header">
                  <span className="msg-date">{new Date(m.created_at).toLocaleDateString()}</span>
                  <span className={`msg-status ${m.reply ? "answered" : "pending"}`}>
                    {m.reply ? "Cevaplandı" : "Cevap Bekliyor"}
                  </span>
                </div>
                <p className="msg-body">"{m.message}"</p>
                {m.reply && (
                  <div className="admin-reply-box">
                    <div className="reply-label">Yönetici Cevabı:</div>
                    <div className="reply-text">{m.reply}</div>
                    <div className="reply-date">{new Date(m.replied_at).toLocaleDateString()}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      
      <section className="profile-section fade-in-up delay-2">
        <h2 className="section-title">İzleme Geçmişi</h2>
        {watchedMovies.length === 0 ? (
          <div className="empty-history">
            <h3>Henüz bir film izlemedin.</h3>
            <p>Filmleri izledim olarak işaretleyerek buraya ekleyebilirsin.</p>
          </div>
        ) : (
          <div className="history-grid">
            {watchedMovies.map((m) => (
              <div
                className="history-card"
                key={m.id}
                onClick={() => navigate(`/movies/${m.movie_id || m.id}`)}
              >
                <div className="history-poster-wrapper">
                  <img
                    src={`https://image.tmdb.org/t/p/w300${m.poster_path}`}
                    alt={m.title}
                    loading="lazy"
                  />
                  <div className="history-overlay">
                    <span>Detay</span>
                  </div>
                </div>
                <p className="history-title">{m.title}</p>
                {m.vote_average > 0 && <span className="history-rating">★ {m.vote_average.toFixed(1)}</span>}
              </div>
            ))}
          </div>
        )}
      </section>

    </div>
  );
}
