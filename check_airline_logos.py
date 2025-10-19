import requests

# List of IATA airline codes to test (add more as needed)
iata_codes = [
    "LH",  # Lufthansa
    "TP",  # TAP Air Portugal
    "AZ",  # ITA Airways
    "AF",  # Air France
    "BA",  # British Airways
    "EK",  # Emirates
    "AA",  # American Airlines
    "DL",  # Delta
    "UA",  # United
    "FR",  # Ryanair
    "U2",  # easyJet
    "LX",  # SWISS
    "KL",  # KLM
    "IB",  # Iberia
    "VY",  # Vueling
    "QR",  # Qatar Airways
    "SQ",  # Singapore Airlines
    "QF",  # Qantas
    "CX",  # Cathay Pacific
    "AC",  # Air Canada
]

logo_url_template = "https://content.airhex.com/content/logos/airlines_{code}_100_100_s.png"

def check_logo(iata_code):
    url = logo_url_template.format(code=iata_code)
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False

if __name__ == "__main__":
    print("Checking airline logo availability on airhex.com:")
    for code in iata_codes:
        has_logo = check_logo(code)
        print(f"{code}: {'✅ Logo found' if has_logo else '❌ No logo'}")
