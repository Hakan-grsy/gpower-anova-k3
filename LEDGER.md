# G*Power ANOVA Tersine Mühendislik Defteri (LEDGER.md)

Bu defter, G*Power 3.1.9.7 yazılımındaki **"F tests -> ANOVA: Fixed effects, omnibus, one-way"** (Tek Yönlü ANOVA) test motorunun temiz oda (clean-room) prensipleriyle yeniden üretilmesi amacıyla yapılan dokümantasyon, ikili analizi (reverse engineering) ve çıkarım kayıtlarını içerir.

---

## 1. Dokümantasyon ve İstatistiksel Temeller [DOK]

Kaynaklar:
- Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). *G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences*. Behavior Research Methods, 39(2), 175–191.
- Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). *Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses*. Behavior Research Methods, 41(4), 1149–1160.
- G*Power 3.1 Manueli (ANOVA Modeli İncelemesi).

### 1.1 Serbestlik Dereceleri (Degrees of Freedom)
Tek Yönlü Varyans Analizinde (One-Way ANOVA Omnibus Testi), $k$ adet bağımsız grup ve toplam $N$ katılımcı/gözlem sayısı için:
- **Pay (Numerator) Serbestlik Derecesi ($df_1$):**
  $$df_1 = k - 1$$
- **Payda (Denominator / Error) Serbestlik Derecesi ($df_2$):**
  $$df_2 = N - k$$
  Burada geçerli bir hata varyansı hesaplanabilmesi için $df_2 > 0$ olmalıdır ($N > k$, dengeli tasarımda grup başına minimum 2 gözlem: $N \ge 2k$).

### 1.2 Noncentrality Parametresi (NCP - $\lambda$)
Merkezi olmayan (noncentral) F dağılımının kayma/konum parametresi $\lambda$:
$$\lambda = f^2 \times N$$
Burada:
- $f$: Cohen'in etki büyüklüğü ($f = \frac{\sigma_m}{\sigma}$, popülasyon standart sapmasına oranlanan grup ortalamalarının standart sapması).
- $N$: Toplam örneklem büyüklüğü ($N = \sum_{i=1}^k n_i$).

### 1.3 Kritik Değer ($F_{crit}$) ve Güç ($1 - \beta$)
- **Kritik F Değeri ($F_{crit}$):**
  Sıfır hipotezi ($H_0$) altındaki merkezi $F(df_1, df_2)$ dağılımının $(1 - \alpha)$ yüzdelik dilimidir:
  $$F_{crit} = F^{-1}(1 - \alpha; df_1, df_2) = \text{ppf}_{F}(1 - \alpha, df_1, df_2)$$
- **İstatistiksel Güç (Power, $1 - \beta$):**
  Alternatif hipotez ($H_1$) altındaki merkezi olmayan $F(df_1, df_2, \lambda)$ dağılımında $F_{crit}$ değerinin üzerindeki kuyruk alanıdır (Survival Function / Complementary CDF):
  $$\text{Actual Power} = P(F > F_{crit} \mid df_1, df_2, \lambda) = 1 - \text{cdf}_{ncF}(F_{crit}, df_1, df_2, \lambda) = \text{sf}_{ncF}(F_{crit}, df_1, df_2, \lambda)$$

---

## 2. İkili Analizi ve Tersine Mühendislik Bulguları [REA]

Analiz Edilen Dosya: `GPowerNT.exe`
- **Dosya Yolu:** `GPower_3.1.9.7_143/GPowerNT.exe`
- **SHA-256 Karması:** `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812`
- **Mimari:** PE32, Intel 32-bit x86 (`Machine: 0x14c`, `ImageBase: 0x00400000`)
- **Kullanılan Araçlar:** `npx rea-agents@6.7.0`, Capstone x86 Disassembler, PE analiz araçları.

### 2.1 PE Kesitleri (Sections) ve Bellek Haritası
| Kesit Adı | Sanal Adres (VA) | Sanal Boyut | Dosya Offseti | Ham Boyut | İçerik |
|---|---|---|---|---|---|
| `.text` | `0x00401000` | `0x1BCA07` | `0x00000400` | `0x001BCA07` | Makine kodları, F-test hesaplama rutinleri |
| `.rdata` | `0x005BE000` | `0x049A6E` | `0x001BD000` | `0x00049A6E` | Vtable tabloları, RTTI tanımları, sabit stringler, IAT |
| `.data` | `0x00608000` | `0x0818C8` | `0x00206C00` | `0x000818C8` | Global değişkenler, RTTI TypeDescriptor nesneleri |
| `.rsrc` | `0x0068A000` | `0x0211D0` | `0x0020D600` | `0x000211D0` | UI Dialog ve Resource verileri |

