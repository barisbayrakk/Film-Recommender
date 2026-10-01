// src/components/SuperNavbar.js
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function SuperNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Avatar harfi
  const avatarLetter = user?.name?.charAt(0)?.toUpperCase() || "?";

  return (
    <nav style={styles.nav}>
      {/* Sol Logo */}
      <div style={styles.logo} onClick={() => navigate("/")}>
        🎬 <span style={{ fontWeight: "bold" }}>CineMind</span>
      </div>

      {/* Sağ Menü */}
      <div style={styles.menu}>
        <Link style={styles.link} to="/">Home</Link>

        {/* Kullanıcı Giriş Yapmamışsa */}
        {!user && (
          <>
            <Link style={styles.link} to="/login">Login</Link>
            <Link style={styles.link} to="/register">Register</Link>
          </>
        )}

        {/* Kullanıcı Giriş Yapmışsa */}
        {user && (
          <>
            <Link style={styles.link} to="/profile">Profile</Link>

            {/* Avatar */}
            <div style={styles.avatar}>{avatarLetter}</div>

            <button style={styles.logoutBtn} onClick={handleLogout}>
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}

const styles = {
  nav: {
    width: "100%",
    padding: "14px 32px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    background:
      "linear-gradient(90deg, #ff0080, #ff4d4d, #7a00ff, #4d79ff)",
    color: "white",
    position: "sticky",
    top: 0,
    zIndex: 100,
    boxShadow: "0 0 15px rgba(255,255,255,0.2)",
  },

  logo: {
    fontSize: "24px",
    cursor: "pointer",
    transition: "0.3s",
  },

  menu: {
    display: "flex",
    alignItems: "center",
    gap: "22px",
    fontSize: "18px",
  },

  link: {
    textDecoration: "none",
    color: "white",
    fontWeight: "500",
    transition: "0.2s",
  },

  avatar: {
    width: "40px",
    height: "40px",
    background: "white",
    color: "#222",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "bold",
    fontSize: "18px",
    boxShadow: "0 0 8px rgba(0,0,0,0.4)",
  },

  logoutBtn: {
    background: "rgba(255,255,255,0.2)",
    border: "1px solid rgba(255,255,255,0.5)",
    color: "white",
    padding: "6px 14px",
    borderRadius: "6px",
    cursor: "pointer",
    backdropFilter: "blur(3px)",
    transition: "0.2s",
  },
};

export default SuperNavbar;
