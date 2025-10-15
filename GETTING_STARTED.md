# Getting Started Guide

## Welcome to CoolFlightPrices! 🛫

This project is an extension of your FlightsPlot project, designed to fetch flight data directly from Skyscanner instead of parsing email updates.

## What's Been Set Up

I've created a solid foundation for your project with:

### ✅ Project Structure
- Clean, modular code organization
- API client abstractions (ready to implement)
- Data models for flights and tracking
- Configuration management
- Rate limiting utilities

### ✅ Documentation
- **README.md**: Project overview
- **PROJECT_PLAN.md**: Detailed roadmap with implementation phases
- **RESEARCH.md**: API options and recommendations
- **TODO.md**: Immediate next steps

### ✅ Code Foundation
- Abstract API client interface
- Data models for `Flight`, `RoundtripFlight`, `TrackedFlight`
- Rate limiter to respect API quotas
- Environment-based configuration

## What You Need to Do Next

Since you mentioned you don't have all the details yet, here's a step-by-step approach:

### Step 1: Research APIs (1-2 hours)

Pick one of these approaches:

**Option A: RapidAPI Skyscanner (Recommended)**
1. Go to https://rapidapi.com/
2. Search for "Skyscanner"
3. Check pricing and features
4. Sign up for free tier to test

**Option B: Kiwi.com (Alternative)**
1. Go to https://tequila.kiwi.com/
2. Sign up for free API key
3. Read documentation
4. Test with some queries

**Option C: Amadeus (Enterprise)**
1. Go to https://developers.amadeus.com/
2. Free tier: 2000 calls/month
3. More complex but very robust

### Step 2: Test an API (2-3 hours)

Once you pick an API, create a simple test:

```python
# test_api.py
import requests
from datetime import date, timedelta

# Example with RapidAPI
def test_skyscanner():
    url = "https://skyscanner-api.p.rapidapi.com/flights/search"
    
    headers = {
        "X-RapidAPI-Key": "YOUR_KEY_HERE",
        "X-RapidAPI-Host": "skyscanner-api.p.rapidapi.com"
    }
    
    params = {
        "origin": "ZRH",
        "destination": "LIS",
        "departureDate": "2025-11-01",
        "returnDate": "2025-11-05",
        "adults": 1
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(response.json())

if __name__ == "__main__":
    test_skyscanner()
```

### Step 3: Decide on UI (30 minutes)

I recommend **Streamlit** because:
- ✅ Fastest to build
- ✅ Python-only (no HTML/CSS/JS)
- ✅ Great for data applications
- ✅ Built-in widgets

To test Streamlit:
```bash
pip install streamlit
streamlit hello  # See examples
```

### Step 4: Build MVP (4-8 hours)

Minimal Viable Product should:
1. Let you enter origin/destination
2. Pick dates
3. Show list of flights
4. Display prices

### Step 5: Add Tracking (2-4 hours)

Then add:
1. "Track this flight" button
2. List of tracked flights
3. Manual price refresh

### Step 6: Automation (4-8 hours)

Finally:
1. Scheduled price checks
2. Store history in database
3. Visualize with plots from original project

## Quick Start Commands

```bash
# Navigate to project
cd /Users/isaac/Documents/Progettini/CoolFlightPrices

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install base dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys (when you have them)
nano .env

# Run tests (when we create them)
# pytest
```

## Project Timeline Estimate

| Phase | Time | Description |
|-------|------|-------------|
| **Phase 1**: API Research | 2-4 hours | Test APIs, pick one |
| **Phase 2**: Basic Fetching | 4-6 hours | Get API calls working |
| **Phase 3**: Simple UI | 4-8 hours | Build search interface |
| **Phase 4**: Display Results | 2-4 hours | Show flights nicely |
| **Phase 5**: Tracking | 4-6 hours | Add/remove tracked flights |
| **Phase 6**: Database | 4-6 hours | Store data persistently |
| **Phase 7**: Automation | 6-8 hours | Background checking |
| **Phase 8**: Visualization | 4-6 hours | Port plotting code |
| **Phase 9**: Polish | 4-8 hours | Error handling, UX |

**Total**: ~35-60 hours of development time

## Important Notes

### API Costs
Most flight APIs have:
- Free tiers with limits
- Paid tiers starting ~$10-50/month
- Rate limits (calls per minute/hour)

**Budget accordingly!**

### Legal Considerations
- ✅ Using official APIs = Legal
- ❌ Web scraping = Against ToS, fragile, ethical issues
- Always use official APIs when available

### Data Accuracy
- Prices change constantly
- Airlines may have different prices
- Always include links to actual booking

## Questions?

As you work through this, you'll discover:
- Which API works best
- What features you really need
- UI preferences
- Performance requirements

**Don't worry about knowing everything upfront!** This foundation is flexible enough to adapt as you learn more.

## Next Steps

1. Read through `RESEARCH.md` for API options
2. Pick an API and sign up
3. Run a test API call
4. Come back and we'll build the first feature!

Good luck! 🚀
