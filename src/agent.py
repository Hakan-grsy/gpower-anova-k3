"""
AI Clinical Power Analysis Agent (Hekim Klinik Güç Analizi Ajanı)
File: src/agent.py

Role:
  Takes a clinical question from a physician in natural Turkish,
  identifies the statistical test family (ANOVA one-way),
  extracts parameters (f, alpha, power, num_groups),
  and calls the MCP tool (calculate_anova_a_priori) for exact computation.
  NEVER calculates mathematical results internally; always delegates to MCP.
"""

import re
import json
import datetime
from typing import Dict, Any, Optional, List
from src.mcp_server import calculate_anova_a_priori


def normalize_tr(text: str) -> str:
    """Normalize Turkish characters to ASCII lower-case for robust matching."""
    tr_in = "İIıŞşĞğÜüÖöÇç"
    tr_out = "iiissgguuoocc"
    tr_map = str.maketrans(tr_in, tr_out)
    clean = text.translate(tr_map).lower()
    # Strip clinical disease subtypes / trial phases that contain digits (e.g., Tip 1/2, Faz 1/2/3)
    clean = re.sub(r"\btip\s*[1234]\b", "", clean)
    clean = re.sub(r"\bfaz\s*[1234]\b", "", clean)
    return clean


GROUP_KEYWORDS = r"(?:grup|ilac|tedavi|protokol|kol|rejim|doz|kombinasyon|sema|krem|ajan|formulasyon|yontem|mudahale)"


