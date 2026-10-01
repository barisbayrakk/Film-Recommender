import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../api";
import "./PersonSearch.css";

export default function PersonSearch() {
    const { name } = useParams();
    const navigate = useNavigate();
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function search() {
            setLoading(true);
            try {
                const data = await apiFetch(`/movies/search/${encodeURIComponent(name)}`);
                setMovies(data || []);
            } catch (err) {
                console.error("Search failed", err);
            } finally {
                setLoading(false);
            }
        }
        search();
    }, [name]);

    return (
        <div className="person-search-container">
            <div className="container">
                <h2 className="section-title">
                    <span style={{ color: "#e50914" }}>{name}</span> ile ilgili sonuçlar
                </h2>

                {loading ? (
                    <div className="loading-text">Aranıyor...</div>
                ) : (
                    <>
                        {movies.length === 0 ? (
                            <p className="no-results">Bu kişiyle ilgili film bulunamadı.</p>
                        ) : (
                            <div className="movies-grid">
                                {movies.map((m) => (
                                    <div
                                        key={m.id}
                                        className="movie-card"
                                        onClick={() => navigate(`/movies/${m.id}`)}
                                    >
                                        <div className="poster-container">
                                            <img
                                                src={
                                                    m.poster_url ||
                                                    `https://image.tmdb.org/t/p/w300${m.poster_path}`
                                                }
                                                alt={m.title}
                                            />
                                            <div className="movie-overlay">
                                                <span className="movie-title">{m.title}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
