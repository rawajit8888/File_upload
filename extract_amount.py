import re
from decimal import Decimal

import sys
sys.stdout.reconfigure(encoding='utf-8')


# Function to convert numbers with suffixes like lakh, crore, M, k into numeric values
def parse_amount_string(num_str, multiplier_str):
    num_clean = num_str.replace(',', '').replace(' ', '').strip()
    try:
        base = Decimal(num_clean)
    except Exception:
        base = Decimal(re.sub(r'[^\d\.]', '', num_clean) or '0')
    mult = Decimal(1)
    unit = None
    if not multiplier_str:
        return base, mult, unit
    m = multiplier_str.lower().strip()
    if re.search(r'\b(lakh|lac|lacs|lakh?s)\b', m) or m in ['l','lk']:
        mult = Decimal(100000); unit = 'lakh'
    elif re.search(r'\b(crore|cr|cr\.|crore?s)\b', m):
        mult = Decimal(10000000); unit = 'crore'
    elif re.search(r'\b(k|thousand|k\.|thou)\b', m):
        mult = Decimal(1000); unit = 'thousand'
    elif re.search(r'\b(million|m|mn|m\.|millions)\b', m):
        mult = Decimal(1000000); unit = 'million'
    elif re.search(r'\b(billion|bn|b)\b', m):
        mult = Decimal(1000000000); unit = 'billion'
    else:
        if m.endswith('k'):
            mult = Decimal(1000); unit = 'thousand'
        elif m.endswith('m'):
            mult = Decimal(1000000); unit = 'million'
        elif m.endswith('l'):
            mult = Decimal(100000); unit = 'lakh'
    return base, mult, unit

# Regex to detect numbers with optional suffixes and currency symbols
pattern = re.compile(r"""
(?P<prefix_currency>₹|rs\.?|inr|usd|\$)?      # optional prefix currency
\s*
(?P<number>\d[\d,\.]*\d|\d+)                 # number allowing commas/periods inside
\s*
(?P<suffix>(?:crore|cr\.?|cr|lakh|lac|lacs|l|k|k\.|thousand|million|m|mn|bn|b)s?\.?)?  # optional suffix
|
(?P<prefix_currency2>₹|rs\.?|inr|usd|\$)\s*(?P<number2>\d[\d,\.]*\d|\d+)
""", re.IGNORECASE | re.VERBOSE)

# Main function to extract amounts from text
def extract_amounts(text):
    results = []
    for m in pattern.finditer(text):
        currency = None
        num_str = None
        suffix = None
        if m.group('number'):
            num_str = m.group('number')
            suffix = m.group('suffix') or ''
            currency = m.group('prefix_currency') or ''
        else:
            num_str = m.group('number2') or ''
            currency = m.group('prefix_currency2') or ''
            suffix = ''
        cur = None
        if currency:
            c = currency.lower().replace('.', '').strip()
            if c in ('$', 'usd'):
                cur = 'USD'
            elif c in ('₹','rs','inr'):
                cur = 'INR'
            else:
                cur = currency.strip()
        base, mult, unit = parse_amount_string(num_str, suffix)
        normalized = int((base * mult).to_integral_value(rounding='ROUND_HALF_UP'))
        start, end = m.span()
        results.append({
            'text': text[start:end],
            'start': start,
            'end': end,
            'currency': cur or 'unknown',
            'value': normalized,
            'unit_multiplier': unit or (str(int(mult)) if mult!=1 else '1'),
            'raw_number': str(base),
            'suffix': suffix or None
        })
    return results


if __name__ == "__main__":
    emails = [
     "my internet banking current limit is 100000 now please increase my transaction limit upto 20,00000",
        "Please set limit to 20lakh",
        "Requesting 10 lacs for transfer",
        "Kindly allow Rs. 5,00,000",
        "Need ₹2.5 crore ASAP",
        "Need ₹2.5 cr ASAP",
        "increase my limit to 2L",
        "hi my internt bnaking limit is 39,0000 and i want to increase it to 12345678 ,kindly increase it as soon as possible",
        "Please approve $1.2 million for the purchase",
        "please increase limit by 5 lakh rs",
        "enhancement of limit two lakh rupees"
    ]

    for email in emails:
        print("Email:", email)
        extracted = extract_amounts(email)
        print("Extracted amounts:", extracted)
        print("-"*50)


