from decimal import Decimal, ROUND_HALF_UP

def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    Round a Decimal value to specified decimal places.
    Uses ROUND_HALF_UP (standard rounding).
    """
    if value is None:
        return Decimal("0.00")
    
    quantize_value = Decimal(10) ** -places
    return value.quantize(quantize_value, rounding=ROUND_HALF_UP)

def format_currency(value: Decimal) -> str:
    """
    Format currency values to 2 decimal places with thousand separators.
    Example: 1234567.89 -> "1,234,567.89"
    """
    if value is None:
        value = Decimal("0.00")
    
    # Round to 2 decimal places
    rounded = round_decimal(value, 2)
    
    # Format with thousand separators
    return f"{rounded:,.2f}"

def format_percentage(value: float) -> float:
    """
    Format percentage values to 2 decimal places.
    """
    return round(value, 2)
