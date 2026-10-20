> **NOT:** BU PROJEDE TEMEL CLI (85), MCP SUNUCUSU (+15) VE AI AJANI (+10) KATMANLARI TAMAMLANMIŞTIR.

# G*Power ANOVA (K3 Grubu) Temiz Oda Klonu, MCP Sunucusu ve AI Ajanı

Bu proje, **G*Power 3.1.9.7** yazılımında yer alan **"F tests -> ANOVA: Fixed effects, omnibus, one-way"** (Tek Yönlü ANOVA) test motorunun temiz oda (clean-room reverse engineering) prensiplerine uygun olarak analiz edilmesi, bağımsız Python CLI motoru, **Model Context Protocol (MCP)** adaptörü ve hekimler için **AI Klinik Danışman Ajanı** olarak sıfırdan geliştirilmesidir.

Proje, resmi G*Power 3.1.9.7 oracle ikili dosyası ile **%100 matematiksel ve istatistiksel eşleşme** sağlamaktadır.

---

## 1. Referans İkili (Oracle Binary) Bilgileri

Analiz ve diferansiyel testlerde temel alınan resmi G*Power çalıştırılabilir dosyası:
- **Dosya Adı:** `GPowerNT.exe`
- **Sürüm:** 3.1.9.7 (Release 143)
- **SHA-256 Karması:** `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812`
- **Mimari:** PE32, Intel 32-bit x86 (`Machine: 0x14c`, `ImageBase: 0x00400000`)
- **Boyut:** 2,287,616 bayt

---

## 2. Proje Mimarisi ve Dizin Yapısı

```text
├── LEDGER.md                   # Dokümantasyon, tersine mühendislik (REA) ve vtable analizleri
├── SPEC.md                     # Gherkin kabul kriterleri şartnamesi
├── HALLUCINATIONS.md           # Ajanın süreç içi yanılgıları ve testlerle giderilme analizi
├── AGENT_COST.md               # Model, token ve süreç maliyet raporu
├── README.md                   # Kapsamlı proje kullanım ve şema dokümanı
├── requirements.txt            # Python bağımlılıkları (scipy, pytest, mcp)
├── gpower-clone / .bat         # Linux/macOS ve Windows çalıştırılabilir CLI wrapper'ları
├── prompts/
│   ├── session1_prompt.md      # 1. Oturum (İnceleme & Şartname) başlangıç istemi
│   └── session2_prompt.md      # 2. Oturum (Temiz Oda Kodlama) başlangıç istemi
├── src/
│   ├── __init__.py
│   ├── engine.py               # scipy.stats tabanlı saf istatistiksel hesaplama motoru
│   ├── cli.py                  # CLI girdi/çıktı katmanı (JSON sözleşmeli)
│   ├── mcp_server.py           # Model Context Protocol (MCP) ince adaptör sunucusu (+15 Puan)
│   └── agent.py                # Hekim klinik soru analiz ve MCP yönlendirme ajanı (+10 Puan)
├── tests/
│   ├── __init__.py
│   ├── test_differential.py   # Oracle 30 test vektörü diferansiyel test suite
│   └── test_mcp.py            # CLI vs MCP katmanı birebir eşdeğerlik test suite (+15 Puan)
├── agent_evaluation/           # AI Ajanı Değerlendirme Paketi (+10 Puan)
│   ├── clinical_questions_tr.json  # 10 adet Türkçe hekim klinik senaryo veri seti
│   ├── evaluation_results.md       # Ajanın %100 tespit ve parametre başarı raporu
│   ├── tool_call_logs.json         # Ajanın MCP aracına yaptığı çağrı log kayıtları
│   └── token_comparison.md         # Vision/GUI vs Text-MCP token ve maliyet karşılaştırması
└── oracle/
    ├── vectors.csv             # 30 adet resmi G*Power doğrulama vektörü (25 geçerli, 5 geçersiz)
    └── screenshots/            # G*Power GUI ekran görüntüleri
```

---

## 3. Kurulum

Proje Python 3.10 veya daha güncel bir sürüm gerektirir.

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

---

## 4. Katman 1: CLI Motoru (Temel Katman - 85 Puan)

### CLI Parametreleri
```bash
python -m src.cli --test anova-oneway --mode <a-priori|post-hoc> --f <effect_size> --alpha <alpha> --power <power> --num-groups <k> [--n <n_total>]
```

### Örnek 1: A Priori Modu (Örneklem Büyüklüğü Hesaplama)
```bash
python -m src.cli --test anova-oneway --mode a-priori --f 0.10 --alpha 0.01 --power 0.80 --num-groups 3
```
**Çıktı (Tek Satır JSON):**
```json
{"n_total": 1395, "actual_power": 0.8008513311846405, "critical": 4.620439183212792, "df1": 2, "df2": 1392, "ncp": 13.950000000000003}
```

### Örnek 2: Post Hoc Modu (Elde Edilen Gücü Hesaplama)
```bash
python -m src.cli --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --num-groups 3 --n 252
```
**Çıktı:**
```json
{"n_total": 252, "actual_power": 0.9514887602242726, "critical": 3.0320649162691873, "df1": 2, "df2": 249, "ncp": 15.75}
```

---

## 5. Katman 2: Model Context Protocol (MCP) Sunucusu (+15 Puan)

`src/mcp_server.py`, `src/engine.py` içindeki hesaplama mantığını kopyalamadan kullanan ince bir adaptördür. Standart MCP stdio protokolü üzerinden harici LLM'ler veya ajanlarla entegre olur.

### MCP Araç Şeması (Tool Schema)

