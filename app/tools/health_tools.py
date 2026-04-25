from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BMIResult:
    bmi: float
    category: str


def calculate_bmi(weight_kg: float, height_cm: float) -> BMIResult:
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    if bmi < 18.5:
        category = "underweight"
    elif bmi < 25:
        category = "normal"
    elif bmi < 30:
        category = "overweight"
    else:
        category = "obesity"
    return BMIResult(bmi=round(bmi, 1), category=category)


def hydration_recommendation(weight_kg: float, activity_level: str) -> dict[str, float | str]:
    base_liters = weight_kg * 0.033
    activity_bonus = {"low": 0.2, "moderate": 0.5, "high": 1.0}.get(activity_level, 0.5)
    liters = round(base_liters + activity_bonus, 2)
    return {
        "recommended_liters_per_day": liters,
        "note": "Increase intake in hot weather, illness, or heavy activity.",
    }


def symptom_checker(symptoms_text: str) -> dict[str, str | list[str]]:
    text = symptoms_text.lower()
    mild_flags = []
    if "headache" in text:
        mild_flags.append("Hydration and rest may help headache symptoms.")
    if "tired" in text or "fatigue" in text:
        mild_flags.append("Sleep quality, stress, and hydration may contribute to fatigue.")
    if "fever" in text:
        mild_flags.append("Monitor temperature and fluid intake.")

    if not mild_flags:
        mild_flags.append("Monitor symptoms, rest, and seek medical advice if persistent.")

    return {
        "possible_supportive_actions": mild_flags,
        "warning": "This is not a diagnosis.",
    }
