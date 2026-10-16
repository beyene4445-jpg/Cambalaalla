"""
Sidama Traditional Calendar + Fichee Cambalaalla Predictor
Based on the Pleiades (Kore) star observation & lunar cycle.
"""
from datetime import datetime, timedelta

# Sidama months (traditional)
SIDAMA_MONTHS = [
    "Battessa", "Dottessa", "Onkolessa", "Woxawessa",
    "Birra", "Saddaasa", "Adola", "Hagayya",
    "Woxa", "Sase", "Xima", "Xela"
]

# Fichee Cambalaalla typically falls mid-April (Gregorian)
# Traditional rule: after the Pleiades (Kore) sets and the new moon
FICHEE_MONTH = 4   # April
FICHEE_DAY_RANGE = (10, 20)  # historically between Apr 10-20

def predict_fichee(year: int) -> dict:
    """
    Predict Fichee Cambalaalla date for a given Gregorian year.
    Rule: First new moon on/after April 10 (approximation).
    """
    # Simple lunar approximation: new moons ~every 29.53 days
    # Reference: Apr 12, 2024 was Fichee
    reference = datetime(2024, 4, 12)
    lunar_cycle = 29.530588
    days_since = (datetime(year, 1, 1) - reference).days
    
    # Find approximate new moon near April
    approx = datetime(year, 4, 12)
    # Adjust by lunar drift (13 days approx per year on calendar)
    drift = ((year - 2024) * 11) % 30
    predicted = approx + timedelta(days=drift - 15)
    
    # Clamp to typical range
    if predicted.month != 4:
        predicted = datetime(year, 4, 12)
    
    # Get next celebration
    today = datetime.now()
    next_year = year if predicted > today else year + 1
    if next_year != year:
        predicted = predict_fichee(next_year)['date']
    
    days_left = (predicted - today).days
    
    # Ethiopian Calendar conversion (approximation: EC = GC - 7/8)
    ec_year = predicted.year - 7 if predicted.month > 9 else predicted.year - 8
    
    return {
        'date': predicted,
        'gregorian': predicted.strftime('%B %d, %Y'),
        'ethiopian': f"{predicted.day} ሚያዝያ {ec_year} ዓ.ም",
        'days_left': days_left,
        'sidama_month': SIDAMA_MONTHS[3]  # Woxawessa
    }

def get_sidama_calendar() -> list:
    """Return Sidama months with Gregorian equivalents (approx)."""
    return [
        {"sidama": "Battessa", "gregorian": "September", "meaning": "Start of new year"},
        {"sidama": "Dottessa", "gregorian": "October", "meaning": "Harvest season"},
        {"sidama": "Onkolessa", "gregorian": "November", "meaning": "Planting"},
        {"sidama": "Woxawessa", "gregorian": "December", "meaning": "Dry season"},
        {"sidama": "Birra", "gregorian": "January", "meaning": "Sunny"},
        {"sidama": "Saddaasa", "gregorian": "February", "meaning": "Heat"},
        {"sidama": "Adola", "gregorian": "March", "meaning": "Pre-rain"},
        {"sidama": "Hagayya", "gregorian": "April", "meaning": "Fichee month"},
        {"sidama": "Woxa", "gregorian": "May", "meaning": "Rain starts"},
        {"sidama": "Sase", "gregorian": "June", "meaning": "Heavy rain"},
        {"sidama": "Xima", "gregorian": "July", "meaning": "Green"},
        {"sidama": "Xela", "gregorian": "August", "meaning": "Pre-harvest"},
    ]
