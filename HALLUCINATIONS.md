# Ajanın Süreç İçi Yanılgıları ve Testlerle Düzeltilmesi (HALLUCINATIONS.md)

Bu dökümanda, tersine mühendislik ve temiz oda (clean-room) geliştirme sürecinde ajanın başlangıçta yaptığı/yapabileceği hatalı varsayımlar (halüsinasyonlar), bunların istatistiksel ve ikili analiz düzeyindeki gerçekleri ve diferansiyel testlerle nasıl yakalanıp düzeltildiği açıklanmaktadır.

---

## 1. Yanılgı 1: Örneklem Büyüklüğü $N$'nin Serbest Bir Tam Sayı Olarak Aranması

### Hatalı Çıkarım (Halüsinasyon):
A priori örneklem hesaplamasında, $P(F > F_{crit}) \ge \text{target\_power}$ şartını sağlayan toplam örneklem büyüklüğü $N$'nin herhangi bir tamsayı ($N \in \{k+1, k+2, \dots\}$) olabileceği ve sürekli kök bulucu algoritmanın (root solver) bulduğu $N_{cont}$ değerinin basitçe $\lceil N_{cont} \rceil$ şeklinde yukarı yuvarlanmasının yeterli olacağı varsayılmıştır.

### Nasıl Yakalandı?
- `oracle/vectors.csv` dosyasındaki ilk test vektörü çalıştırıldığında ($f = 0.10, \alpha = 0.01, \text{power} = 0.80, k = 3$):
  - Sürekli çözücü $N \approx 1392.4$ değerini üretmekte ve basit tavan yuvarlama $N = 1393$ sonucunu vermektedir.
  - Ancak G*Power oracle çıktısında `n_total = 1395` olarak kaydedilmiştir.
- `tests/test_differential.py` diferansiyel testi çalıştırıldığında $1393 \ne 1395$ hatası alınmış ve $N$ değerinde %100 eşleşme kuralı ihlal edilmiştir.

### İkili Analizi (Reverse Engineering) ile Doğrulama:
`GPowerNT.exe` üzerinde yapılan Capstone disassembler analizinde, `VA: 0x004BADB0` adresindeki `PowerFAnovaGlobal::AdjustSampleSize` metodunun şu kodu icra ettiği tespit edilmiştir:
```assembly
0x004BADC9: divsd xmm0, qword ptr [esp + 0xc]   ; xmm0 = N_cont / k (grup başına düşen n)
0x004BADDc: call  0x005AC047                    ; CRT ceil(n)
0x004BADE1: fmul  qword ptr [esi + 0xf0]        ; ST(0) = ceil(N_cont / k) * k
```
G*Power, omnibus ANOVA'da eşit grup dağılımı (balanced design, $n_1 = n_2 = \dots = n_k$) zorunlu kıldığından, $N$ değeri kesinlikle grup sayısı $k$'nın bir tam katı ($N = n_{group} \times k$) olmak zorundadır. $1392.4 / 3 = 464.13 \rightarrow \lceil 464.13 \rceil = 465 \rightarrow 465 \times 3 = 1395$ olarak düzeltilmiş ve testler %100 yeşile dönmüştür.

---

## 2. Yanılgı 2: F-Testinde İki Yönlü (Two-Tailed) Analiz ve $\alpha / 2$ Bölünmesi İhtimali

### Hatalı Çıkarım (Halüsinasyon):
İki ortalama farkı test eden Student t-testlerinde yaygın olarak kullanılan çift kuyruk (two-tailed) hipotez mantığının, ANOVA F-testi için de geçerli olabileceği ve kullanıcı yön belirtmediğinde $\alpha$'nın ikiye bölünmesi ($\alpha / 2$) veya F dağılımının sol kuyruğunun da ret bölgesine dahil edilmesi gerektiği yanılgısına düşülmüştür.

### Nasıl Yakalandı?
- Eğer F dağılımı iki yönlü varsayılsaydı, kritik F değeri $F_{crit} = \text{ppf}_F(1 - \alpha/2, df_1, df_2)$ olarak hesaplanacak ve Row 2 için kritik F değeri $4.6204392$ yerine yaklaşık $5.30$ çıkacaktı.
- Diferansiyel test suite'imiz (`test_valid_vector_differential`) kritik F ve gerçek güç değerlerini $10^{-4}$ toleransla karşılaştırdığında bu hipotez anında elenmiştir.

### İstatistiksel Doğrulama:
Tek Yönlü ANOVA omnibus testi, varyans oranına ($F = MS_{between} / MS_{error}$) dayanır. Kareler toplamının oranı her zaman pozitif olduğundan ve alternatif hipotez ($H_1: \text{en az bir grup ortalaması farklıdır}$) $F$ istatistiğini yalnızca sağa doğru büyüttüğünden, F-testi matematiksel olarak her zaman tek yönlü (sağ kuyruk) testtir. Güç formülü kesin olarak $1 - \text{cdf}_{ncF}(F_{crit})$ veya $\text{sf}_{ncF}(F_{crit})$ olarak sabitlenmiştir.

---

## 3. Yanılgı 3: Girdi Aralık Sınırlarının Kapalı Aralık $[0, 1]$ veya $[0, 50]$ Kabul Edilmesi

### Hatalı Çıkarım (Halüsinasyon):
Alfa ve güç değerlerinin teorik olasılık uzayı $[0, 1]$ olduğundan, $\alpha = 1.0$ veya $\text{power} = 1.0$ ya da etki büyüklüğü $f = 0.0$ girdilerinin kabul edilip sıfır örneklem veya sonsuz güç dönüleceği varsayılmıştır.

### Nasıl Yakalandı?
- `oracle/vectors.csv` satır 27-31'deki negatif sınır durumları çalıştırıldığında:
  - $f = 0.0 \rightarrow$ G*Power hata verdi: `ERROR: Effect size f is outside the admissible range (1e-06; 50).`
  - $\alpha = 1.0 \rightarrow$ G*Power hata verdi: `ERROR: Alpha is outside the admissible range (1e-07; 1).`
  - $\text{power} = 1.0 \rightarrow$ G*Power hata verdi: `ERROR: Power is outside the admissible range (1e-07; 1).`
  - $k = 1 \rightarrow$ G*Power hata verdi: `ERROR: There must be at least 2 groups.`
- Bu hata mesajları `GPowerNT.exe` içerisindeki string tabloları (`0x005C6000` bölgesi) ve doğrulama rutinleri (`0x00487CB0` vb.) ile %100 uyumlu hale getirilmiş ve tüm hata testleri başarıyla geçirilmiştir.
