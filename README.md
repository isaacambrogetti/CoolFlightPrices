# CoolFlightPrices - Extended Flight Price Tracker

This project extends the original [FlightsPlot](https://github.com/isaacambrogetti/FlightsPlot) project to directly fetch flight data from Amadeus API instead of relying on email updates.

## ✨ Current Status

**✅ MVP Ready!** Basic flight search with Streamlit UI is working.

### Working Features:
- ✅ Amadeus API integration
- ✅ Flight search (one-way & roundtrip)

## Technology Stack

- **Backend**: Python 3.8+
- **API**: Amadeus (free tier: 2000 calls/month)
- **UI**: Streamlit (web-based)
- **Future**: SerpApi for Google Flights scraping
- **Data Storage**: SQLite (coming soon)
- **Visualization**: matplotlib, plotly

## Features

### Current
- Search flights by route and date
- One-way and roundtrip support
- Price comparison
- Flight details (times, airlines, stops, duration)
- Responsive web UI

### Planned
- Track specific flights
- Price history storage
- Price drop alerts
- Visualization charts (port from original FlightsPlot)
- Export to CSV
- Multi-city searches

## API Information

**Amadeus for Developers**
- Free tier: 2000 API calls/month
- Real flight data from 400+ airlines
- No credit card required
- Sign up: https://developers.amadeus.com/

**Future: SerpApi (Google Flights)**
- Web scraping alternative
- More comprehensive data
- Will be added as secondary source

## Project Structure

```
CoolFlightPrices/
├── src/
│   ├── api/
│   │   ├── amadeus_client.py    # Amadeus API integration
│   │   └── rate_limiter.py      # Rate limiting
│   ├── models/
│   │   └── flight.py            # Data models
│   └── ui/
│       └── app.py               # Streamlit UI
├── config/
│   └── settings.py              # Configuration
├── test_amadeus_api.py          # API test script
└── data/                        # Storage (future)
```

## Contributing

This is a personal project, but feedback and suggestions are welcome!

## License

MIT License - feel free to use and modify

## Credits

- Original project: [FlightsPlot](https://github.com/isaacambrogetti/FlightsPlot)
- Built with: Amadeus API, Streamlit, Python
- Made with ❤️ and AI assistance (Claude)