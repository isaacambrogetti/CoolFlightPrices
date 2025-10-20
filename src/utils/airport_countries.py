"""
Airport to Country Mapping

Maps IATA airport codes to their respective countries.
"""

# Airport code to country mapping
AIRPORT_COUNTRIES = {
    # Portugal
    'LIS': 'Portugal',
    'OPO': 'Portugal',
    'FAO': 'Portugal',
    'FNC': 'Portugal',
    'PDL': 'Portugal',
    
    # Switzerland
    'ZRH': 'Switzerland',
    'GVA': 'Switzerland',
    'BSL': 'Switzerland',
    'BRN': 'Switzerland',
    'LUG': 'Switzerland',
    
    # Spain
    'MAD': 'Spain',
    'BCN': 'Spain',
    'AGP': 'Spain',
    'PMI': 'Spain',
    'SVQ': 'Spain',
    'VLC': 'Spain',
    'BIO': 'Spain',
    'ALC': 'Spain',
    'SCQ': 'Spain',
    
    # France
    'CDG': 'France',
    'ORY': 'France',
    'NCE': 'France',
    'LYS': 'France',
    'MRS': 'France',
    'TLS': 'France',
    'BOD': 'France',
    'NTE': 'France',
    
    # Italy
    'FCO': 'Italy',
    'CIA': 'Italy',
    'MXP': 'Italy',
    'LIN': 'Italy',
    'VCE': 'Italy',
    'NAP': 'Italy',
    'BGY': 'Italy',
    'BLQ': 'Italy',
    'CTA': 'Italy',
    'PMO': 'Italy',
    
    # Germany
    'FRA': 'Germany',
    'MUC': 'Germany',
    'TXL': 'Germany',
    'DUS': 'Germany',
    'HAM': 'Germany',
    'CGN': 'Germany',
    'STR': 'Germany',
    'HAJ': 'Germany',
    
    # UK
    'LHR': 'United Kingdom',
    'LGW': 'United Kingdom',
    'STN': 'United Kingdom',
    'LTN': 'United Kingdom',
    'MAN': 'United Kingdom',
    'EDI': 'United Kingdom',
    'BHX': 'United Kingdom',
    'GLA': 'United Kingdom',
    
    # Greece
    'ATH': 'Greece',
    'HER': 'Greece',
    'RHO': 'Greece',
    'CFU': 'Greece',
    'JTR': 'Greece',
    'SKG': 'Greece',
    
    # Netherlands
    'AMS': 'Netherlands',
    'RTM': 'Netherlands',
    'EIN': 'Netherlands',
    
    # Belgium
    'BRU': 'Belgium',
    'CRL': 'Belgium',
    
    # Austria
    'VIE': 'Austria',
    'SZG': 'Austria',
    'INN': 'Austria',
    
    # USA
    'JFK': 'United States',
    'LAX': 'United States',
    'ORD': 'United States',
    'MIA': 'United States',
    'SFO': 'United States',
    'EWR': 'United States',
    'BOS': 'United States',
    'ATL': 'United States',
    'SEA': 'United States',
    'DEN': 'United States',
    
    # Canada
    'YYZ': 'Canada',
    'YVR': 'Canada',
    'YUL': 'Canada',
    
    # Other European
    'DUB': 'Ireland',
    'CPH': 'Denmark',
    'OSL': 'Norway',
    'ARN': 'Sweden',
    'HEL': 'Finland',
    'PRG': 'Czech Republic',
    'WAW': 'Poland',
    'BUD': 'Hungary',
    'OTP': 'Romania',
    'SOF': 'Bulgaria',
    'ZAG': 'Croatia',
    'LJU': 'Slovenia',
    
    # Middle East
    'DXB': 'United Arab Emirates',
    'AUH': 'United Arab Emirates',
    'DOH': 'Qatar',
    'IST': 'Turkey',
    'TLV': 'Israel',
    
    # Asia
    'HKG': 'Hong Kong',
    'SIN': 'Singapore',
    'NRT': 'Japan',
    'HND': 'Japan',
    'ICN': 'South Korea',
    'PEK': 'China',
    'PVG': 'China',
    'BKK': 'Thailand',
    'KUL': 'Malaysia',
    
    # South America
    'GRU': 'Brazil',
    'GIG': 'Brazil',
    'EZE': 'Argentina',
    'SCL': 'Chile',
    'BOG': 'Colombia',
    'LIM': 'Peru',
    
    # Africa
    'CAI': 'Egypt',
    'JNB': 'South Africa',
    'CPT': 'South Africa',
    'CMN': 'Morocco',
    'TUN': 'Tunisia',
    
    # Oceania
    'SYD': 'Australia',
    'MEL': 'Australia',
    'AKL': 'New Zealand',
}


def get_country_for_airport(airport_code: str) -> str:
    """
    Get the country for a given airport code
    
    Args:
        airport_code: 3-letter IATA airport code
        
    Returns:
        Country name, or 'Unknown' if not in mapping
    """
    return AIRPORT_COUNTRIES.get(airport_code.upper(), 'Unknown')


def get_airports_by_country(country: str) -> list:
    """
    Get all airport codes for a given country
    
    Args:
        country: Country name
        
    Returns:
        List of airport codes in that country
    """
    return [code for code, c in AIRPORT_COUNTRIES.items() if c == country]


def get_all_countries() -> list:
    """
    Get list of all countries in the mapping
    
    Returns:
        Sorted list of unique country names
    """
    return sorted(set(AIRPORT_COUNTRIES.values()))
