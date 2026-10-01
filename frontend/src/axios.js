// HTTP istekleri için Axios kütüphanesi
import axios from "axios";

// --------------------------------------------------
// API BASE URL
// --------------------------------------------------
// .env dosyasından backend API adresi alınır
const API_URL = process.env.REACT_APP_API_URL;

// --------------------------------------------------
// AXIOS INSTANCE
// --------------------------------------------------
// Ortak ayarlarla tek bir axios instance oluşturulur
// Böylece her yerde aynı baseURL kullanılır
const api = axios.create({
  baseURL: API_URL,
});

// --------------------------------------------------
// REQUEST INTERCEPTOR (TOKEN EKLEME)
// --------------------------------------------------
// Her request gönderilmeden önce otomatik çalışır
// Amaç:
// - localStorage'daki token'ı al
// - Authorization header olarak ekle
api.interceptors.request.use((config) => {
    // Kullanıcının giriş token'ı
  const token = localStorage.getItem("token");
  // Token varsa Authorization header ekle
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Güncellenmiş config'i geri döndür
  return config;
});

// --------------------------------------------------
// EXPORT
// --------------------------------------------------
// Bu instance import edilerek tüm API çağrıları yapılır
export default api;
