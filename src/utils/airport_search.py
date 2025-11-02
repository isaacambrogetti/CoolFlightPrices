"""
Airport search and autocomplete utilities
Helps users find airport codes by searching for city or airport names
"""

# Common airports database (can be expanded)
AIRPORTS = {
    # Switzerland
    'ZRH': {'name': 'Zurich Airport', 'city': 'Zurich', 'country': 'Switzerland'},
    'GVA': {'name': 'Geneva Airport', 'city': 'Geneva', 'country': 'Switzerland'},
    'BSL': {'name': 'EuroAirport Basel', 'city': 'Basel', 'country': 'Switzerland'},
    'BRN': {'name': 'Bern Airport', 'city': 'Bern', 'country': 'Switzerland'},
    
    # Portugal
    'LIS': {'name': 'Lisbon Airport', 'city': 'Lisbon', 'country': 'Portugal'},
    'OPO': {'name': 'Porto Airport', 'city': 'Porto', 'country': 'Portugal'},
    'FAO': {'name': 'Faro Airport', 'city': 'Faro', 'country': 'Portugal'},
    'PDL': {'name': 'Ponta Delgada Airport', 'city': 'Ponta Delgada', 'country': 'Portugal'},
    'FNC': {'name': 'Madeira Airport', 'city': 'Funchal', 'country': 'Portugal'},
    
    # UK
    'LHR': {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK'},
    'LGW': {'name': 'Gatwick Airport', 'city': 'London', 'country': 'UK'},
    'STN': {'name': 'Stansted Airport', 'city': 'London', 'country': 'UK'},
    'LTN': {'name': 'Luton Airport', 'city': 'London', 'country': 'UK'},
    'LCY': {'name': 'London City Airport', 'city': 'London', 'country': 'UK'},
    'MAN': {'name': 'Manchester Airport', 'city': 'Manchester', 'country': 'UK'},
    'EDI': {'name': 'Edinburgh Airport', 'city': 'Edinburgh', 'country': 'UK'},
    
    # France
    'CDG': {'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'country': 'France'},
    'ORY': {'name': 'Orly Airport', 'city': 'Paris', 'country': 'France'},
    'NCE': {'name': 'Nice Airport', 'city': 'Nice', 'country': 'France'},
    'LYS': {'name': 'Lyon Airport', 'city': 'Lyon', 'country': 'France'},
    'MRS': {'name': 'Marseille Airport', 'city': 'Marseille', 'country': 'France'},
    
    # Germany
    'FRA': {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany'},
    'MUC': {'name': 'Munich Airport', 'city': 'Munich', 'country': 'Germany'},
    'BER': {'name': 'Berlin Brandenburg Airport', 'city': 'Berlin', 'country': 'Germany'},
    'HAM': {'name': 'Hamburg Airport', 'city': 'Hamburg', 'country': 'Germany'},
    'DUS': {'name': 'Dusseldorf Airport', 'city': 'Dusseldorf', 'country': 'Germany'},
    
    # Spain
    'MAD': {'name': 'Madrid Barajas Airport', 'city': 'Madrid', 'country': 'Spain'},
    'BCN': {'name': 'Barcelona Airport', 'city': 'Barcelona', 'country': 'Spain'},
    'AGP': {'name': 'Malaga Airport', 'city': 'Malaga', 'country': 'Spain'},
    'PMI': {'name': 'Palma de Mallorca Airport', 'city': 'Palma', 'country': 'Spain'},
    'SVQ': {'name': 'Seville Airport', 'city': 'Seville', 'country': 'Spain'},
    'VLC': {'name': 'Valencia Airport', 'city': 'Valencia', 'country': 'Spain'},
    'ALC': {'name': 'Alicante Airport', 'city': 'Alicante', 'country': 'Spain'},
    
    # Italy
    'FCO': {'name': 'Fiumicino Airport', 'city': 'Rome', 'country': 'Italy'},
    'CIA': {'name': 'Ciampino Airport', 'city': 'Rome', 'country': 'Italy'},
    'MXP': {'name': 'Malpensa Airport', 'city': 'Milan', 'country': 'Italy'},
    'LIN': {'name': 'Linate Airport', 'city': 'Milan', 'country': 'Italy'},
    'BGY': {'name': 'Orio al Serio Airport', 'city': 'Bergamo', 'country': 'Italy'},
    'VCE': {'name': 'Marco Polo Airport', 'city': 'Venice', 'country': 'Italy'},
    'TSF': {'name': 'Treviso Airport', 'city': 'Treviso', 'country': 'Italy'},
    'BLQ': {'name': 'Bologna Airport', 'city': 'Bologna', 'country': 'Italy'},
    'NAP': {'name': 'Naples Airport', 'city': 'Naples', 'country': 'Italy'},
    'CTA': {'name': 'Catania Airport', 'city': 'Catania', 'country': 'Italy'},
    'PMO': {'name': 'Palermo Airport', 'city': 'Palermo', 'country': 'Italy'},
    'BRI': {'name': 'Bari Airport', 'city': 'Bari', 'country': 'Italy'},
    'TRN': {'name': 'Turin Airport', 'city': 'Turin', 'country': 'Italy'},
    'PSA': {'name': 'Pisa Airport', 'city': 'Pisa', 'country': 'Italy'},
    'FLR': {'name': 'Florence Airport', 'city': 'Florence', 'country': 'Italy'},
    'GOA': {'name': 'Genoa Airport', 'city': 'Genoa', 'country': 'Italy'},
    'VRN': {'name': 'Verona Airport', 'city': 'Verona', 'country': 'Italy'},
    'CAG': {'name': 'Cagliari Airport', 'city': 'Cagliari', 'country': 'Italy'},
    'OLB': {'name': 'Olbia Airport', 'city': 'Olbia', 'country': 'Italy'},
    'AHO': {'name': 'Alghero Airport', 'city': 'Alghero', 'country': 'Italy'},
    'TPS': {'name': 'Trapani Airport', 'city': 'Trapani', 'country': 'Italy'},
    'BDS': {'name': 'Brindisi Airport', 'city': 'Brindisi', 'country': 'Italy'},
    'AOI': {'name': 'Ancona Airport', 'city': 'Ancona', 'country': 'Italy'},
    'PEG': {'name': 'Perugia Airport', 'city': 'Perugia', 'country': 'Italy'},
    'RMI': {'name': 'Rimini Airport', 'city': 'Rimini', 'country': 'Italy'},
    'TRS': {'name': 'Trieste Airport', 'city': 'Trieste', 'country': 'Italy'},
    
    # USA
    'JFK': {'name': 'JFK Airport', 'city': 'New York', 'country': 'USA'},
    'LAX': {'name': 'Los Angeles Airport', 'city': 'Los Angeles', 'country': 'USA'},
    'ORD': {'name': "O'Hare Airport", 'city': 'Chicago', 'country': 'USA'},
    'MIA': {'name': 'Miami Airport', 'city': 'Miami', 'country': 'USA'},
    'SFO': {'name': 'San Francisco Airport', 'city': 'San Francisco', 'country': 'USA'},
    'BOS': {'name': 'Boston Logan Airport', 'city': 'Boston', 'country': 'USA'},
    
    # Netherlands
    'AMS': {'name': 'Amsterdam Schiphol Airport', 'city': 'Amsterdam', 'country': 'Netherlands'},
    
    # Belgium
    'BRU': {'name': 'Brussels Airport', 'city': 'Brussels', 'country': 'Belgium'},
    
    # Austria
    'VIE': {'name': 'Vienna Airport', 'city': 'Vienna', 'country': 'Austria'},
    
    # Greece
    'ATH': {'name': 'Athens Airport', 'city': 'Athens', 'country': 'Greece'},
    
    # Turkey
    'IST': {'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkey'},
    
    # UAE
    'DXB': {'name': 'Dubai Airport', 'city': 'Dubai', 'country': 'UAE'},
}


def search_airports(query: str, max_results: int = 10):
    """
    Search for airports by code, city name, or airport name
    
    Args:
        query: Search query (can be airport code, city name, or airport name)
        max_results: Maximum number of results to return
        
    Returns:
        List of tuples (code, display_string)
    """
    if not query:
        return []
    
    query = query.upper().strip()
    results = []
    
    # Direct code match (highest priority)
    if query in AIRPORTS:
        airport = AIRPORTS[query]
        results.append((query, f"{query} - {airport['city']}, {airport['country']} ({airport['name']})"))
    
    # Search in city names and airport names
    for code, airport in AIRPORTS.items():
        if query in code:
            continue  # Already added if direct match
        
        if (query in airport['city'].upper() or 
            query in airport['name'].upper() or
            query in airport['country'].upper()):
            results.append((code, f"{code} - {airport['city']}, {airport['country']} ({airport['name']})"))
    
    return results[:max_results]


def get_airport_display_name(code: str) -> str:
    """Get display name for an airport code"""
    if code in AIRPORTS:
        airport = AIRPORTS[code]
        return f"{code} - {airport['city']}, {airport['country']}"
    return code


def parse_airport_input(input_str: str) -> str:
    """
    Parse user input and extract airport code
    Handles formats like:
    - "ZRH"
    - "ZRH - Zurich, Switzerland"
    - "Zurich"
    
    Returns:
        Airport code (3-letter IATA code)
    """
    if not input_str:
        return ""
    
    input_str = input_str.strip().upper()
    
    # Check if it's already a 3-letter code
    if len(input_str) == 3 and input_str.isalpha():
        return input_str
    
    # Check if it contains a code at the beginning (format: "ZRH - City, Country")
    if ' - ' in input_str:
        code = input_str.split(' - ')[0].strip()
        if len(code) == 3 and code.isalpha():
            return code
    
    # Try to find by city/airport name
    results = search_airports(input_str, max_results=1)
    if results:
        return results[0][0]
    
    return ""


def get_all_airport_options():
    """Get all airports as display options for dropdown"""
    options = []
    for code, airport in sorted(AIRPORTS.items()):
        options.append(f"{code} - {airport['city']}, {airport['country']}")
    return options
