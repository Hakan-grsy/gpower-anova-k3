# AI Klinik Ajanı Değerlendirme Raporu (evaluation_results.md)

Bu rapor, `src/agent.py` içinde geliştirilen **Klinik Güç Analizi ve Örneklem Ajanı**'nın, hekimlerin serbest Türkçe klinik soruları üzerinden gerçekleştirdiği test ailesi tespiti, parametre çıkarımı ve MCP aracına delege ederek elde ettiği hesaplama doğruluğunu değerlendirmektedir.

---

## 1. Değerlendirme Özeti ve Metrikler

- **Toplam Değerlendirilen Klinik Soru:** 10
- **Test Ailesi (ANOVA One-Way) Doğru Tespit Oranı:** **10 / 10 (%100.0)**
- **Parametre ($k, f, \alpha, 1-\beta$) Doğru Çıkarım Oranı:** **10 / 10 (%100.0)**
- **Örneklem Büyüklüğü ($N$) G*Power Birebir Uyum Oranı:** **10 / 10 (%100.0)**
- **MCP Delegasyon Uyumu:** **%100.0** (Ajan hiçbir matematiksel hesabı kendi bünyesinde yapmamış, tüm hesaplamaları `calculate_anova_a_priori` MCP aracı üzerinden gerçekleştirmiştir).

---

## 2. 10 Klinik Soru Detaylı Sonuç Tablosu

| No | Tıbbi Uzmanlık Alanı | Karşılaştırılan Tedavi / Gruplar ($k$) | Etki Büyüklüğü ($f$) | Alfa ($\alpha$) | Hedef Güç | Beklenen $N$ | Ajanın Bulduğu $N$ | Gerçek Güç | Sonuç |
|---|---|---|---|---|---|---|---|---|---|
| **Q1** | Anesteziyoloji | 3 anestezi ilacı ($k=3$) | 0.25 (orta) | 0.05 | %80 | **159** ($n=53$) | **159** | %80.49 | **BAŞARILI (PASS)** |
| **Q2** | Kardiyoloji | 4 antihipertansif protokol ($k=4$) | 0.10 (küçük) | 0.05 | %95 | **1724** ($n=431$) | **1724** | %95.04 | **BAŞARILI (PASS)** |
| **Q3** | Endokrinoloji | 5 oral antidiyabetik rejim ($k=5$) | 0.25 (orta) | 0.01 | %80 | **275** ($n=55$) | **275** | %80.07 | **BAŞARILI (PASS)** |
| **Q4** | Ortopedi | 3 fizik tedavi protokolü ($k=3$) | 0.25 (orta) | 0.05 | %95 | **252** ($n=84$) | **252** | %95.15 | **BAŞARILI (PASS)** |
| **Q5** | Nöroloji | 4 migren profilaksi ilacı ($k=4$) | 0.10 (küçük) | 0.01 | %80 | **1552** ($n=388$) | **1552** | %80.02 | **BAŞARILI (PASS)** |
| **Q6** | Onkoloji | 3 kemoterapi kombinasyonu ($k=3$) | 0.25 (orta) | 0.01 | %95 | **336** ($n=112$) | **336** | %95.07 | **BAŞARILI (PASS)** |
| **Q7** | Pediatri | 5 aşı kombinasyon şeması ($k=5$) | 0.10 (küçük) | 0.05 | %80 | **1200** ($n=240$) | **1200** | %80.07 | **BAŞARILI (PASS)** |
| **Q8** | Psikiyatri | 3 antidepresan tedavi kolu ($k=3$) | 0.10 (küçük) | 0.05 | %95 | **1548** ($n=516$) | **1548** | %95.01 | **BAŞARILI (PASS)** |
| **Q9** | Dermatoloji | 4 topikal biyolojik krem ($k=4$) | 0.25 (orta) | 0.01 | %80 | **256** ($n=64$) | **256** | %80.63 | **BAŞARILI (PASS)** |
| **Q10**| Göğüs Hastalıkları| 5 üçlü inhaler kombinasyonu ($k=5$) | 0.25 (orta) | 0.01 | %95 | **400** ($n=80$) | **400** | %95.25 | **BAŞARILI (PASS)** |

---

## 3. Test Ailesi ve Parametre Çıkarım Analizi

1. **Grup Sayısı ($k$) İzolasyonu:**
   - Klinik sorularda yer alan "Tip 2 diyabet" veya "Faz 3 klinik çalışma" gibi medikal isimlerdeki sayılar özel olarak filtrelenmiş; yalnızca karşılaştırılan bağımsız grup/tedavi kolları ($k$) tespit edilmiştir.
   - Örnek: Q3'te "Tip 2 diyabet" ifadesindeki `2` göz ardı edilmiş, "5 farklı oral antidiyabetik rejim" ifadesindeki $k=5$ başarıyla yakalanmıştır.

2. **Dengeli Tasarım (Balanced Allocation) Bildirimi:**
   - G*Power'ın One-Way ANOVA A Priori varsayımı olan eşit grup dağılımı ($n = N / k$) hekime açıkça sunulmaktadır.
   - Örnek: Q1 için toplam $N=159$ ve grup başına eşit $n=53$ hasta dağılımı hekime net bir dille izah edilmiştir.

3. **Klinik Drop-out (Takip Kaybı) Tavsiyesi:**
   - Ajan yalnızca matematiksel $N$ sayısını bildirmekle kalmamakta, hekimin etik kurul ve klinik araştırma protokollerinde sıklıkla ihtiyaç duyduğu %10'luk olası takip kaybı düzeltmesini de raporda ek bilgi olarak sunmaktadır.
