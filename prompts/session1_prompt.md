# Oturum 1: İnceleme, Tersine Mühendislik ve Şartname Çıkarımı (Specification Prompt)

## Amaç
G*Power 3.1.9.7 yazılımının **"F tests -> ANOVA: Fixed effects, omnibus, one-way"** (Tek Yönlü ANOVA) test modülünü tersine mühendislik araçları (`npx rea-agents`, Ghidra, PE analizi, x86 disassembler) ve orijinal literatür kılavuzları üzerinden derinlemesine incelemek; serbestlik dereceleri, noncentrality parametresi, hata denetimleri, `ceil` yuvarlama adımları ve A priori / Post-hoc hesaplama algoritmalarını çıkarıp `LEDGER.md` ve `SPEC.md` dosyalarına dökmektir.

## Görev Kapsamı
1. **Literatür ve Dokümantasyon İncelemesi [DOK]:**
   - Faul et al. (2007, 2009) makaleleri ve G*Power kullanıcı el kitabındaki F-testi formülasyonlarını doğrula.
   - Serbestlik dereceleri: $df_1 = k - 1$ (gruplar arası), $df_2 = N - k$ (hata / grup içi).
   - Noncentrality parametresi (NCP): $\lambda = f^2 \times N$.
   - Kritik F değeri ($F_{crit}$) ve Gerçek Güç ($1 - \beta$) formülasyonları.

2. **İkili (Binary) Analizi ve Tersine Mühendislik [REA]:**
   - `GPowerNT.exe` (SHA-256: `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812`) ikili dosyasını `npx rea-agents` ve statik analiz yöntemleriyle incele.
   - Vtable adreslerini, RTTI tanımlarını (`PowerFAnovaGlobal`, `CEff_F_Anova_Omni`) ve ilgili metodları tespit et.
   - Girdi doğrulama ve hata dizesi referans adreslerini (`There must be at least 2 groups`, `admissible range` kontrolleri) çıkar.
   - A priori $N$ arama döngüsünü ve grup dengelemesi için uygulanan `ceil` tavan yuvarlama (`ceil(N / k) * k`) mekanizmasını montaj kodunda doğrula.

3. **Ajan Çıkarımları [AJAN]:**
   - Hesaplama modelleri arasındaki farklar, grup başına eşit dağılım kuralı ($n \ge 2$), sınır durumları ve sayısal tolerans gereksinimlerini kaydet.

4. **Kabul Şartnamesi [SPEC]:**
   - Gherkin formatında `SPEC.md` hazırlayarak `a-priori`, `post-hoc` ve hata durumları (geçersiz $\alpha, \beta, f, k$) için kabul kriterlerini tanımla.
