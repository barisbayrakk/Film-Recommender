import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function UpcomingDetail() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    fetch(`${API_URL}/movies/upcoming/detail/${id}`)
      .then(res => res.json())
      .then(setMovie);
  }, [id]);

  if (!movie) return <>Yükleniyor...</>;

  return (
    <div style={{ color: "white", padding: 32 }}>
      <img
        src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
        style={{ width: 300 }}
      />
      <h1>{movie.title}</h1>
      <p>{movie.overview}</p>

      <h3>Yönetmen</h3>
      <p>{movie.directors[0].name}</p>

      <h3>Oyuncular</h3>
      {movie.cast.map(c => (
        <div style={{ marginBottom: 10 }}>
          {c.name} → {c.character}
        </div>
      ))}
    </div>
  );
}
