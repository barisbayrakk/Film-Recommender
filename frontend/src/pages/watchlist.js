import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";
import MovieCard from "../components/MovieCard";
import "../components/MovieCard.css";
import "./watchlist.css";

export default function WatchList() {
  const [likedMovies, setLikedMovies] = useState([]);
  const [watchlistMovies, setWatchlistMovies] = useState([]);
  const [watchedMovies, setWatchedMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  // Verileri Yükle
  const loadData = async () => {
    setLoading(true);
    try {
      
      const userCols = await apiFetch("/user/collections");
      setLikedMovies(userCols.liked || []);
      setWatchlistMovies(userCols.watchlist || []);
      setWatchedMovies(userCols.watched || []);

    } catch (err) {
      console.error("Veri yüklenemedi", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Beğeni Kaldır
  const handleUnlike = async (movieId) => {
    try {
      await apiFetch(`/likes/toggle/${movieId}`, { method: 'POST' });
      setLikedMovies(prev => prev.filter(m => (m.movie_id || m.id) !== movieId));
    } catch (err) { alert("İşlem başarısız"); }
  };

  // İzleme Listesinden Kaldır
  const handleRemoveFromWatchlist = async (movieId) => {
    try {
      await apiFetch(`/user/watchlist/${movieId}`, { method: 'DELETE' });
      setWatchlistMovies(prev => prev.filter(m => (m.movie_id || m.id) !== movieId));
    } catch (err) { alert("İşlem başarısız"); }
  };

  // İzlediklerimden Kaldır (Toggle mantığı çalışır)
  const handleRemoveWatched = async (movieId) => {
    try {
      await apiFetch(`/watched/${movieId}`, { method: 'POST' });
      setWatchedMovies(prev => prev.filter(m => (m.movie_id || m.id) !== movieId));
    } catch (err) { alert("İşlem başarısız"); }
  };

  if (loading) return <div className="page-container loading"><h2>Yükleniyor...</h2></div>;

  return (
    <div className="page-container container watchlist-page">
      <header className="watchlist-header">
        <h1 className="page-title">Kütüphanem</h1>
        <p className="page-subtitle">Beğendiğin filmler ve kişisel listelerin burada.</p>
      </header>

      {/* --- BEĞENDİKLERİM --- */}
      <section className="watchlist-section liked-section">
        <div className="section-header-row">
          <h2>❤️ Beğendiklerim</h2>
          <span className="count-badge">{likedMovies?.length || 0} Film</span>
        </div>

        <div className="movie-grid">
          {likedMovies && likedMovies.length > 0 ? (
            likedMovies.map((movie) => (
              <div key={movie.id} className="movie-grid-item">
                <MovieCard
                  id={movie.movie_id || movie.id}
                  title={movie.title}
                  poster_path={movie.poster_path}
                  poster_url={movie.poster_url}
                  vote_average={movie.vote_average}
                />
                <button
                  className="remove-movie-btn"
                  onClick={() => handleUnlike(movie.movie_id || movie.id)}
                  title="Beğenmekten Vazgeç"
                >
                  ✕
                </button>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <span className="empty-icon">💔</span>
              <p>Henüz hiç film beğenmedin.</p>
            </div>
          )}
        </div>
      </section>

      <div className="divider"></div>

      {/* --- İZLEME LİSTEM --- */}
      <section className="watchlist-section liked-section">
        <div className="section-header-row">
          <h2>📌 İzleme Listem</h2>
          <span className="count-badge">{watchlistMovies?.length || 0} Film</span>
        </div>

        <div className="movie-grid">
          {watchlistMovies && watchlistMovies.length > 0 ? (
            watchlistMovies.map((movie) => (
              <div key={movie.id} className="movie-grid-item">
                <MovieCard
                  id={movie.movie_id || movie.id}
                  title={movie.title}
                  poster_path={movie.poster_path}
                  poster_url={movie.poster_url}
                  vote_average={movie.vote_average}
                />
                <button
                  className="remove-movie-btn"
                  onClick={() => handleRemoveFromWatchlist(movie.movie_id || movie.id)}
                  title="Listeden Çıkar"
                >
                  ✕
                </button>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <span className="empty-icon">📝</span>
              <p>İzleme listen henüz boş.</p>
            </div>
          )}
        </div>
      </section>

      <div className="divider"></div>

      {/* --- İZLEDİKLERİM --- */}
      <section className="watchlist-section liked-section">
        <div className="section-header-row">
          <h2>👀 İzlediklerim</h2>
          <span className="count-badge">{watchedMovies?.length || 0} Film</span>
        </div>

        <div className="movie-grid">
          {watchedMovies && watchedMovies.length > 0 ? (
            watchedMovies.map((movie) => (
              <div key={movie.id} className="movie-grid-item">
                <MovieCard
                  id={movie.movie_id || movie.id}
                  title={movie.title}
                  poster_path={movie.poster_path}
                  poster_url={movie.poster_url}
                  vote_average={movie.vote_average}
                />
                {movie.user_rating > 0 && (
                  <div className="user-rating-badge">
                    ★ {movie.user_rating}
                  </div>
                )}
                <button
                  className="remove-movie-btn"
                  onClick={() => handleRemoveWatched(movie.movie_id || movie.id)}
                  title="İzlediklerimden Çıkar"
                >
                  ✕
                </button>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <span className="empty-icon">🎬</span>
              <p>Henüz izlediğin film yok.</p>
            </div>
          )}
        </div>
      </section>


    </div>
  );
}
