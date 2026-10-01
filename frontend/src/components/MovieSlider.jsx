import React, { useEffect, useState } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "./MovieSlider.css";

function MovieSlider({ title, endpoint }) {
  const [movies, setMovies] = useState([]);

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    fetch(API_URL + endpoint)
      .then(res => res.json())
      .then(setMovies)
      .catch(console.error);
  }, [endpoint]);

  return (
    <div className="slider-section">
      <h2 className="slider-title">{title}</h2>

      <Swiper spaceBetween={15} slidesPerView={6}>
        {movies.map(movie => (
          <SwiperSlide key={movie.id}>
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="slider-poster"
            />
            <p className="slider-name">{movie.title}</p>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
}

export default MovieSlider;
