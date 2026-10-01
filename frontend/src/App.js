// frontend/src/App.js
// --------------------------------------------------
// React uygulamasının ana routing (yönlendirme) dosyası
// - Sayfa rotaları
// - Admin korumalı route
// - Ortak bileşenler (Navbar, Chatbot)
// --------------------------------------------------

// Admin paneli
import AdminDashboard from "./pages/AdminDashboard";
// i18n (çoklu dil) yapılandırması
import "./i18n/i18n";
// React çekirdeği
import React from "react";
import { Routes, Route } from "react-router-dom";
// Statik sayfalar
import About from "./pages/About";
import Contact from "./pages/Contact";
// Ortak bileşenler
import Navbar from "./components/Navbar";
// Ana sayfalar
import Home from "./pages/Home";
import MovieList from "./pages/MovieList";
import MovieDetail from "./pages/MovieDetail";
// Auth sayfaları
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
// Kullanıcı sayfaları
import Profile from "./pages/Profile";
import WatchList from "./pages/watchlist";
// Admin route guard
import AdminRoute from "./components/AdminRoute";
// Chatbot bileşeni
import Chatbot from "./components/Chatbot";
// Oyuncu / kişi arama sayfası
import PersonSearch from "./pages/PersonSearch";
// Eğlenceli içerikler
import DidYouKnow from "./pages/DidYouKnow"; 
import QuizShow from "./pages/QuizShow";

function App() {
  return (
    <>
      <Navbar />

      <Routes>
        {/* Ana Sayfa */}
        <Route path="/" element={<Home />} />
        <Route path="/admin" element={<AdminDashboard />} />

        {/* Film Listeleri */}
        <Route path="/movies" element={<MovieList type="all" />} />
        <Route path="/trending" element={<MovieList type="trending" />} />
        <Route path="/upcoming" element={<MovieList type="upcoming" />} />

        {/* Film Detayları */}
        <Route path="/movies/:id" element={<MovieDetail />} />
        <Route path="/upcoming/:id" element={<MovieDetail type="upcoming" />} />
        <Route path="/person/:name" element={<PersonSearch />} /> {/* 🔥 New Route */}

        {/* Diziler */}
        <Route
          path="/series"
          element={<div style={{ padding: 32 }}>Diziler yakında...</div>}
        />

        {/* Watchlist / Profil */}
        <Route path="/watchlist" element={<WatchList />} />

        {/* Admin Protected Route */}
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          }
        />

        <Route path="/profile" element={<Profile />} />

        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/did-you-know" element={<DidYouKnow />} />
        <Route path="/quiz" element={<QuizShow />} />

        {/* Auth */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
      </Routes>
      <Chatbot />
    </>
  );
}

export default App;
