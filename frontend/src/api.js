// frontend/src/api.js
// --------------------------------------------------
// Frontend için merkezi API çağrı yardımcı dosyası
// - Base URL yönetimi
// - Token handling (localStorage / sessionStorage)
// - Timeout & hata yönetimi
// --------------------------------------------------


// --------------------------------------------------
// API BASE URL
// --------------------------------------------------
// React ortam değişkeninden API URL al
let API_URL = process.env.REACT_APP_API_URL;
// Eğer tanımlı değilse boş string kullan
if (!API_URL) {
  API_URL = "";
}

// --------------------------------------------------
// URL DÜZENLEME
// --------------------------------------------------
// Sondaki "/" karakterini temizle
// Örn: https://api.site.com/ -> https://api.site.com
API_URL = API_URL.replace(/\/$/, "");

// --------------------------------------------------
// GENEL API FETCH FONKSİYONU
// --------------------------------------------------
export async function apiFetch(path, { method = "GET", body = null, token = null } = {}) {
  if (!path.startsWith("/")) path = "/" + path;

  const url = API_URL + path;

  const headers = { "Content-Type": "application/json" };

  // --------------------------------------------------
  // TOKEN YÖNETİMİ
  // --------------------------------------------------
  // Öncelik sırası:
  // 1) Fonksiyon parametresi olarak verilen token
  // 2) localStorage
  // 3) sessionStorage
  const finalToken = token || localStorage.getItem("token") || sessionStorage.getItem("token"); 
  // Token varsa Authorization header ekle
  if (finalToken) headers["Authorization"] = `Bearer ${finalToken}`;

  let res;
  try {
    // --------------------------------------------------
    // TIMEOUT MEKANİZMASI
    // --------------------------------------------------
    // Backend yavaşsa isteği 30 saniye sonra iptal et
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    // Fetch isteği
    res = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
     // Timeout iptal edilir (istek başarılıysa)
    clearTimeout(timeoutId);
  } catch (err) {
    // Ağ veya bağlantı hatası (Backend kapalı veya timeout)
    if (err.name === 'AbortError') {
      throw { status: 0, detail: "İstek zaman aşımına uğradı. Lütfen tekrar deneyin." };
    }
    throw { status: 0, detail: `Bağlantı hatası: ${err.message}` };
  }
   // --------------------------------------------------
  // RESPONSE PARSE
  // --------------------------------------------------
  // Önce text olarak oku
  const text = await res.text();
  let data = null;
  try {
    // Yanıt gövdesi varsa JSON olarak parse et
    data = text ? JSON.parse(text) : null;
  } catch {
    // JSON değilse veya boşsa, metin olarak kalabilir.
    data = text;
  }

  if (!res.ok) {
    // Backend'den 4xx veya 5xx hata kodu gelirse
    let detailMessage = "API hatası";
    if (typeof data === 'object' && data?.detail) {
      detailMessage = data.detail;
    } else if (typeof data === 'string' && data) {
      // Hata gövdesi bir string ise
      detailMessage = data;
    }

    throw {
      status: res.status,
      detail: detailMessage,
    };
  }

  return data;
}

// CAPTCHA Al
export async function getCaptcha() {
  return apiFetch("/contact/captcha");
}

// Mesaj Gönder
export async function sendContactMessage(formData) {
  return apiFetch("/contact/send", {
    method: "POST",
    body: formData,
  });
}