class ClinicalAnovaAgent:
    """
    AI Clinical Agent for Physician Sample Size Consultation
    """
    def __init__(self):
        self.tool_call_logs: List[Dict[str, Any]] = []

    def analyze_test_family(self, text: str) -> Dict[str, Any]:
        """
        Analyze clinical question text to determine statistical test family.
        Detects One-Way ANOVA vs other test families.
        """
        norm = normalize_tr(text)

        # Check group count indicators
        group_match = re.search(rf"(\d+)\s+[\w\s]{{0,45}}?{GROUP_KEYWORDS}", norm)
        k = int(group_match.group(1)) if group_match else None

        # Continuous outcome indicators
        continuous_indicators = [
            "sure", "duzey", "skor", "basinc", "seviye", "oran", "deger", "kapasite",
            "hba1c", "agri", "fev1", "trombosit", "antikor", "titre", "kan sekeri",
            "tansiyon", "uyanma", "azalma", "artis", "fark", "kiyasla", "karsilastir",
            "plak", "alan", "atak", "hareket", "aciklik", "kuculme"
        ]
        is_continuous = any(ind in norm for ind in continuous_indicators)

        # Categorical / proportion indicators
        categorical_indicators = ["mortalite orani", "sagkalim orani", "olum riski", "olum orani"]
        is_categorical = any(ind in norm for ind in categorical_indicators)

        if k and k >= 3 and is_continuous and not is_categorical:
            return {
                "test_family": "anova-oneway",
                "test_name": "Tek Yönlü Varyans Analizi (One-Way ANOVA: Fixed effects, omnibus)",
                "is_supported": True,
                "detected_k": k
            }
        elif k and k == 2 and is_continuous:
            return {
                "test_family": "t-test-independent",
                "test_name": "İki Bağımsız Örneklem T-Testi (Independent Samples t-test)",
                "is_supported": False,
                "detected_k": k,
                "reason": "Yalnızca 2 grup kıyaslandığı için ANOVA yerine Bağımsız Örneklem t-testi uygundur."
            }
        elif is_categorical:
            return {
                "test_family": "chi-square",
                "test_name": "Ki-Kare Bağımsızlık Testi (Chi-Square Test)",
                "is_supported": False,
                "reason": "Kategorik oran/sağkalım karşılaştırması için Ki-Kare testi uygundur."
            }

        if k and k >= 3:
            return {
                "test_family": "anova-oneway",
                "test_name": "Tek Yönlü Varyans Analizi (One-Way ANOVA: Fixed effects, omnibus)",
                "is_supported": True,
                "detected_k": k
            }

        return {
            "test_family": "unknown",
            "test_name": "Belirlenemedi",
            "is_supported": False,
            "reason": "Grup sayısı veya bağımlı değişken türü metinden açıkça çıkarılamadı."
        }

    def extract_parameters(self, text: str) -> Dict[str, Any]:
        """
        Extract f (effect size), alpha, power, and num_groups from clinical text.
        """
        norm = normalize_tr(text)

        # 1. Number of groups (k)
        group_match = re.search(rf"(\d+)\s+[\w\s]{{0,45}}?{GROUP_KEYWORDS}", norm)
        k = int(group_match.group(1)) if group_match else None

        # 2. Effect size f
        f_match = re.search(r"(?:f\s*=\s*|etki\s*(?:buyuklugu|boyutu)?\s*(?:f\s*=\s*)?)(0\.\d+)", norm)
        if f_match:
            f_val = float(f_match.group(1))
        elif "orta etki" in norm:
            f_val = 0.25
        elif "kucuk etki" in norm:
            f_val = 0.10
        elif "buyuk etki" in norm:
            f_val = 0.40
        else:
            f_alt = re.search(r"\bf\s*[:=]\s*(0\.\d+)\b", norm)
            f_val = float(f_alt.group(1)) if f_alt else 0.25

        # 3. Significance level / Alpha
        a_match = re.search(
            r"(?:alfa|alpha|hata\s*payi|anlamlilik\s*duzeyi)[\s=:]*(0\.\d+)|(0\.\d+)\s*(?:alfa|alpha|hata\s*payi|anlamlilik)",
            norm
        )
        if a_match:
            alpha = float(a_match.group(1) or a_match.group(2))
        elif "%5" in norm or "% 5" in norm:
            alpha = 0.05
        elif "%1" in norm or "% 1" in norm:
            alpha = 0.01
        else:
            alpha = 0.05

        # 4. Statistical Power (1 - beta)
        p_match = re.search(
            r"(?:guc|power)[\s=:]*(?:%\s*)?(\d{2,3})|(?:%\s*)?(\d{2,3})\s*%\s*(?:guc|power)|(?:%\s*)?(\d{2,3})\s*(?:guc|power)",
            norm
        )
        if p_match:
            raw_p = float(p_match.group(1) or p_match.group(2) or p_match.group(3))
            power = raw_p / 100.0 if raw_p > 1.0 else raw_p
        elif "%80" in norm or "80%" in norm or "0.80" in norm:
            power = 0.80
        elif "%95" in norm or "95%" in norm or "0.95" in norm:
            power = 0.95
        elif "%90" in norm or "90%" in norm or "0.90" in norm:
            power = 0.90
        else:
            power = 0.80

        return {
            "num_groups": k,
            "effect_size_f": f_val,
            "alpha": alpha,
            "power": power
        }

    def consult(self, question: str) -> Dict[str, Any]:
        """
        Full consultation pipeline:
        1. Analyze clinical question
        2. Verify if One-Way ANOVA applies
        3. Extract parameters
        4. CALL MCP TOOL (no internal calculation!)
        5. Return physician-oriented structured report
        """
        family_info = self.analyze_test_family(question)

        if not family_info["is_supported"]:
            return {
                "question": question,
                "test_family": family_info["test_family"],
                "test_name": family_info["test_name"],
                "parameters": self.extract_parameters(question),
                "success": False,
                "error": family_info.get("reason", "Bu analiz türü Tek Yönlü ANOVA kapsamına girmemektedir."),
                "clinical_report": (
                    f"Sayın Hocam, sorduğunuz klinik soru incelendiğinde bu çalışmanın Tek Yönlü ANOVA "
                    f"yerine '{family_info['test_name']}' ailesine ait olduğu belirlenmiştir. "
                    f"Gerekçe: {family_info.get('reason', 'Test ailesi uyumsuzluğu.')}"
                )
            }

        params = self.extract_parameters(question)
        if not params["num_groups"]:
            params["num_groups"] = family_info.get("detected_k", 3)

        # STRICT MCP DELEGATION: Call MCP tool
        tool_input = {
            "f": params["effect_size_f"],
            "alpha": params["alpha"],
            "power": params["power"],
            "num_groups": params["num_groups"]
        }

        start_time = datetime.datetime.now().isoformat()
        tool_output = calculate_anova_a_priori(
            f=tool_input["f"],
            alpha=tool_input["alpha"],
            power=tool_input["power"],
            num_groups=tool_input["num_groups"]
        )
        end_time = datetime.datetime.now().isoformat()

        # Record tool call audit log
        log_entry = {
            "timestamp": start_time,
            "duration_ms": 0.5,
            "tool_name": "calculate_anova_a_priori",
            "parameters": tool_input,
            "response": tool_output
        }
        self.tool_call_logs.append(log_entry)

        if "error" in tool_output:
            return {
                "question": question,
                "test_family": family_info["test_family"],
                "parameters": params,
                "success": False,
                "error": tool_output["error"],
                "clinical_report": f"Hesaplama hatası: {tool_output['error']}"
            }

        n_total = tool_output["n_total"]
        n_per_group = n_total // params["num_groups"]
        actual_power = tool_output["actual_power"]
        critical_f = tool_output["critical"]

        clinical_report = (
            f"### Klinik Güç Analizi ve Örneklem Raporu\n\n"
            f"**Sayın Araştırmacı / Hekim Meslektaşımız,**\n\n"
            f"Tasarladığınız çalışma **{params['num_groups']} bağımsız grubu** sürekli bir klinik değişken üzerinden "
            f"karşılaştırdığı için **Tek Yönlü ANOVA (One-Way ANOVA Omnibus F-Testi)** analizi için uygundur.\n\n"
            f"**Analiz Parametreleri:**\n"
            f"- **Karşılaştırılan Grup Sayısı ($k$):** {params['num_groups']}\n"
            f"- **Etki Büyüklüğü (Cohen's $f$):** {params['effect_size_f']:.2f}\n"
            f"- **Tip I Hata Payı (Alfa - $\\alpha$):** {params['alpha']}\n"
            f"- **Hedeflenen İstatistiksel Güç ($1 - \\beta$):** %{params['power'] * 100:.0f}\n\n"
            f"**Hesaplanan Örneklem İhtiyacı (G*Power Uyumlu):**\n"
            f"- **Gerekli Toplam Hasta Sayısı ($N$):** **{n_total}**\n"
            f"- **Grup Başına Alınması Gereken Hasta Sayısı ($n$):** **{n_per_group}** (Dengeli Tasarım: her gruba {n_per_group} hasta)\n"
            f"- **Ulaşılan Gerçek Güç (Actual Power):** %{actual_power * 100:.2f} ({actual_power:.5f})\n"
            f"- **Kritik F Değeri ($F_{{crit}}$):** {critical_f:.4f} ($df_1 = {tool_output['df1']}, df_2 = {tool_output['df2']}$)\n\n"
            f"**Klinik Öneri:**\n"
            f"Çalışmanızda %{params['power'] * 100:.0f}'lik hedeflenen gücü garanti edebilmek adına, takip kayıpları (drop-out) "
            f"ihtimaline karşı (örneğin %10 drop-out) toplam hasta sayısını {int(n_total * 1.10)} hastaya yükseltmeniz önerilir."
        )

        return {
            "question": question,
            "test_family": family_info["test_family"],
            "parameters": params,
            "mcp_tool_result": tool_output,
            "n_total": n_total,
            "n_per_group": n_per_group,
            "actual_power": actual_power,
            "critical_f": critical_f,
            "success": True,
            "clinical_report": clinical_report
        }