### 2.2 Sınıf Hiyerarşisi, RTTI ve Vtable Adresleri
G*Power, C++ nesne yönelimli mimarisinde ANOVA için `PowerFAnovaGlobal` sınıfını kullanmaktadır:
- **`PowerFAnovaGlobal` RTTI TypeDescriptor:** `VA: 0x0060CB70` (Mangled Name: `.?AVPowerFAnovaGlobal@@` offset `0x0060CB7C`)
- **RTTI Complete Object Locator:** `VA: 0x005EEEAC`
- **Vtable (Sanal Fonksiyon Tablosu):** `VA: 0x005C8538` (Dosya offseti: `0x001C7538`)

Vtable içindeki kritik sanal fonksiyon indeksleri:
- `vfunc[0]  (VA: 0x004981C0)`: Temel ilklendirme ve nesne yıkıcı
- `vfunc[1]  (VA: 0x00496830)`: A priori optimizasyon ve arama döngüsü yürütücüsü
- `vfunc[12] (VA: 0x004B8D50)`: `PowerFAnovaGlobal::CalculateParameters` (df1, df2, NCP, kritik F ve güç hesaplama parametrelerini dolduran metod)
- `vfunc[13] (VA: 0x004B8E40)`: Dispatcher / Değerlendirme çağrısı
- `vfunc[29] (VA: 0x004BADB0)`: `PowerFAnovaGlobal::AdjustSampleSize` (Grup boyutu dengeleme ve tavan yuvarlama metodu)

### 2.3 Girdi Doğrulama ve Hata Dizesi Referansları
Doğrulama fonksiyonları `.text` içerisinde `0x00487400` - `0x00488500` adres aralığında yer alır:
1. **Grup Sayısı ($k$) Kontrolü:**
   - Fonksiyon: `VA: 0x00487CB0`
   - Hata Dizesi: `"There must be at least 2 groups."` (`VA: 0x005C6594`, Dosya offseti `0x001C5594`)
   - Disassembly:
     ```assembly
     0x00487CB0: cmp  dword ptr [esp + 4], 2
     0x00487CB5: jl   0x00487CBC
     0x00487CB7: mov  al, 1
     0x00487CB9: ret  4
     0x00487CBC: lea  eax, [ecx + 0x2b0]
     0x00487CC2: push 0x005C6594           ; "There must be at least 2 groups."
     0x00487CC7: push eax
     0x00487CC8: call 0x00437DB0           ; Hata raporlama rutini
     0x00487CCD: add  esp, 8
     0x00487CD0: xor  al, al
     0x00487CD2: ret  4
     ```
2. **Etki Büyüklüğü ($f$) Kontrolü:**
   - Hata Dizesi: `"Effect size f is outside the admissible range (1e-06; 50)."` (`VA: 0x005C66BC`)
   - Doğrulama Aralığı: $10^{-6} < f < 50$ (açık aralık).
   - Xref: `VA: 0x00487665`, `VA: 0x0048776D`.
3. **Alfa ($\alpha$) Kontrolü:**
   - Hata Dizesi: `"Alpha is outside the admissible range (1e-07; 1)."` (`VA: 0x005C6100`)
   - Doğrulama Aralığı: $10^{-7} < \alpha < 1$ (açık aralık).
   - Xref: `VA: 0x004874ED`, `VA: 0x004875B5`.
4. **Güç ($1 - \beta$) Kontrolü:**
   - Hata Dizesi: `"Power is outside the admissible range (1e-07; 1)."` (`VA: 0x005C60D8`)
   - Doğrulama Aralığı: $10^{-7} < \text{power} < 1$ (açık aralık).
   - Xref: `VA: 0x0048809D`, `VA: 0x00488195`.
5. **Test Seçimi ve Arayüz Dizesi:**
   - String: `"ANOVA: Fixed effects, omnibus, one-way"` (`VA: 0x005C9AE4`, Dosya offseti `0x001C8AE4`)
   - Xref: `VA: 0x004BA58D`.

### 2.4 A Priori $N$ Arama Döngüsü ve Ceil Yuvarlama Mekanizması
G*Power omnibus ANOVA testinde eşit grup dağılımı ($n_1 = n_2 = \dots = n_k$) varsayılır. Bu nedenle toplam örneklem boyutu $N$, kesinlikle grup sayısı $k$'nın tam katı olmak zorundadır.

