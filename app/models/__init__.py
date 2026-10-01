# Movie (Film) ORM model sınıfını içe aktarır
# Filmlere ait veritabanı tablosunu temsil eder
from .movie import Movie
# User (Kullanıcı) ORM model sınıfını içe aktarır
# Kullanıcı bilgileri ve kimlik doğrulama verilerini içerir
from .users import User
# Rating (Puanlama) ORM model sınıfını içe aktarır
# Kullanıcıların filmlere verdiği puanları temsil eder
from .rating import Rating
# Review (Yorum) ORM model sınıfını içe aktarır
# Kullanıcıların filmler hakkında yazdığı metinsel yorumları tutar
from .review import Review
# ListItem ORM model sınıfını içe aktarır
# Kullanıcının izleme listesi (watchlist) veya favori listesi gibi
# film listelerini temsil eder
from .lists import ListItem
# --------------------------------------------------
# DIŞA AÇILACAK MODEL SINIFLARI
# --------------------------------------------------

# __all__ değişkeni, bu paket dışından
# hangi sınıfların erişilebilir olacağını tanımlar.
# Böylece yalnızca gerekli model sınıfları dışa açılır
# ve kodun okunabilirliği ile güvenliği artırılır.
__all__ = ["Movie", "User", "Rating", "Review", "ListItem"]
