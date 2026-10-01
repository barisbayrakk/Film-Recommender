// frontend/src/pages/Home.js

import React, { useEffect, useState } from "react";
import MovieCard from "../components/MovieCard";
import { apiFetch } from "../api";
import { useNavigate } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [personalRecs, setPersonalRecs] = useState([]);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [heroMovie, setHeroMovie] = useState(null);

 
  const [query, setQuery] = useState("");
  const [filtered, setFiltered] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [allMovies, setAllMovies] = useState([]);

  const token = localStorage.getItem("token");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        
        const allData = await apiFetch("/movies/all");
        setAllMovies(allData);
        setFiltered(allData);

       
        const pinnedActors = ["Al Pacino", "Brad Pitt", "Tom Hanks", "Leonardo DiCaprio"];

        const sorted = [...allData].sort((a, b) => {
          
          const hasPinnedA = (a.cast || []).some(c => pinnedActors.some(p => c.name.includes(p)));
          const hasPinnedB = (b.cast || []).some(c => pinnedActors.some(p => c.name.includes(p)));

          if (hasPinnedA && !hasPinnedB) return -1;
          if (!hasPinnedA && hasPinnedB) return 1;

          
          return (b.popularity || 0) - (a.popularity || 0);
        });

        setTrending(sorted);

        
        if (token) {
          try {
            const dashData = await apiFetch("/dashboard/user");
            setDashboard(dashData);
            setPersonalRecs(dashData.recommendations || []);
          } catch (e) {
            console.error("Dashboard load failed", e);
          }
        }

      } catch (err) {
        console.error("Home load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [token]);

  
  useEffect(() => {
    const source = personalRecs.length > 0 ? personalRecs : trending;
    if (source.length > 0) {
      const random = source[Math.floor(Math.random() * Math.min(5, source.length))];
      setHeroMovie(random);
    }
  }, [personalRecs, trending]);

  const handleRandomPick = () => {
    const source = trending.length > 0 ? trending : [];
    if (source.length > 0) {
      const random = source[Math.floor(Math.random() * source.length)];
      navigate(`/movies/${random.id}`);
    }
  };

  
  const handleSearch = async () => {
    const q = query.trim();
    if (!q) {
      setIsSearching(false);
      return;
    }
    setIsSearching(true);

    try {
      const results = await apiFetch(`/movies/search/${q}`);
      setFiltered(results);
    } catch (err) {
      console.error("Search error:", err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  const [selectedCategory, setSelectedCategory] = useState("all");

  const filterCategory = (type) => {
    setQuery("");
    setSelectedCategory(type); 

    if (type === "all") {
      setIsSearching(false);
      return;
    }
    setIsSearching(true);
    let result = [];
    switch (type) {
      case "turk":
        
        result = allMovies.filter(m => m.original_language === 'tr');
        break;
      case "imdb85":
        result = allMovies.filter(m => (m.vote_average || 0) >= 8.5);
        break;
      case "aksiyon":
        result = allMovies.filter(m => /aksiyon|action/i.test(JSON.stringify(m.genres || [])));
        break;
      case "dram":
        result = allMovies.filter(m => /drama|dram/i.test(JSON.stringify(m.genres || [])));
        break;
      case "komedi":
        result = allMovies.filter(m => /komedi|comedy/i.test(JSON.stringify(m.genres || [])));
        break;
      case "bilim":
        result = allMovies.filter(m => /science|bilim/i.test(JSON.stringify(m.genres || [])));
        break;
      case "korku":
        result = allMovies.filter(m => /horror|korku/i.test(JSON.stringify(m.genres || [])));
        break;
      case "romantik":
        result = allMovies.filter(m => /romance|romantik/i.test(JSON.stringify(m.genres || [])));
        break;
      case "animasyon":
        result = allMovies.filter(m => /animation|animasyon/i.test(JSON.stringify(m.genres || [])));
        break;
      case "aile":
        result = allMovies.filter(m => /family|aile/i.test(JSON.stringify(m.genres || [])));
        break;
      case "belgesel":
        result = allMovies.filter(m => /documentary|belgesel/i.test(JSON.stringify(m.genres || [])));
        break;
      default:
        result = allMovies;
    }

    
    result = result.sort((a, b) => (b.vote_average || 0) - (a.vote_average || 0));

    setFiltered(result);
  };

  const handleSort = (criteria) => {
    let sorted = [...filtered];

    sorted.sort((a, b) => {
      const ratingA = a.vote_average || 0;
      const ratingB = b.vote_average || 0;
      const hasRatingA = ratingA > 0;
      const hasRatingB = ratingB > 0;

      
      if (hasRatingA && !hasRatingB) return -1;
      if (!hasRatingA && hasRatingB) return 1;

      
      if (criteria === 'year') {
        return new Date(b.release_date || 0) - new Date(a.release_date || 0);
      } else if (criteria === 'imdb') {
        return ratingB - ratingA;
      }
      return 0;
    });

    setFiltered(sorted);
  };

  if (loading) return <div className="loading-screen">Yükleniyor...</div>;

  return (
    <div className="home-container">

     
      <header
        className="hero-section brand-hero"
        style={{
          position: 'relative',
          height: '70vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          textAlign: 'center',
          overflow: 'hidden',
          backgroundColor: '#000'
        }}
      >
        
        <div className="film-strip-bg"></div>
        <div className="film-strip-overlay"></div>
        <div className="hero-content animate-fade-up">

          
          <div className="brand-icon-wrapper">
            <div className="clapperboard">
              <div className="clapper-top"></div>
              <div className="clapper-bottom"></div>
            </div>
          </div>

          
          <h1 className="brand-title">
            Film<span style={{ color: '#e50914' }}>Rec</span>
          </h1>

         
          <p className="brand-subtitle">
            En iyi filmleri keşfet, incele ve favorilerine ekle!
          </p>

          
          <div className="search-box-brand">
            <input
              type="text"
              placeholder="Bilim kurgu, romantik, komedi..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button onClick={handleSearch} className="search-btn-brand">
              Bul 🔍
            </button>
          </div>

          
          <div className="quick-filters">
            <button className="filter-pill" onClick={() => filterCategory("bilim")}>Bilim Kurgu</button>
            <button className="filter-pill" onClick={() => filterCategory("korku")}>Korku</button>
            <button className="filter-pill" onClick={() => filterCategory("turk")}>Türk Filmleri</button>

            <button className="filter-pill" onClick={() => filterCategory("dram")}>Dram</button>
            <button className="filter-pill" onClick={() => filterCategory("komedi")}>Komedi</button>
            <button className="filter-pill" onClick={() => filterCategory("romantik")}>Romantik</button>
            <button className="filter-pill" onClick={() => filterCategory("animasyon")}>Animasyon</button>
            <button className="filter-pill" onClick={() => filterCategory("aile")}>Aile</button>
            <button className="filter-pill" onClick={() => filterCategory("belgesel")}>Belgesel</button>
          </div>



        </div>
      </header>

      <div className="container dashboard-main">

        
        {isSearching ? (
          <div className="section-block">
            <div className="section-header-row" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '25px', marginTop: '40px' }}>
              <h2 className="section-title" style={{ margin: 0 }}>Arama Sonuçları ({filtered.length})</h2>

              
              {isSearching && (
                <div className="sort-controls animate-fade-in" style={{ marginTop: 0, background: 'rgba(255,255,255,0.05)' }}>
                  <span className="sort-label">Sırala:</span>
                  <button className="sort-btn" onClick={() => handleSort('year')}>📅 Yıla Göre</button>
                  <button className="sort-btn" onClick={() => handleSort('imdb')}>⭐ IMDb Puanına Göre</button>
                </div>
              )}
            </div>
            <div className="movie-grid">
              {filtered.map((m) => (
                <MovieCard key={m.id} id={m.id} title={m.title} poster_path={m.poster_path} vote_average={m.vote_average} />
              ))}
              {filtered.length === 0 && <p className="no-results">Sonuç bulunamadı.</p>}
            </div>
          </div>
        ) : (
          
          <>
            
            <div className="section-block">
              <h2 className="section-title">Popüler Filmler 🍿</h2>
              <div className="movie-grid">
                {trending.slice(0, 54).map((m) => (
                  <MovieCard key={m.id} {...m} />
                ))}
              </div>
            </div>
          </>
        )}

      </div>
    </div >
  );
}