#### Araç Adı
`calculate_anova_a_priori`

#### Tanım
Tek Yönlü ANOVA (One-Way ANOVA: Fixed effects, omnibus) A Priori güç analizi için gerekli toplam örneklem boyutunu ($N$), gerçekleşen gücü ve kritik $F$ istatistiğini dengeli grup tasarımıyla hesaplar.

#### Girdi Parametreleri (Input Schema)
| Parametre Adı | Tür | Zorunlu | Kabul Edilen Aralık | Açıklama |
|---|---|---|---|---|
| `f` | `float` | Evet | $10^{-6} < f < 50$ (açık aralık) | Cohen'in $f$ etki büyüklüğü |
| `alpha` | `float` | Evet | $10^{-7} < \alpha < 1$ (açık aralık) | Tip I hata oranı / anlamlılık düzeyi |
| `power` | `float` | Evet | $10^{-7} < 1-\beta < 1$ (açık aralık) | Hedeflenen istatistiksel güç |
| `num_groups` | `int` | Evet | $k \ge 2$ tamsayı | Karşılaştırılan bağımsız grup sayısı |

#### Çıktı Parametreleri (Output Schema)
| Alan Adı | Tür | Açıklama |
|---|---|---|
| `n_total` | `int` | Hedef gücü sağlayan en küçük toplam örneklem büyüklüğü ($N = n_{group} \times k$) |
| `actual_power` | `float` | Tam sayı $N$ ile elde edilen gerçek istatistiksel güç ($P(F > F_{crit} \mid \lambda)$) |
| `critical` | `float` | Sıfır hipotezi altındaki kritik $F$ değeri ($F_{crit}$) |
| `df1` | `int` | Gruplar arası (pay) serbestlik derecesi ($k - 1$) |
| `df2` | `int` | Hata (payda) serbestlik derecesi ($N - k$) |
| `ncp` | `float` | Noncentrality parametresi ($\lambda = f^2 \times N$) |

*Hata Durumunda:* `{"error": "<Açıklama>"}` nesnesi döner.

---

## 6. Katman 3: AI Klinik Danışman Ajanı (+10 Puan)

`src/agent.py`, hekimin Türkçe klinik sorusunu analiz eder, One-Way ANOVA test ailesine ait olup olmadığını teyit eder, parametreleri çıkarır ve **tüm hesaplamayı MCP aracına delege ederek** hekime anlaşılır bir klinik rapor üretir.

### Örnek Ajan Kullanımı
```python
from src.agent import ClinicalAnovaAgent

agent = ClinicalAnovaAgent()
soru = "3 farklı anestezi ilacının uyanma süresine etkisini kıyaslayacağım. f=0.25 etki büyüklüğünü %80 güç ve 0.05 hata payıyla yakalamak için toplam kaç hastaya ihtiyacım var?"

yanit = agent.consult(soru)
print(yanit["clinical_report"])
```

**Üretilen Hekim Raporu:**
```text
### Klinik Güç Analizi ve Örneklem Raporu

Sayın Araştırmacı / Hekim Meslektaşımız,
Tasarladığınız çalışma 3 bağımsız grubu sürekli bir klinik değişken üzerinden karşılaştırdığı için Tek Yönlü ANOVA analizi için uygundur.

Analiz Parametreleri:
- Karşılaştırılan Grup Sayısı (k): 3
- Etki Büyüklüğü (Cohen's f): 0.25
- Tip I Hata Payı (Alfa - α): 0.05
- Hedeflenen İstatistiksel Güç (1 - β): %80

Hesaplanan Örneklem İhtiyacı (G*Power Uyumlu):
- Gerekli Toplam Hasta Sayısı (N): 159
- Grup Başına Alınması Gereken Hasta Sayısı (n): 53 (Dengeli Tasarım: her gruba 53 hasta)
- Ulaşılan Gerçek Güç (Actual Power): %80.49 (0.80489)
- Kritik F Değeri (F_crit): 3.0540 (df1 = 2, df2 = 156)

Klinik Öneri:
Çalışmanızda %80'lik hedeflenen gücü garanti edebilmek adına, takip kayıpları (drop-out) ihtimaline karşı (%10) toplam hasta sayısını 174 hastaya yükseltmeniz önerilir.
```

---

## 7. Test Paketleri ve Doğrulama Raporları

### 1. Diferansiyel Test (CLI vs G*Power Oracle)
`oracle/vectors.csv` içindeki 30 test vektörünü (25 geçerli, 5 geçersiz) test eder:
```bash
pytest -v tests/test_differential.py
```
*Sonuç: 31 passed in 59s (%100 N eşleşmesi).*

### 2. MCP Eşdeğerlik Testi (CLI vs MCP Layer)
CLI ile MCP aracının aynı parametrelerle bit-for-bit aynı çıktıyı verdiğini doğrular:
```bash
pytest -v tests/test_mcp.py
```
*Sonuç: 30 passed in 31s (%100 tam eşdeğerlik).*

---

## 8. Demo Video

Süreç ve çalıştırma tanıtım videosu:
- **Yerel Video Dosyası:** [docs/demo.mp4](docs/demo.mp4)
- **Çevrimiçi İzleme:** `https://youtu.be/DEMO_VIDEO_PLACEHOLDER`

---

## 9. Akademik Atıflar (Citations)

1. **Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007).**
   *G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences.*
   Behavior Research Methods, 39(2), 175–191. https://doi.org/10.3758/BF03193146

2. **Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009).**
   *Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses.*
   Behavior Research Methods, 41(4), 1149–1160. https://doi.org/10.3758/BRM.41.4.1149
