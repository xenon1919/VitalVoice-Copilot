from __future__ import annotations

from app.tools.health_tools import calculate_bmi, hydration_recommendation, symptom_checker


class ToolAgent:
    def run(self, requested_tools: list[str], query: str) -> dict:
        results: dict = {}

        for tool in requested_tools:
            if tool == "symptom_checker":
                results["symptom_checker"] = symptom_checker(query)

        return results

    def run_bmi(self, weight_kg: float, height_cm: float) -> dict:
        result = calculate_bmi(weight_kg, height_cm)
        recommendations = {
            "underweight": "Consider consulting a healthcare provider about healthy weight gain.",
            "normal": "Maintain your current weight with balanced diet and exercise.",
            "overweight": "Consider increasing physical activity and adjusting diet.",
            "obesity": "Consult a healthcare provider for personalized guidance."
        }
        return {
            "bmi": result.bmi, 
            "category": result.category,
            "recommendation": recommendations.get(result.category, "Consult a healthcare provider.")
        }

    def run_hydration(self, weight_kg: float, activity_level: str) -> dict:
        result = hydration_recommendation(weight_kg, activity_level)
        return {
            "daily_intake_liters": result["recommended_liters_per_day"],
            "recommendation": result["note"]
        }