Tersine mühendislikle ortaya çıkarılan `VA: 0x004BADB0` yordamı incelendiğinde:
```assembly
; Girdi: esp+0xC = sürekli sayısal çözücüden (0x004F9BB0) dönen yaklaşık örneklem büyüklüğü N_cont
;        [esi + 0xF0] = grup sayısı k
0x004BADB0: sub   esp, 8
0x004BADB3: movsd xmm0, qword ptr [esp + 0xc]   ; xmm0 = N_cont
0x004BADB9: push  esi
0x004BADBA: mov   esi, ecx
0x004BADBC: sub   esp, 8
0x004BADBF: fld   qword ptr [esi + 0xf0]        ; ST(0) = k
0x004BADC5: fstp  qword ptr [esp + 0xc]         ; Stack'e k yaz
0x004BADC9: divsd xmm0, qword ptr [esp + 0xc]   ; xmm0 = N_cont / k (grup başına düşen sürekli n)
0x004BADCF: movsd qword ptr [esp + 0x18], xmm0
0x004BADD5: fld   qword ptr [esp + 0x18]        ; FPU'ya yükle
0x004BADD9: fstp  qword ptr [esp]               ; CRT ceil için parametre
0x004BADDc: call  0x005AC047                    ; CALL CRT ceil() [IAT: 0x005BE590]
0x004BADE1: fmul  qword ptr [esi + 0xf0]        ; ST(0) = ceil(N_cont / k) * k
0x004BADE7: add   esp, 8
0x004BADEA: pop   esi
0x004BADEB: add   esp, 8
0x004BADEE: ret   8
```
Bu rutin matematiksel olarak şu adımı icra eder:
$$n_{\text{per\_group}} = \lceil N_{\text{cont}} / k \rceil$$
$$N_{\text{total}} = n_{\text{per\_group}} \times k$$
Ayrıca geçerli bir model için grup başına en az 2 gözlem ($n_{\text{per\_group}} \ge 2$) olması gerektiğinden $N_{\text{total}} \ge 2k$'dır.

---

## 3. Ajanın Çıkarımları ve Temiz Oda Tasarım Notları [AJAN]

1. **A-priori $N$ Çözümü (İteratif Arama):**
   - Hedef gücü ($\text{target\_power}$) sağlayan en küçük örneklem büyüklüğü, $n_{\text{group}} \ge 2$ tam sayısı üzerinden aranır.
   - Her aday $n_{\text{group}}$ için:
     - $N = n_{\text{group}} \times k$
     - $df_1 = k - 1$
     - $df_2 = N - k$
     - $\lambda = f^2 \times N$
     - $F_{crit} = \text{ppf}_{F}(1 - \alpha, df_1, df_2)$
     - $\text{actual\_power} = \text{sf}_{ncF}(F_{crit}, df_1, df_2, \lambda)$
   - $\text{actual\_power} \ge \text{target\_power}$ şartını sağlayan ilk $n_{\text{group}}$ tam sayısında durulur ve $N_{\text{total}} = n_{\text{group}} \times k$ belirlenir.
   - Arama performansı için üst sınır üssel olarak genişletilip ardından ikili arama (binary search) ile $O(\log M)$ sürede kesin minimum bulunur.

2. **Sayısal Hassasiyet ve scipy.stats Uyum:**
   - G*Power'ın kullandığı AS 243 / Ding F dağılımı integrasyonu ile `scipy.stats.ncf.sf` (veya `1 - ncf.cdf`) $10^{-7}$ hassasiyetle birebir örtüşmektedir.
   - Kritik F değeri `scipy.stats.f.ppf(1 - alpha, df1, df2)` ile 7 ondalık basamakta tam olarak eşleşmektedir.

3. **CLI Sözleşmesi ve Hata Yönetimi:**
   - Girdi parametreleri: `--test anova-oneway --mode <a-priori|post-hoc> --f <float> --alpha <float> --power <float> --num-groups <int> [--n <int>]`
   - Geçerli durumlarda stdout'a tek satır JSON basılmalı ve exit code 0 dönmelidir:
     `{"n_total": 1395, "actual_power": 0.8008513, "critical": 4.6204392, "df1": 2, "df2": 1392, "ncp": 13.95}`
   - Geçersiz parametrelerde (örn. $k < 2$, $\alpha \notin (1e-7; 1)$, $f \notin (1e-6; 50)$ veya $N < 2k$) stdout veya stderr'e `{"error":"<açıklama>"}` JSON'ı basılmalı ve 0'dan farklı exit code (örn. 1) ile sonlanmalıdır.
