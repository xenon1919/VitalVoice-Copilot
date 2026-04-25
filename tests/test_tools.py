from app.tools.health_tools import calculate_bmi, hydration_recommendation, symptom_checker


def test_bmi_range() -> None:
    result = calculate_bmi(weight_kg=70, height_cm=175)
    assert result.bmi == 22.9
    assert result.category == "normal"


def test_hydration_high_activity() -> None:
    result = hydration_recommendation(weight_kg=60, activity_level="high")
    assert result["recommended_liters_per_day"] > 2.5


def test_symptom_checker_includes_warning() -> None:
    result = symptom_checker("I have headache and fatigue")
    assert "warning" in result
