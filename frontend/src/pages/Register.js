// frontend/src/components/register.js

import React, { useState } from "react";
import { apiFetch } from "../api";
import { useNavigate } from "react-router-dom";
import "./Auth.css";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const navigate = useNavigate();

  async function handleRegister(e) {
    e.preventDefault();

    if (password !== confirmPassword) {
      setMessage("❌ Şifreler eşleşmiyor!");
      return;
    }

    if (!/[A-Z]/.test(password)) {
      setMessage("❌ Şifre en az bir büyük harf içermelidir!");
      return;
    }

    setMessage("Kayıt olunuyor...");

    try {
      const data = await apiFetch("/auth/register", {
        method: "POST",
        body: {
          username,
          email,
          password
        }
      });

      setMessage("✅ Kayıt başarılı! Hesap doğrulama linki e-posta adresinize gönderildi (Simülasyon). Şimdi giriş yapabilirsiniz.");
      
      alert("Kayıt başarılı! Lütfen e-posta adresinize (Mailtrap kutunuza) gönderilen doğrulama linkine tıklayın.");
      navigate("/login");

    } catch (err) {
      console.log("REGISTER ERROR:", err);

      if (err.status === 422) {
        // Doğrulama hatası
        setMessage("❌ Şifre en az 6 karakter olmalı ve geçerli bir e-posta girmelisiniz.");
      } else if (err.status === 400) {
        // Hata mesajını backend'den al
        setMessage(`❌ ${err.detail || "Bu e-posta veya kullanıcı adı zaten kullanılıyor."}`);
      } else if (err.status === 0) {
        // Bağlantı hatası
        setMessage(`❌ ${err.detail}`);
      } else {
        // Diğer beklenmeyen hatalar
        setMessage(`❌ Kayıt başarısız: ${err.detail || "Beklenmedik bir hata oluştu."}`);
      }
    }
  }

  return (
    <div className="auth-background">
      <div className="auth-card">
        <h1 className="auth-title">Kayıt Ol</h1>

        <form onSubmit={handleRegister}>
          <input
            className="auth-input"
            placeholder="Kullanıcı Adı"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <input
            type="email"
            className="auth-input"
            placeholder="E-posta Adresi"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            className="auth-input"
            placeholder="Şifre (en az 6 karakter)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <input
            type="password"
            className="auth-input"
            placeholder="Şifre Tekrar"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          <button type="submit" className="auth-button">Kayıt Ol</button>
        </form>

        {message && <p className={`auth-message ${message.includes("başarılı") ? 'success' : 'error'}`}>{message}</p>}

        <p className="auth-switch">
          Zaten hesabın var mı?{" "}
          <span onClick={() => navigate("/login")}>Giriş yap.</span>
        </p>
      </div>
    </div>
  );
}

export default Register;