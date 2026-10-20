# Oturum 2: Temiz Oda Kodlama ve CLI Motoru (Clean Room Implementation Prompt)

## Amaç
Oturum 1'de oluşturulan `SPEC.md` kabul kriterlerine ve `LEDGER.md` dokümantasyonuna dayanarak, tersine mühendisliği yapılan kodlara veya tescilli binary kütüphanelerine doğrudan bağımlılık olmaksızın, tamamen bağımsız ve sıfırdan bir Python CLI hesaplama motoru geliştirmektir.

## Kodlama Kuralları ve Gereksinimler
1. **Bağımsız Temiz Oda Yaklaşımı (Clean-Room Design):**
   - Hesaplama motoru `scipy.stats` (özellikle `f` ve `ncf` dağılımları) ve standart Python kütüphaneleri kullanılarak `src/engine.py` içinde yazılmalıdır.
   - CLI arayüzü `src/cli.py` ve çalıştırılabilir wrapper `gpower-clone` (ve `gpower-clone.bat`) olarak hazırlanmalıdır.

2. **CLI Sözleşmesi:**
   ```bash
   python src/cli.py --test anova-oneway --mode <a-priori|post-hoc> --f <effect_size> --alpha <alpha> --power <power> --num-groups <k> [--n <n_total>]
   ```

3. **Girdi Doğrulama ve Hata Yönetimi:**
   - Grup sayısı $k < 2$ ise: `{"error":"There must be at least 2 groups."}`
   - Etki büyüklüğü $f \le 10^{-6}$ veya $f \ge 50.0$ ise: `{"error":"Effect size f is outside the admissible range (1e-06; 50)."}`
   - Alfa $\alpha \le 10^{-7}$ veya $\alpha \ge 1.0$ ise: `{"error":"Alpha is outside the admissible range (1e-07; 1)."}`
   - Güç $\le 10^{-7}$ veya $\ge 1.0$ ise: `{"error":"Power is outside the admissible range (1e-07; 1)."}`
   - Hata oluştuğunda JSON formatında hata mesajı dönmeli ve exit code `1` olmalıdır.

4. **Hesaplama Motoru Algoritması:**
   - **A Priori Modu:**
     - Grup başına eşit sayıda katılımcı ($n_{group}$) atanır. Her grupta en az 2 gözlem bulunmalıdır ($n_{group} \ge 2$).
     - İteratif olarak $\text{actual\_power}(n_{group} \times k) \ge \text{target\_power}$ koşulunu sağlayan en küçük tam sayı $n_{group}$ belirlenir.
     - Toplam örneklem $N = n_{group} \times k$ olarak kesinleştirilir.
   - **Post Hoc Modu:**
     - Verilen $N$ için (burada $N \ge 2k$), $df_1 = k - 1$, $df_2 = N - k$, $\lambda = f^2 \times N$, $F_{crit} = \text{ppf}_F(1 - \alpha, df_1, df_2)$ ve $\text{actual\_power} = \text{sf}_{ncF}(F_{crit}, df_1, df_2, \lambda)$ hesaplanır.

5. **Çıktı Biçimi:**
   - Standart çıkışa (stdout) tam olarak tek satır JSON nesnesi yazılmalıdır:
     ```json
     {"n_total": 1395, "actual_power": 0.8008513, "critical": 4.6204392, "df1": 2, "df2": 1392, "ncp": 13.95}
     ```
   - Çıkış kodu `0` olmalıdır.
