import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';
import { apiFetch } from "../api";
import ActiveUsers from "../components/admin/ActiveUsers";
import "./AdminDashboard.css";

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [messages, setMessages] = useState([]); 

  const [movies, setMovies] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");


  useEffect(() => {
    if (activeTab === "dashboard") {
      loadStats();
      loadAnalytics();
    }
    if (activeTab === "users") loadUsers();
    if (activeTab === "movies") loadMovies();
    if (activeTab === "messages") loadMessages(); 
  }, [activeTab]);

  

  const filteredMovies = movies.filter(m =>
    m.title.toLowerCase().includes(searchTerm.toLowerCase())
  );


  async function loadStats() {
    try {
      const data = await apiFetch("/admin/dashboard");
      setStats(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function loadAnalytics() {
    try {
      const data = await apiFetch("/admin/analytics");
      setAnalytics(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function loadUsers() {
    try {
      const data = await apiFetch("/admin/users");
      setUsers(data);
    } catch (e) {
      console.error(e);
    }
  }

  
  async function loadMessages() {
    try {
      const data = await apiFetch("/contact/messages");
      setMessages(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleReply(id, oldReply) {
    const replyText = prompt("Cevabınızı yazın:", oldReply || "");
    if (replyText === null) return; // Cancelled

    try {
      await apiFetch(`/contact/${id}/reply`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: { reply: replyText } // Fixed: Pass object directly
      });
      alert("Cevap gönderildi!");
      loadMessages(); // Refresh list
    } catch (err) {
      const msg = err.detail || err.message || JSON.stringify(err);
      alert("Hata: " + (typeof msg === 'object' ? JSON.stringify(msg, null, 2) : msg));
    }
  }

  // Actions
  async function handleAddMovie(e) {
    e.preventDefault();
    const form = e.target;
    // Check if form elements exist/are not null
    const title = form.elements.title.value;
    const overview = form.elements.overview.value;
    const release_date = form.elements.release_date.value;
    const poster_url = form.elements.poster_url.value;
    const genres = form.elements.genres.value;

    const body = { title, overview, release_date, poster_url, genres };

    try {
      await apiFetch("/admin/movies", {
        method: "POST",
        body: body 
      });
      alert("Film başarıyla eklendi!");
      form.reset();
      loadStats();
    } catch (err) {
      console.error(err);
      let msg = err.detail || err.message || JSON.stringify(err);
      if (typeof msg === 'object') {
        msg = JSON.stringify(msg, null, 2);
      }
      alert("Hata detayları:\n" + msg);
    }
  }

  async function handleDeleteUser(id) {
    if (!window.confirm("Kullanıcıyı silmek istediğinize emin misiniz?")) return;
    try {
      await apiFetch(`/admin/users/${id}`, { method: "DELETE" });
      setUsers(users.filter(u => u.id !== id));
      alert("Kullanıcı silindi.");
    } catch (err) {
      alert("Hata: " + err.message);
    }
  }

  async function toggleAdmin(id, currentStatus) {
    const newStatus = currentStatus === 1 ? 0 : 1;
    try {
      await apiFetch(`/admin/users/${id}/role`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: { is_admin: newStatus } 
      });
      setUsers(users.map(u => u.id === id ? { ...u, is_admin: newStatus } : u));
    } catch (err) {
      alert("Hata: " + (err.detail || err.message));
    }
  }

  async function loadMovies() {
    try {
      const data = await apiFetch("/movies/all");
      setMovies(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleDeleteMovie(id) {
    if (!window.confirm("Filmi silmek istediğinize emin misiniz?")) return;
    try {
      await apiFetch(`/admin/movies/${id}`, { method: "DELETE" });
      setMovies(movies.filter(m => m.id !== id));
      alert("Film silindi.");
    } catch (err) {
      alert("Hata: " + err.message);
    }
  }

  return (
    <div className="admin-container">
      <div className="admin-sidebar">
        <h2>Admin Panel</h2>
        <ul>
          <li className={activeTab === "dashboard" ? "active" : ""} onClick={() => setActiveTab("dashboard")}>Dashboard</li>
          <li className={activeTab === "users" ? "active" : ""} onClick={() => setActiveTab("users")}>Kullanıcılar</li>
          <li className={activeTab === "movies" ? "active" : ""} onClick={() => setActiveTab("movies")}>Film Yönetimi</li>
          <li className={activeTab === "messages" ? "active" : ""} onClick={() => setActiveTab("messages")}>Mesajlar</li>
          <li className={activeTab === "settings" ? "active" : ""} onClick={() => setActiveTab("settings")}>Ayarlar</li>
        </ul>
      </div>

      <div className="admin-content">
        
        {activeTab === "dashboard" && stats && (
          <div>
            <div className="dashboard-grid">
              <div className="stat-card">
                <h3>Toplam Kullanıcı</h3>
                <p>{stats.total_users}</p>
              </div>
              <div className="stat-card">
                <h3>Toplam Film</h3>
                <p>{stats.total_movies}</p>
              </div>
              <div className="stat-card">
                <h3>Toplam Yorum</h3>
                <p>{stats.total_reviews}</p>
              </div>
              <div className="stat-card">
                <h3>Sistem Durumu</h3>
                {analytics?.system_health ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
                    <span style={{
                      display: 'block',
                      width: '12px', height: '12px',
                      borderRadius: '50%',
                      backgroundColor: analytics.system_health.color,
                      boxShadow: `0 0 10px ${analytics.system_health.color}`
                    }}></span>
                    <span style={{ fontSize: '1.2em', fontWeight: 'bold' }}>{analytics.system_health.latency} ms</span>
                  </div>
                ) : (
                  <p style={{ fontSize: '0.9em', color: '#888' }}>Ölçülüyor...</p>
                )}
              </div>
            </div>

           
            {analytics && (
              <div className="charts-section">
               

                
                <div className="chart-box">
                  <h3>Haftalık Aktivite</h3>
                  <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                      <LineChart data={analytics.weekly_activity}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis dataKey="day" stroke="#888" />
                        <YAxis stroke="#888" allowDecimals={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#222', border: 'none', borderRadius: '8px' }} />
                        <Legend />
                        <Line type="monotone" dataKey="new_users" name="Yeni Üye" stroke="#e50914" strokeWidth={3} dot={{ r: 4 }} />
                        <Line type="monotone" dataKey="new_reviews" name="Yeni Yorum" stroke="#ffa000" strokeWidth={3} dot={{ r: 4 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                
                <div className="chart-box">
                  <h3>Popüler Türler</h3>
                  <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                      <BarChart data={analytics.genre_distribution} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis type="number" stroke="#888" allowDecimals={false} />
                        <YAxis dataKey="name" type="category" stroke="#888" width={150} tick={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ backgroundColor: '#222', border: 'none', borderRadius: '8px' }} />
                        <Bar dataKey="value" name="Film Sayısı" fill="#007bff" radius={[0, 4, 4, 0]} barSize={20} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}


            
            {analytics?.top_commented_movies && (
              <div className="section-block" style={{ marginTop: '20px' }}>
                <h3>💬 En Çok Yorum Alan Filmler</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Film Başlığı</th>
                      <th>Yorum Sayısı</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.top_commented_movies.map(m => (
                      <tr key={m.id}>
                        <td>{m.id}</td>
                        <td>
                          <Link to={`/movies/${m.id}`} style={{ color: '#fff', textDecoration: 'none' }} onMouseOver={(e) => e.target.style.textDecoration = 'underline'} onMouseOut={(e) => e.target.style.textDecoration = 'none'}>
                            {m.title}
                          </Link>
                        </td>
                        <td>
                          <span style={{ color: '#00e5ff', fontWeight: 'bold' }}>{m.review_count} Yorum</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

           
            {analytics?.top_liked_movies && (
              <div className="section-block" style={{ marginTop: '20px' }}>
                <h3>❤️ En Çok Beğenilen Filmler</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Film Başlığı</th>
                      <th>Beğeni Sayısı</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.top_liked_movies.map(m => (
                      <tr key={m.id}>
                        <td>{m.id}</td>
                        <td>
                          <Link to={`/movies/${m.id}`} style={{ color: '#fff', textDecoration: 'none' }} onMouseOver={(e) => e.target.style.textDecoration = 'underline'} onMouseOut={(e) => e.target.style.textDecoration = 'none'}>
                            {m.title}
                          </Link>
                        </td>
                        <td>
                          <span style={{ color: '#ff4081', fontWeight: 'bold' }}>{m.like_count} Beğeni</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

           
            {analytics?.top_rated_movies && (
              <div className="section-block" style={{ marginTop: '20px' }}>
                <h3>⭐ En Yüksek Puanlı Filmler</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Film Başlığı</th>
                      <th>Ortalama Puan</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.top_rated_movies.map(m => (
                      <tr key={m.id}>
                        <td>{m.id}</td>
                        <td>
                          <Link to={`/movies/${m.id}`} style={{ color: '#fff', textDecoration: 'none' }} onMouseOver={(e) => e.target.style.textDecoration = 'underline'} onMouseOut={(e) => e.target.style.textDecoration = 'none'}>
                            {m.title}
                          </Link>
                        </td>
                        <td>
                          <span style={{ color: '#ffd700', fontWeight: 'bold' }}>★ {m.avg_score}</span>
                          <span style={{ fontSize: '0.8em', color: '#888', marginLeft: '8px' }}>({m.count} oy)</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            
            {analytics?.active_users && <ActiveUsers users={analytics.active_users} />}
          </div>
        )}

        
        {activeTab === "users" && (
          <div>
            <h2>Kullanıcı Yönetimi</h2>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Kullanıcı Adı</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.username}</td>
                    <td>{u.email}</td>
                    <td>
                      <span className={u.is_admin === 1 ? "badge admin" : "badge user"}>
                        {u.is_admin === 1 ? "Admin" : "User"}
                      </span>
                    </td>
                    <td>
                      <button className="btn-small" onClick={() => toggleAdmin(u.id, u.is_admin)}>
                        {u.is_admin === 1 ? "User Yap" : "Admin Yap"}
                      </button>
                      <button className="btn-small delete" onClick={() => handleDeleteUser(u.id)}>Sil</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        
        {activeTab === "movies" && (
          <div>
            <h2>Film Ekle</h2>
            <form className="admin-form" onSubmit={handleAddMovie}>
              <div className="form-group">
                <label>Film Adı</label>
                <input name="title" required placeholder="Örn: Inception" />
              </div>
              <div className="form-group">
                <label>Özet</label>
                <textarea name="overview" rows="4" placeholder="Film özeti..." />
              </div>
              <div className="row">
                <div className="form-group">
                  <label>Yıl</label>
                  <input name="release_date" placeholder="2010-07-16" />
                </div>
                <div className="form-group">
                  <label>Türler</label>
                  <input name="genres" placeholder='["Sci-Fi", "Action"]' />
                </div>
              </div>
              <div className="form-group">
                <label>Poster URL</label>
                <input name="poster_url" placeholder="https://..." />
              </div>
              <button type="submit" className="btn-primary">Filmi Kaydet</button>
            </form>

            <h2 style={{ marginTop: '40px' }}>Film Listesi</h2>

          
            <div style={{ marginBottom: '15px' }}>
              <input
                type="text"
                placeholder="Film ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '4px',
                  border: '1px solid #444',
                  backgroundColor: '#222',
                  color: '#fff'
                }}
              />
            </div>

            <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Poster</th>
                    <th>Başlık</th>
                    <th>Yıl</th>
                    <th>İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredMovies.map(m => (
                    <tr key={m.id}>
                      <td>{m.id}</td>
                      <td>
                        <img
                          src={m.poster_url || `https://image.tmdb.org/t/p/w92${m.poster_path}`}
                          alt={m.title}
                          style={{ width: '40px', borderRadius: '4px' }}
                        />
                      </td>
                      <td>{m.title}</td>
                      <td>{m.release_date ? m.release_date.split("-")[0] : "-"}</td>
                      <td>
                        <button className="btn-small delete" onClick={() => handleDeleteMovie(m.id)}>Sil</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

       
        {activeTab === "messages" && (
          <div>
            <h2>Gelen Mesajlar</h2>
            <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Tarih</th>
                    <th>Gönderen</th>
                    <th>Mesaj</th>
                    <th>Cevap Durumu</th>
                    <th>İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  {messages.map(m => (
                    <tr key={m.id}>
                      <td>{new Date(m.created_at).toLocaleDateString()}</td>
                      <td>
                        <div><strong>{m.name}</strong></div>
                        <div style={{ fontSize: '0.9em', color: '#aaa' }}>{m.email}</div>
                      </td>
                      <td style={{ maxWidth: '300px' }}>{m.message}</td>
                      <td>
                        {m.reply ? (
                          <span style={{ color: 'lime' }}>Cevaplandı</span>
                        ) : (
                          <span style={{ color: 'orange' }}>Bekliyor</span>
                        )}
                        {m.reply && <div style={{ fontSize: '0.8em', color: '#999', marginTop: 5 }}>Cevap: {m.reply}</div>}
                      </td>
                      <td>
                        <button className="btn-small" onClick={() => handleReply(m.id, m.reply)}>
                          {m.reply ? "Düzenle" : "Cevapla"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        
        {activeTab === "settings" && (
          <div className="settings-container">
            <h2>Sistem Ayarları</h2>

            <div className="setting-card">
              <div className="setting-info">
                <h4>Yeni Üye Alımı</h4>
                <p>Siteye yeni kullanıcı kayıtlarını duraklat.</p>
              </div>
              <label className="switch">
                <input type="checkbox" defaultChecked />
                <span className="slider round"></span>
              </label>
            </div>

            <div className="setting-card">
              <div className="setting-info">
                <h4>Bakım Modu</h4>
                <p>Siteyi sadece adminlerin erişimine açık hale getir.</p>
              </div>
              <label className="switch">
                <input type="checkbox" />
                <span className="slider round"></span>
              </label>
            </div>

            <div className="setting-card">
              <div className="setting-info">
                <h4>Önbellek (Cache) Temizle</h4>
                <p>Redis/Local önbelleği sıfırlar.</p>
              </div>
              <button className="btn-small delete" onClick={() => alert("Önbellek temizlendi!")}>Temizle</button>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
