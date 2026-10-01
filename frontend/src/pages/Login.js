import React, { useState } from "react";
import { apiFetch } from "../api";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true); 
  const [message, setMessage] = useState("");

  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleLogin(e) {
    e.preventDefault();
    setMessage("");

    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: { email, password },
      });

      
      const me = await apiFetch("/auth/me", { token: data.access_token });

      login(me, data.access_token, rememberMe);

      setMessage("Giriş başarılı! Yönlendiriliyorsunuz...");
      setTimeout(() => navigate("/"), 800);

    } catch (err) {
      console.log("LOGIN ERROR:", err);
      setMessage(err.detail || "Giriş başarısız.");
    }
  }

  return (
    <div className="auth-background">
      <div className="auth-card">
        <h1 className="auth-title">Giriş Yap</h1>

        <form onSubmit={handleLogin}>
          <input
            type="email"
            className="auth-input"
            placeholder="E-posta"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            className="auth-input"
            placeholder="Şifre"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <div className="auth-options">
            <label className="remember-me">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              Beni Hatırla
            </label>
          </div>


          <button className="auth-button">Giriş Yap</button>
        </form>

        {message && <p className="auth-message">{message}</p>}

        <p className="auth-switch">
          FilmRec'te yeni misin?
          <span onClick={() => navigate("/register")}> Hemen kayıt ol.</span>
        </p>
      </div>
    </div>
  );
}

export default Login;
