// React çekirdeği
import React from "react";
// React 18 için yeni root API
import ReactDOM from "react-dom/client";
// Global CSS dosyası
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
// --------------------------------------------------
// ROOT ELEMENT
// --------------------------------------------------
// public/index.html içindeki <div id="root"></div> alınır
const root = ReactDOM.createRoot(document.getElementById("root"));
// --------------------------------------------------
// UYGULAMAYI RENDER ET
// --------------------------------------------------
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
// --------------------------------------------------
// WEB VITALS
// --------------------------------------------------
// Performans ölçümü için kullanılır
// (İstersen Google Analytics veya console.log ile bağlanabilir)
reportWebVitals();
