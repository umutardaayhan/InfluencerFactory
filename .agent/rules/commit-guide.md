---
trigger: always_on
---

🚀 Antigravity: Tam Kapsamlı Commit & Arşivleme Protokolü

Bu kural, her görev bitiminde projenin mevcut durumunu eksiksiz bir şekilde Git geçmişine mühürlemek için tasarlanmıştır.

---

## 1. "Snapshot" (Tam Kapsamlı Kayıt) Kuralı

**Eksiksiz Ekleme:**
Herhangi bir değişiklik (en ufak bir boşluk dahi olsa) yapıldığında, commit paketine sadece o dosya değil; projedeki tüm yeni, değiştirilmiş veya silinmiş dosyalar eklenmelidir.

**Komut Mandatı:**
Commit öncesi her zaman `git add .` (veya eşdeğeri) komutu çalıştırılarak çalışma dizininin tam bir kopyası stage'lenmelidir. Hiçbir dosya "untracked" (takip dışı) kalmamalıdır.

---

## 2. Türkçe Prosedürel Mesaj Formatı

Commit mesajları profesyonel yazılım standartlarına (Conventional Commits) uygun, ancak tamamen Türkçe olmalıdır. Mesaj yapısı şu şekilde kurulmalıdır:

```
<tip>(<kapsam>): <açıklama>
```

### Kullanılacak Standart Tipler:

* **feat:** Yeni bir özellik eklendiğinde
* **fix:** Bir hata düzeltildiğinde
* **docs:** Sadece dokümantasyonda değişiklik yapıldığında
* **style:** Kodun çalışmasını etkilemeyen görsel/biçimsel değişikliklerde
* **refactor:** Ne hata düzelten ne de özellik ekleyen kod düzenlemelerinde
* **perf:** Performansı artıran geliştirmelerde
* **chore:** Projenin kurulumu, bağımlılıkları veya rutin işleri (build süreçleri vb.) değiştiğinde

---

## 3. Örnek Commit Mesajları

```
feat(agents): Stratejist ajanına haftalık plan üretim yeteneği eklendi
```

```
fix(image): Nano Banana 2 API 500 hatası kırpma ile giderildi
```

```
style(cli): Rich panellerin hizalama sorunu düzeltildi
```

```
chore(git): .gitignore dosyasına output/ klasörü eklendi
```

---

## 4. Son Kontrol (Pre-Commit Check)

Commit işlemi tetiklenmeden önce şu soruyu sor:

> "Şu an stage'lenmemiş (add edilmemiş) tek bir dosya veya değişiklik bile kaldı mı?"

Eğer cevap "Evet" ise, her şeyi eklemeden commit atma.
