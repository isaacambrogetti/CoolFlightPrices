# CoolFlightPrices - Development Plan

## Overview
Extension of FlightsPlot to fetch flight data directly from Skyscanner with an interactive UI.

## Research Phase

### 1. Skyscanner Data Access Options

#### Option A: RapidAPI Skyscanner API
- **Pros**: 
  - Official API access
  - Structured data
  - Reliable
  - Legal
- **Cons**: 
  - May have costs
  - Rate limits
  - Requires API key
- **Action**: Research pricing and capabilities

#### Option B: Web Scraping
- **Pros**: 
  - Free
  - Direct access
- **Cons**: 
  - Against ToS (legal risk)
  - Fragile (breaks when site changes)
  - May need to handle anti-bot measures
  - Ethical concerns
- **Action**: Last resort only

#### Option C: Alternative Flight APIs
- **Kiwi.com API**
- **Amadeus API**
- **Aviationstack**
- **Action**: Compare features and costs

### 2. UI Framework Selection

#### Option A: Streamlit
- **Pros**: 
  - Very quick development
  - Python-only
  - Great for data apps
  - Built-in widgets
- **Cons**: 
  - Less customization
  - Web-based only
- **Best for**: Rapid prototyping

#### Option B: Flask + Web UI
- **Pros**: 
  - Full control
  - Professional look
  - Customizable
- **Cons**: 
  - More development time
  - Need HTML/CSS/JS knowledge
- **Best for**: Production app

#### Option C: PyQt/Tkinter
- **Pros**: 
  - Desktop application
  - No web server needed
  - Native feel
- **Cons**: 
  - More complex
  - Distribution challenges
- **Best for**: Desktop-first approach

### 3. Data Storage

#### Option A: SQLite
- **Pros**: 
  - Relational
  - SQL queries
  - No server needed
- **Use for**: Tracked flights, price history

#### Option B: JSON Files
- **Pros**: 
  - Simple
  - Human-readable
  - Good for config
- **Use for**: User preferences, simple data

## Implementation Phases

### Phase 1: Research & Setup (Current)
- [ ] Set up project structure ✓
- [ ] Research Skyscanner API options
- [ ] Decide on UI framework
- [ ] Create proof-of-concept for data fetching
- [ ] Test API rate limits and costs

### Phase 2: Core Data Fetching Module
- [ ] Implement API client
- [ ] Create flight search function
  - Input: origin, destination, dates
  - Output: list of available flights
- [ ] Handle errors and rate limiting
- [ ] Cache responses appropriately
- [ ] Write tests

### Phase 3: Data Models & Storage
- [ ] Design database schema
  - Tracked flights
  - Price history
  - User preferences
- [ ] Implement data models
- [ ] Create database helpers
- [ ] Migration system

### Phase 4: Basic UI - Search Interface
- [ ] Date picker (departure & return)
- [ ] Origin/destination input
- [ ] Search button
- [ ] Display flight results
  - Flight times
  - Airlines
  - Prices
  - Duration
  - Stops

### Phase 5: Tracking Interface
- [ ] "Track this flight" button for each result
- [ ] View currently tracked flights
- [ ] Remove from tracking
- [ ] Set price alerts (optional)

### Phase 6: Background Monitoring
- [ ] Scheduled price checks
- [ ] Compare with previous prices
- [ ] Store price history
- [ ] Notification system (email/desktop)

### Phase 7: Visualization
- [ ] Port visualization from original project
- [ ] Enhanced plots with more data
- [ ] Interactive charts (if using Plotly)
- [ ] Export capabilities

### Phase 8: Polish & Features
- [ ] Error handling
- [ ] Loading states
- [ ] User settings
- [ ] Documentation
- [ ] Testing

## File Structure (Planned)

```
CoolFlightPrices/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── config/
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── skyscanner_client.py
│   │   └── rate_limiter.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── flight.py
│   │   └── tracking.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_manager.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py
│   └── visualization/
│       ├── __init__.py
│       └── plotter.py
├── tests/
│   └── __init__.py
└── data/
    └── .gitkeep
```

## Next Steps

1. **Immediate**: Research RapidAPI Skyscanner options
2. **Then**: Create a simple proof-of-concept that fetches one flight
3. **Decide**: Choose UI framework based on complexity vs. speed tradeoff
4. **Build**: Start with minimal viable product (MVP)

## Questions to Answer

- [ ] What's the budget for API costs?
- [ ] Desktop app vs. web app preference?
- [ ] How frequently should flights be checked?
- [ ] What notification methods are preferred?
- [ ] Should it support multiple users or single user?

## Resources

- [RapidAPI Skyscanner](https://rapidapi.com/skyscanner/api/skyscanner-flight-search)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Kiwi.com Tequila API](https://tequila.kiwi.com/)
