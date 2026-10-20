# Kabul Kriterleri Şartnamesi (SPEC.md)

Özellik: G*Power Klonu - Tek Yönlü ANOVA Güç ve Örneklem Analizi Motoru
  Bir araştırmacı veya veri bilimci olarak
  Tek yönlü ANOVA (One-Way ANOVA: Fixed effects, omnibus) analizleri için
  A priori (örneklem büyüklüğü belirleme) ve Post hoc (ulaşılan gücü hesaplama) hesaplamalarını
  G*Power 3.1.9.7 ile %100 uyumlu şekilde çalıştırmak istiyorum.

  Arka Plan:
    Geçerli aralık kısıtları:
      - Etki büyüklüğü f: (1e-06, 50.0) açık aralığı
      - Alfa (Tip I hata olasılığı): (1e-07, 1.0) açık aralığı
      - Güç (1 - Beta): (1e-07, 1.0) açık aralığı
      - Grup sayısı k: En az 2 (k >= 2) tamsayısı
      - Toplam örneklem N: k'nın tamsayı katı (N = n_group * k) ve grup başına en az 2 gözlem (n_group >= 2, N >= 2k)

  # -------------------------------------------------------------
  # Kural 1: A Priori Modu Hesaplamaları
  # -------------------------------------------------------------
  Senaryo Taslağı: Geçerli parametrelerle A Priori örneklem büyüklüğü hesaplama
    Diyelim ki hesaplama modu "a-priori" olarak seçildi
    Ve etki büyüklüğü f <f> olarak verildi
    Ve alfa düzeyi <alpha> olarak verildi
    Ve hedef güç <power> olarak verildi
    Ve grup sayısı <k> olarak verildi
    CLI motoru "--test anova-oneway --mode a-priori --f <f> --alpha <alpha> --power <power> --num-groups <k>" komutuyla çalıştırıldığında
    O zaman çıkış kodu 0 olmalıdır
    Ve çıktı tek satır geçerli bir JSON nesnesi olmalıdır
    Ve JSON çıktısındaki "n_total" değeri beklenen <expected_n> değerine tam olarak eşit olmalıdır
    Ve JSON çıktısındaki "df1" değeri <expected_df1> olmalıdır
    Ve JSON çıktısındaki "df2" değeri <expected_df2> olmalıdır
    Ve JSON çıktısındaki "actual_power" değeri en az <power> olmalı ve beklenen <expected_power> ile 1e-4 hassasiyetle uyuşmalıdır
    Ve JSON çıktısındaki "critical" değeri beklenen <expected_crit> ile 1e-4 hassasiyetle uyuşmalıdır
    Ve JSON çıktısındaki "ncp" değeri beklenen <expected_ncp> ile 1e-4 hassasiyetle uyuşmalıdır

    Örnekler:
      | f    | alpha | power | k | expected_n | expected_df1 | expected_df2 | expected_ncp | expected_crit | expected_power |
      | 0.10 | 0.01  | 0.80  | 3 | 1395       | 2            | 1392         | 13.9500000   | 4.6204392     | 0.8008513      |
      | 0.10 | 0.01  | 0.80  | 4 | 1552       | 3            | 1548         | 15.5200000   | 3.7942844     | 0.8001904      |
      | 0.10 | 0.01  | 0.80  | 5 | 1685       | 4            | 1680         | 16.8500000   | 3.3303378     | 0.8011114      |
      | 0.10 | 0.05  | 0.80  | 3 | 969        | 2            | 966          | 9.6900000    | 3.0050418     | 0.8011010      |
      | 0.10 | 0.05  | 0.95  | 3 | 1548       | 2            | 1545         | 15.4800000   | 3.0015485     | 0.9500866      |
      | 0.25 | 0.05  | 0.95  | 3 | 252        | 2            | 249          | 15.7500000   | 3.0320649     | 0.9514888      |
      | 0.25 | 0.01  | 0.80  | 3 | 228        | 2            | 225          | 14.2500000   | 4.7007255     | 0.8029054      |
      | 0.001| 0.05  | 0.05  |100| 200        | 99           | 100          | 0.0002000    | 1.3926688     | 0.0500010      |
      | 5.0  | 0.05  | 0.05  |100| 200        | 99           | 100          | 5000.0       | 1.3926688     | 1.0000000      |

  # -------------------------------------------------------------
  # Kural 2: Post Hoc Modu Hesaplamaları
  # -------------------------------------------------------------
  Senaryo Taslağı: Belirli bir örneklem büyüklüğü ile Post Hoc güç hesaplama
    Diyelim ki hesaplama modu "post-hoc" olarak seçildi
    Ve etki büyüklüğü f <f> olarak verildi
    Ve alfa düzeyi <alpha> olarak verildi
    Ve grup sayısı <k> olarak verildi
    Ve toplam örneklem boyutu N <n_total> olarak sağlandı
    CLI motoru "--test anova-oneway --mode post-hoc --f <f> --alpha <alpha> --num-groups <k> --n <n_total>" komutuyla çalıştırıldığında
    O zaman çıkış kodu 0 olmalıdır
    Ve çıktı tek satır geçerli bir JSON nesnesi olmalıdır
    Ve JSON çıktısındaki "n_total" değeri <n_total> olmalıdır
    Ve JSON çıktısındaki "df1" değeri (<k> - 1) olmalıdır
    Ve JSON çıktısındaki "df2" değeri (<n_total> - <k>) olmalıdır
    Ve JSON çıktısındaki "ncp" değeri (<f>^2 * <n_total>) olmalıdır
    Ve JSON çıktısındaki "actual_power" değeri beklenen <expected_power> ile 1e-4 hassasiyetle uyuşmalıdır

    Örnekler:
      | f    | alpha | k | n_total | expected_power |
      | 0.10 | 0.01  | 3 | 1395    | 0.8008513      |
      | 0.25 | 0.05  | 3 | 252     | 0.9514888      |
      | 0.25 | 0.01  | 4 | 256     | 0.8062800      |

  # -------------------------------------------------------------
  # Kural 3: Geçersiz Girdiler ve Hata Denetimi
  # -------------------------------------------------------------
  Senaryo Taslağı: Geçersiz parametreler verildiğinde hata fırlatma
    Diyelim ki CLI geçersiz parametrelerle çağrıldı: <invalid_args>
    CLI motoru bu parametrelerle çalıştırıldığında
    O zaman çıkış kodu 0'dan farklı (1) olmalıdır
    Ve çıktı tek satır JSON nesnesi olmalıdır
    Ve JSON çıktısı "error" anahtarı içermelidir
    Ve hata mesajı <expected_error_substr> ifadesini içermelidir

    Örnekler:
      | invalid_args                                                     | expected_error_substr                                         |
      | --test anova-oneway --mode a-priori --f 0.0 --alpha 0.05 --power 0.80 --num-groups 3  | Effect size f is outside the admissible range (1e-06; 50).    |
      | --test anova-oneway --mode a-priori --f 0.25 --alpha 1.0 --power 0.80 --num-groups 3 | Alpha is outside the admissible range (1e-07; 1).             |
      | --test anova-oneway --mode a-priori --f 0.25 --alpha 0.5 --power 1.0 --num-groups 3  | Power is outside the admissible range (1e-07; 1).             |
      | --test anova-oneway --mode a-priori --f 0.25 --alpha 0.5 --power 0.80 --num-groups 1 | There must be at least 2 groups.                              |
      | --test anova-oneway --mode a-priori --f 0.25 --alpha 0.5 --power -0.8 --num-groups 3 | Power is outside the admissible range (1e-07; 1).             |
      | --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --num-groups 3             | Total sample size (--n) is required for post-hoc mode         |
      | --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --num-groups 3 --n 3       | Total sample size must be at least 2 * num_groups             |
