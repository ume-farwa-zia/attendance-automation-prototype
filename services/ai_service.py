"""
AI-powered attendance insights using Google Gemini.

If GEMINI_API_KEY isn't set, falls back to a rule-based summary so the
dashboard is fully demoable without a live API key/billing account — the
same "graceful degradation" pattern used for QR/geofence testing.
"""
import json

from config import Config


def _rule_based_summary(stats: dict) -> dict:
    total = stats.get("total_employees", 0)
    present = stats.get("present", 0)
    late = stats.get("late", 0)
    absent = stats.get("absent", 0)

    rate = round((present + late) / total * 100, 1) if total else 0.0

    if rate >= 90:
        health = "Excellent"
    elif rate >= 75:
        health = "Good"
    elif rate >= 50:
        health = "Needs attention"
    else:
        health = "Poor"

    recommendations = []
    if late > 0:
        recommendations.append(
            f"{late} employee(s) arrived late today — consider a reminder about office start time."
        )
    if absent > 0:
        recommendations.append(
            f"{absent} employee(s) have not checked in yet — follow up if this continues."
        )
    if not recommendations:
        recommendations.append("Attendance looks healthy today, no action needed.")

    return {
        "attendance_rate_percent": rate,
        "health_score": health,
        "summary": f"{present + late} of {total} employees present today ({rate}%). "
                   f"{late} late, {absent} not yet checked in.",
        "recommendations": recommendations,
        "source": "rule_based_fallback",
    }


def generate_attendance_insights(stats: dict) -> dict:
    """
    stats: {"total_employees": int, "present": int, "late": int, "absent": int, "date": str}
    Returns a dict with attendance_rate_percent, health_score, summary, recommendations.
    """
    if not Config.GEMINI_API_KEY:
        return _rule_based_summary(stats)

    try:
        import google.generativeai as genai

        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)

        prompt = f"""You are an HR attendance analyst. Given these stats for {stats.get('date')}:
Total employees: {stats.get('total_employees')}
Present (on time): {stats.get('present')}
Late: {stats.get('late')}
Absent / not checked in: {stats.get('absent')}

Respond ONLY with JSON (no markdown, no preamble) in this exact shape:
{{"attendance_rate_percent": <number>, "health_score": "<Excellent|Good|Needs attention|Poor>",
"summary": "<one or two sentence summary>", "recommendations": ["<short actionable tip>", "..."]}}"""

        response = model.generate_content(prompt)
        text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(text)
        result["source"] = "gemini"
        return result

    except Exception:
        # Any API/parsing failure falls back to rule-based rather than
        # breaking the dashboard.
        fallback = _rule_based_summary(stats)
        fallback["source"] = "rule_based_fallback_after_gemini_error"
        return fallback
