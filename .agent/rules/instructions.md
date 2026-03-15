---
trigger: always_on
---

🛡️ Antigravity: Yapısal Bütünlük ve Kaos Engelleme Protokolü
Bu kural, Influencer Factory projesinin "Spagetti Kod" yığınına dönüşmesini engellemek ve AI'nın mevcudu korumasını sağlamak için tasarlanmıştır.

1. Önce Gözlemle, Sonra Hareket Et (Observation First)
Keşif Mandatı: Herhangi bir kod yazmadan veya dosya oluşturmadan önce, çalışma dizinini ve ilgili dosyaları mutlaka taramalısın.

Varlık Kontrolü: Eğer 'a' değişkenine, fonksiyonuna veya dosyasına ihtiyacın varsa ve bulamıyorsan; yeni bir tane oluşturma. Önce grep veya dosya gezgini ile mevcut olup olmadığını teyit et.

2. Mevcut Yapıyı Onurlandır (Respect the Legacy)
Yeniden İcat Etme: Mevcut bir mantık (logic) veya değişken zaten varsa, onu kullan. Mevcut olanı bulamadığın için benzer işi yapan paralel bir yapı kurmak kesinlikle yasaktır.

Bağımlılık Analizi: Bir dosyayı değiştirmeden önce, o dosyanın diğer hangi dosyaları beslediğini (import/export) kontrol et. Bir yeri tamir ederken diğer tarafı yıkma.

3. "Kır-Dök" Yasağı ve Dur-Sor Protokolü (Stop & Ask)
Erişim Engeli: Eğer bir kaynağa ('a' değişkeni gibi) erişemiyorsan veya yolunu (path) bulamıyorsan; asla placeholder veya sahte (mock) bir yapı oluşturma.

Kırmızı Bayrak: Kaynağın eksik olduğunu veya kafanın karıştığını fark ettiğin anda işlemi durdur ve kullanıcıya şu formatta haber ver:

⚠️ YAPI ÇATIŞMASI: '[X]' görevini yapmak için '[a]' öğesine ihtiyacım var ancak projede birden fazla '[a]' buldum veya '[a]'ya erişemiyorum. Devam etmek için yeni bir yapı mı kurayım yoksa mevcut '[a]'nın yolunu mu göstermek istersin?

4. Minimalist Müdahale (Atomic Changes)
Görev Sapması: Sadece senden istenen göreve odaklan. "Hazır elim değmişken şurayı da düzelteyim" diyerek projenin genel mimarisini bozacak geniş çaplı refactoring işlemlerine girme.

Dosya Kirliliği: Tek bir fonksiyon için yeni bir dosya oluşturma. Mevcut yardımcı (utility) dosyalarını kullan.

5. Doğrulama (Self-Check)
Kodu teslim etmeden önce kendine şu soruyu sor: "Ben şu an mevcuttaki bir şeyi mi kullandım, yoksa projede zaten olan bir şeyin kopyasını mı yarattım?" Cevap "kopya" ise kodu sil ve mevcuda entegre et.
