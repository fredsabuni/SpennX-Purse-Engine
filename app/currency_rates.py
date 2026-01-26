from decimal import Decimal
from typing import Dict

# Current exchange rates from spennx.com (1 USD = X currency)
# These rates will be used as fallback if rate is not in recipient JSON
# Later these can be loaded from a database table
CURRENCY_RATES: Dict[str, Decimal] = {
    "USD": Decimal("1.0"),
    "NGN": Decimal("1433.6190917516"),
    "KES": Decimal("125.30281513658"),
    "TZS": Decimal("2450.495049505"),
    "EUR": Decimal("0.83262260443543"),
    "GBP": Decimal("0.72138541150152"),
    "RWF": Decimal("1420.8214931542"),
    "UGX": Decimal("3457.7905067933"),
    "NOK": Decimal("9.7708691701344"),
    "AED": Decimal("3.6725"),
    "PHP": Decimal("59.44767954"),
    "CAD": Decimal("1.3452372791339"),
    "XAF": Decimal("571.1219951195"),
}

def get_usd_rate(currency_code: str) -> Decimal:
    """
    Get the exchange rate to convert from currency to USD.
    Returns 1 / rate since our rates are "1 USD = X currency"
    
    Example: 
    - 1 USD = 1433.62 NGN
    - To convert NGN to USD: amount_ngn / 1433.62
    - So rate_to_usd = 1 / 1433.62
    """
    if not currency_code:
        return Decimal("1.0")
    
    currency_code = currency_code.upper()
    
    if currency_code == "USD":
        return Decimal("1.0")
    
    if currency_code in CURRENCY_RATES:
        # Convert "1 USD = X currency" to "1 currency = Y USD"
        return Decimal("1.0") / CURRENCY_RATES[currency_code]
    
    # If currency not found, assume 1:1 (will need to be updated)
    return Decimal("1.0")

def convert_to_usd(amount: Decimal, currency_code: str, rate_from_json: Decimal = None) -> Decimal:
    """
    Convert an amount to USD.
    
    Priority:
    1. Use rate from recipient JSON if available (sanity checked against known rates)
    2. Use predefined rates from CURRENCY_RATES
    3. Assume 1:1 if currency not found
    
    Args:
        amount: The amount in original currency
        currency_code: The currency code (NGN, KES, etc.)
        rate_from_json: Optional rate from recipient JSON
    
    Returns:
        Amount in USD
    """
    if not amount:
        return Decimal("0")
    
    currency_code = currency_code.upper() if currency_code else "USD"
    
    # If using matching currency (USD to USD), result is amount
    if currency_code == "USD":
        return amount

    # Determine if we should trust the JSON rate
    use_json_rate = False
    
    if rate_from_json and rate_from_json > 0:
        # If we know the currency, sanity check the JSON rate
        if currency_code in CURRENCY_RATES:
            known_rate = CURRENCY_RATES[currency_code] # 1 USD = X Currency
            
            # Check if JSON rate matches "1 USD = X Currency" format (e.g. 571 for XAF)
            # Allow 50% deviation to account for market savings/fluctuations
            if abs(rate_from_json - known_rate) < (known_rate * Decimal("0.5")):
                use_json_rate = True
                
            # Check if JSON rate matches "1 Currency = Y USD" format (e.g. 0.0017 for XAF)
            elif abs((Decimal("1.0")/rate_from_json) - known_rate) < (known_rate * Decimal("0.5")):
                use_json_rate = True
                
            # If it matches neither (like the 2.515 case aka 7545 USD error), ignore it
            # and fall back to known rates
        else:
            # If currency unknown, we have to trust the JSON rate
            use_json_rate = True

    if use_json_rate:
        # Check if the JSON rate is "currency to USD" or "USD to currency"
        # If it's a large number (>10), it's likely "1 USD = X currency" (except for Japanese Yen etc, but generic rule)
        # Better heuristic: Compare with 1.0. 
        # Most african/global currencies designated here are > 1 per USD (NGN, XAF, KES)
        # Currencies < 1 per USD are GBP, EUR, KWD.
        
        if rate_from_json > 10:
             # Assume 1 USD = rate * Currency -> USD = Amount / rate
            return amount / rate_from_json
        else:
            # Assume 1 Currency = rate * USD -> USD = Amount * rate
            return amount * rate_from_json
    
    # Otherwise use our predefined rates
    usd_rate = get_usd_rate(currency_code)
    return amount * usd_rate

# Function to update rates from database (to be implemented later)
def update_rates_from_db(db_session):
    """
    Update CURRENCY_RATES from database table.
    This will be implemented when you create the rates table.
    
    Example table structure:
    CREATE TABLE currency_rates (
        currency_code VARCHAR(3) PRIMARY KEY,
        usd_rate DECIMAL(20, 10),
        updated_at TIMESTAMP
    );
    """
    pass
