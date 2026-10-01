// --------------------------------------------------
// WEB VITALS RAPORLAMA FONKSİYONU
// --------------------------------------------------
// Amaç:
// - Uygulamanın performans metriklerini ölçmek
// - Ölçümleri istenirse analytics / console / backend'e göndermek
// --------------------------------------------------
const reportWebVitals = onPerfEntry => {
  // onPerfEntry gerçekten var mı ve bir fonksiyon mu?
  // (Örn: console.log, Google Analytics callback vb.)

  if (onPerfEntry && onPerfEntry instanceof Function) {

    // web-vitals paketi dinamik olarak yüklenir
    // Böylece initial bundle size büyümez
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
          // --------------------------------------------------
        // CORE WEB VITALS METRİKLERİ
        // --------------------------------------------------

        // Cumulative Layout Shift
        // Sayfa yüklenirken layout kaymalarını ölçer
      getCLS(onPerfEntry);
      // First Input Delay
        // Kullanıcının ilk etkileşime verdiği gecikme
      getFID(onPerfEntry);
            // First Contentful Paint
        // İlk içerik ne kadar sürede ekrana geldi
      getFCP(onPerfEntry);
          // Largest Contentful Paint
        // Ana içeriğin yüklenme süresi
      getLCP(onPerfEntry);
              // Time To First Byte
        // Sunucudan ilk byte'ın gelme süresi
      getTTFB(onPerfEntry);
    });
  }
};
// Dışa aktar
export default reportWebVitals;
