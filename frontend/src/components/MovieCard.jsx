import React from "react";
import { Link } from "react-router-dom";
import "./MovieCard.css";

export default function MovieCard({ id, title, poster_path, poster_url, vote_average, type }) {
  const linkPath = type === "upcoming" ? `/upcoming/${id}` : `/movies/${id}`;

  const imageSrc = poster_url
    ? poster_url
    : poster_path
      ? `https://image.tmdb.org/t/p/w500${poster_path}`
      : "https://via.placeholder.com/300x450?text=No+Poster";

  return (
    <Link to={linkPath} className="movie-card">
      <div className="poster-wrap">
        <img
          src={imageSrc}
          alt={title}
          className="poster"
        />
        <span className="rating">⭐ {vote_average?.toFixed(1)}</span>
      </div>

      <h3 className="movie-title">{title}</h3>
    </Link>
  );
}
