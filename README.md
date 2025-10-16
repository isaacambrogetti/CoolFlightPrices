# CoolFlightPrices ✈️

> **Smart flight search with flexible dates, multi-airport comparison, and intelligent price tracking**

An advanced flight price comparison tool that extends the original [FlightsPlot](https://github.com/isaacambrogetti/FlightsPlot) project. Instead of relying on email updates, CoolFlightPrices directly fetches real-time flight data from the Amadeus API and provides powerful search capabilities with interactive visualizations.

![Python](https://img.shields.io/badge/python-3.13-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.50.0-red)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Features

### ✅ Currently Available

#### 🔍 Smart Search Modes
- **Single Date Search**: Find best flights for specific dates
- **Flexible Date Search**: Compare prices across date ranges (up to hundreds of combinations)
- **Multi-Airport Search**: Compare multiple origin/destination airports simultaneously

#### 📊 Interactive Visualizations
- **Price Heatmap**: Visual calendar showing cheapest days to fly
- **Price Distribution**: Histogram of price ranges across all combinations
- **Duration vs Price**: Scatter plot showing trip length trade-offs
- **Calendar View**: Bar chart of best prices per departure date

#### ⚙️ Advanced Filters
- **Time Filtering**: Set acceptable departure/arrival hours (e.g., no red-eyes)
- **Trip Duration Strategies**:
  - Flexible: Any duration within range
  - Fixed Duration: Exactly N days
  - Maximum Days Possible: Prioritize longest stays
- **Smart Sampling**: Reduce API calls while maintaining coverage

#### 🎯 Key Capabilities
- One-way and roundtrip flights
- Compare up to 9+ airport combinations
- Real-time price data from 400+ airlines
- Rate-limited API calls (respects free tier limits)
- Detailed flight information (times, airlines, stops, duration)

## 📋 Quick Start

### Prerequisites
- Python 3.8 or higher
- Amadeus API credentials ([free signup](https://developers.amadeus.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/isaacambrogetti/CoolFlightPrices.git
cd CoolFlightPrices
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API credentials**
```bash
cp .env.example .env
# Edit .env and add your Amadeus API credentials:
# AMADEUS_API_KEY=your_key_here
# AMADEUS_API_SECRET=your_secret_here
```

5. **Run the application**
```bash
streamlit run src/ui/app.py
```

6. **Open in browser**: http://localhost:8501

## 🎮 Usage Examples

### Single Date Search
Perfect for specific travel plans:
```
From: ZRH
To: LIS
Departure: 2025-12-15
Return: 2025-12-22
→ Find best flights for these exact dates
```

### Flexible Date Search
When you have date flexibility:
```
Departure: Dec 10-20 (11 days)
Return: Dec 17-27 (11 days)
Min days at destination: 5
→ Compare 121 date combinations, find cheapest option
```

### Multi-Airport Search
Compare nearby airports:
```
From: ZRH, GVA, BSL  (Switzerland)
To: LIS, OPO, FAO    (Portugal)
→ Compare 9 route combinations, find absolute best deal
```

### Advanced: All Features Combined
```
From: ZRH, GVA
To: LIS, OPO
Departure: Dec 10-20
Return: Dec 17-27
Duration: Fixed 7 days
Time filters: Departure after 8 AM, arrival before 10 PM
→ Smart search across routes, dates, and preferences
```

## 📁 Project Structure

```
CoolFlightPrices/
├── src/
│   ├── api/
│   │   ├── amadeus_client.py      # Amadeus API wrapper
│   │   ├── rate_limiter.py        # Rate limiting (10/min, 100/hr)
│   │   ├── date_range_search.py   # Date combination logic
│   │   └── batch_search.py        # Batch API calls with progress
│   ├── models/
│   │   └── flight.py              # Data models
│   ├── ui/
│   │   └── app.py                 # Streamlit web interface
│   └── visualization/
│       └── heatmap.py             # Interactive charts
├── config/
│   └── settings.py                # Configuration
├── docs/
│   ├── features/                  # Feature documentation
│   ├── technical/                 # Technical guides
│   ├── GETTING_STARTED.md         # Beginner's guide
│   └── USAGE_GUIDE.md             # Complete usage instructions
├── test_*.py                      # Test scripts
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment template
```

## 📚 Documentation

- **[Getting Started](GETTING_STARTED.md)**: Setup and first search
- **[Usage Guide](USAGE_GUIDE.md)**: Complete feature walkthrough
- **[Quickstart](QUICKSTART.md)**: 5-minute intro

### Feature Documentation
- **[Multi-Airport Search](docs/features/FEATURE_MULTI_AIRPORT.md)**: Compare multiple airports
- **[Flexible Date Search](docs/features/FEATURE_DATE_RANGE.md)**: Date range comparison
- **[Trip Preferences](docs/features/FEATURE_TRIP_PREFERENCES.md)**: Duration strategies and time filters

## 🔧 Technology Stack

- **Backend**: Python 3.13
- **API**: [Amadeus for Developers](https://developers.amadeus.com/)
  - Free tier: 2000 API calls/month
  - Real-time data from 400+ airlines
  - No credit card required
- **Web Framework**: Streamlit 1.50.0
- **Data Processing**: pandas 2.3.3, numpy
- **Visualizations**: plotly 6.3.1, matplotlib
- **HTTP Client**: requests 2.32.3

## 💡 Tips & Best Practices

### API Quota Management
- Free tier provides ~66 calls/day
- Single date search: 1 API call per route
- Flexible search: calls = dates × routes
- Use **Smart Sampling** to reduce calls by 95%+

### Efficient Searching
1. Start with single date to verify routes
2. Use 2-3 airports per side (not 5+)
3. Enable smart sampling for date ranges
4. Set time filters before searching
5. Monitor your monthly API usage

### Best Value Searches
- **Budget airlines**: Often use secondary airports (EasyJet, Ryanair)
- **Multiple Swiss airports**: ZRH vs GVA vs BSL can differ significantly
- **London airports**: LHR, LGW, STN prices vary by 50%+
- **Weekday flexibility**: Midweek flights often cheaper

## 🛠️ Development

### Run Tests
```bash
# Test API connection
python test_amadeus_api.py

# Test date range logic
python test_date_range.py

# Test visualizations
python test_visualizations.py
```

### Code Style
- PEP 8 compliant
- Type hints where applicable
- Comprehensive error handling
- Detailed docstrings

## 🗺️ Roadmap

### Planned Features
- [ ] Flight tracking (save favorites)
- [ ] Price history database
- [ ] Price drop alerts
- [ ] Export results to CSV
- [ ] Email notifications
- [ ] Airport autocomplete
- [ ] Nearby airport finder
- [ ] Mobile-responsive design
- [ ] SerpApi integration (Google Flights alternative)

### Future Enhancements
- [ ] Multi-city searches
- [ ] Budget optimization (stay under $X)
- [ ] Carbon footprint calculations
- [ ] Hotel price integration
- [ ] Rental car comparison

## 🤝 Contributing

This is primarily a personal project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Credits

- **Original concept**: [FlightsPlot](https://github.com/isaacambrogetti/FlightsPlot) by Isaac Ambrogetti
- **APIs**: [Amadeus for Developers](https://developers.amadeus.com/)
- **Frameworks**: [Streamlit](https://streamlit.io/), [Plotly](https://plotly.com/)
- **Development**: Built with assistance from Claude (Anthropic)

## 📧 Contact

- **Author**: Isaac Ambrogetti
- **GitHub**: [@isaacambrogetti](https://github.com/isaacambrogetti)
- **Original Project**: [FlightsPlot](https://github.com/isaacambrogetti/FlightsPlot)

---

⭐ **Star this repo if you find it useful!** ⭐