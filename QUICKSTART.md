# Quick Start Guide - Amadeus API + Streamlit

## 🚀 Setup Instructions

Follow these steps to get up and running:

### 1. Get Amadeus API Credentials (5 minutes)

1. Go to **https://developers.amadeus.com/**
2. Click **"Register"** to create a free account
3. After logging in, click **"Create New App"**
4. Choose **"Self-Service"** (Free tier: 2000 calls/month)
5. Fill in the app details:
   - **App Name**: CoolFlightPrices (or any name)
   - **Category**: Choose relevant category
6. Click **"Create"** 
7. You'll see your credentials:
   - **API Key** (long string)
   - **API Secret** (long string)
8. **Copy both** - you'll need them in the next step

### 2. Set Up the Project (5 minutes)

```bash
# Navigate to project directory
cd /Users/isaac/Documents/Progettini/CoolFlightPrices

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Credentials (2 minutes)

```bash
# Copy the example environment file
cp .env.example .env

# Open .env in your editor
nano .env
# or
open -e .env
```

Add your Amadeus credentials:
```bash
AMADEUS_API_KEY=your_actual_api_key_here
AMADEUS_API_SECRET=your_actual_api_secret_here
```

**Save the file!**

### 4. Test the API (2 minutes)

```bash
# Make sure virtual environment is active
source .venv/bin/activate

# Run the test script
python test_amadeus_api.py
```

You should see:
- ✅ Amadeus client initialized successfully!
- ✅ Found X flight offers!
- Flight details displayed

### 5. Launch the Streamlit UI (1 minute)

```bash
# Run the Streamlit app
streamlit run src/ui/app.py
```

Your browser should open automatically to `http://localhost:8501`

If not, manually open: **http://localhost:8501**

## 🎯 Using the App

1. **Search for flights:**
   - Enter origin (e.g., ZRH)
   - Enter destination (e.g., LIS)
   - Pick departure date
   - Choose roundtrip or one-way
   - Click "Search Flights"

2. **View results:**
   - Flights sorted by price
   - Expand any flight to see details
   - See flight times, airlines, stops

3. **Track flights (coming soon):**
   - Click "Track this flight" (placeholder for now)

## 🐛 Troubleshooting

### "Amadeus API credentials not found"
- Make sure you created the `.env` file
- Check that you copied the credentials correctly
- No spaces around the `=` sign
- No quotes around the values

### "Error during flight search"
- **Invalid airport code**: Use 3-letter IATA codes (ZRH, LIS, JFK, etc.)
- **API quota exceeded**: Free tier has 2000 calls/month
- **Invalid dates**: Make sure dates are in the future
- **Network error**: Check your internet connection

### "ModuleNotFoundError"
- Make sure virtual environment is activated: `source .venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port already in use
- Streamlit default port is 8501
- If busy, use: `streamlit run src/ui/app.py --server.port 8502`

## 📊 API Limits (Free Tier)

- **2000 API calls per month**
- **10 calls per second** (rate limited in code)
- **No credit card required**

Each search = 1 API call, so you can do about 66 searches per day.

## 🎓 Common Airport Codes

| Code | City | Country |
|------|------|---------|
| ZRH | Zurich | Switzerland |
| LIS | Lisbon | Portugal |
| LHR | London Heathrow | UK |
| CDG | Paris Charles de Gaulle | France |
| FCO | Rome Fiumicino | Italy |
| BCN | Barcelona | Spain |
| MAD | Madrid | Spain |
| AMS | Amsterdam | Netherlands |
| FRA | Frankfurt | Germany |
| MUC | Munich | Germany |
| JFK | New York JFK | USA |
| LAX | Los Angeles | USA |
| SFO | San Francisco | USA |
| ORD | Chicago O'Hare | USA |
| DXB | Dubai | UAE |
| SIN | Singapore | Singapore |
| HND | Tokyo Haneda | Japan |

Full list: https://www.iata.org/en/publications/directories/code-search/

## 🔜 Next Steps

Once the basic app is working:

1. **Add tracking functionality**
   - Save favorite flights
   - Monitor price changes
   - Set price alerts

2. **Add database storage**
   - Store search history
   - Track price over time
   - Export to CSV

3. **Add visualizations**
   - Price trend graphs
   - Calendar heatmaps
   - Price comparison charts

4. **Advanced features**
   - Multi-city searches
   - Flexible date searches
   - Price predictions

Check `TODO.md` for the complete roadmap!

## 📚 Resources

- **Amadeus Docs**: https://developers.amadeus.com/self-service
- **Streamlit Docs**: https://docs.streamlit.io/
- **Python Amadeus SDK**: https://github.com/amadeus4dev/amadeus-python

## 🆘 Need Help?

If you get stuck, check:
1. Error messages in terminal
2. Streamlit error display
3. `RESEARCH.md` for API alternatives
4. `PROJECT_PLAN.md` for development roadmap

Happy flight hunting! ✈️
