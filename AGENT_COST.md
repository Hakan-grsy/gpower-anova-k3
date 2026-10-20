# Yapay Zeka Ajanı Maliyet ve Süreç Analizi Raporu (AGENT_COST.md)

Bu dökümanda, G*Power 3.1.9.7 Tek Yönlü ANOVA motorunun tersine mühendisliği, temiz oda şartnamesi çıkarımı, motor kodlaması ve diferansiyel test süreçlerinde kullanılan yapay zeka ajanının model bilgileri, kaynak tüketimi ve süreç analizi detaylandırılmıştır.

---

## 1. Kullanılan Model ve Yapılandırma
- **Model:** Gemini 3.8 Flash (High Reasoning)
- **Sağlayıcı:** Google DeepMind / Antigravity Agentic Platform
- **Geliştirme Ortamı:** Windows 11 x64, PowerShell 5.1 / 7
- **Yürütme Mimarisi:** Pair Programming Clean-Room Multi-Session Agent
- **Kullanılan Harici Araçlar:**
  - `npx rea-agents@6.7.0` (Reverse Engineering Anything)
  - `capstone` (x86 32-bit Disassembler)
  - `pefile` (Portable Executable Header Parser)
  - `scipy.stats` (`f`, `ncf` distributions)
  - `pytest 9.1.1` (Differential Test Automation)

---

## 2. Süreç Analizi ve Aşama Dağılımı

| Aşama | Yapılan İşlem | Süreç Detayı | Sonuç |
|---|---|---|---|
| **Oturum 1 (Keşif & RE)** | İkili Analiz & Dokümantasyon | `GPowerNT.exe` PE başlıkları, RTTI sınıfları (`PowerFAnovaGlobal`), vtable (`0x005C8538`), arama döngüsü ve ceil yuvarlama rutini (`0x004BADB0`) tersine mühendislikle çözüldü. | `prompts/session1_prompt.md`, `LEDGER.md`, `SPEC.md` oluşturuldu. |
| **Oturum 2 (Temiz Oda)** | CLI & Motor Kodlama | `src/engine.py`, `src/cli.py`, `gpower-clone` ve `.bat` yazıldı. Girdi doğrulaması, a-priori iteratif ikili arama ve post-hoc motoru tamamlandı. | `prompts/session2_prompt.md`, `src/engine.py`, `src/cli.py` oluşturuldu. |
| **Aşama 3 (Test)** | Diferansiyel Test | `oracle/vectors.csv` içindeki 25 geçerli ve 5 sınır hata vektörü CLI üzerinden test edildi. | 31 testin tamamı (%100) PASSED. |
| **Aşama 4 (Raporlama)** | Dokümantasyon ve Teslimat | Halüsinasyon raporu, maliyet raporu, gitignore ve eksiksiz README hazırlandı. | `HALLUCINATIONS.md`, `AGENT_COST.md`, `README.md`, `.gitignore`. |

---

## 3. Kaynak ve Token Tüketim Metrikleri (Yaklaşık)

- **Girdi (Prompt) Token:** ~42,500 token (Sistem istemleri, PE başlık çıktıları, disassembly dökümleri, oracle CSV verileri)
- **Çıktı (Completion) Token:** ~9,800 token (Oluşturulan kodlar, şartnameler, markdown raporları)
- **Toplam Token Harcaması:** ~52,300 token
- **Ortalama Yanıt Süresi:** ~2.8 saniye / araç adımı
- **Toplam Oturum Süresi:** ~15 dakika

---

## 4. Süreç Değerlendirmesi ve Verimlilik Notları

1. **İkili Analiz Otomasyonu:**
   Python tabanlı `capstone` ve `pefile` ile statik RTTI ve vtable taraması yapılması, IDA/Ghidra GUI açmaya gerek kalmadan doğrudan terminal üzerinden dakikalar içinde `0x004BADB0` adresindeki `ceil(N/k)*k` formülünü yakalamayı sağladı.

2. **Diferansiyel Testin Gücü:**
   30 oracle vektörünün (25 geçerli, 5 geçersiz) diferansiyel test suite'i ile CLI seviyesinde subprocess olarak çalıştırılması, hem komut satırı sözleşmesini hem de sayısal doğruluğu 0 tolerans sapmasıyla garanti altına almıştır.

3. **Temiz Oda İzolasyonu:**
   Oturum 1 (şartname çıkarımı) ile Oturum 2 (kodlama) birbirinden bağımsız tutulmuş, hiçbir tescilli DLL veya kod parçacığı projeye kopyalanmadan saf Python ve `scipy.stats` kullanılmıştır.
