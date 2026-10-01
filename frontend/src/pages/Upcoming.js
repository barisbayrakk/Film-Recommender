// frontend/src/pages/Upcoming.js

import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";
import MovieCard from "../components/MovieCard";
import "./Home.css"; 

export default function Upcoming() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch("/movies/upcoming");

        
        const today = new Date();
        const onlyFuture = data.filter((m) => {
          if (!m.release_date) return false;
          
          const rDate = new Date(m.release_date);
          const tDate = new Date();
          tDate.setHours(0, 0, 0, 0);
          rDate.setHours(0, 0, 0, 0);

          return rDate > tDate;
        });

        
        const sorted = [...onlyFuture].sort(
          (a, b) =>
            new Date(a.release_date).getTime() -
            new Date(b.release_date).getTime()
        );

        setMovies(sorted);
      } catch (err) {
        console.error("Upcoming load error:", err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  if (loading) {
    return (
      <div className="home-container">
        <h2 style={{ color: "white", marginTop: 40 }}>Yakında çıkacak filmler yükleniyor...</h2>
      </div>
    );
  }

  return (
    <div className="home-container">
      <h1 style={{ color: "white", margin: "20px 0" }}>Yakında Vizyona Girecek Filmler</h1>

      <div className="movie-grid">
        {movies.map((m) => (
          <MovieCard
            key={m.id}
            id={m.id}
            title={m.title}
            poster_path={m.poster_path}
            vote_average={m.vote_average}
          />
        ))}
      </div>
    </div>
  );
}
