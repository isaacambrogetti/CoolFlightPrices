# CoolFlightPrices - Extended Flight Price Tracker

This project extends the original [FlightsPlot](https://github.com/isaacambrogetti/FlightsPlot) project to directly fetch flight data from Skyscanner instead of relying on email updates.

## 🚧 Project Status: In Development

This is an extension branch that aims to implement:
- Direct Skyscanner data fetching (API or web scraping)
- Interactive UI for selecting dates and destinations
- Flight selection and tracking interface
- Real-time price monitoring

## Planned Features

### Phase 1: Direct Data Fetching
- [ ] Research Skyscanner API options (RapidAPI, official API, or web scraping)
- [ ] Implement data fetching module
- [ ] Handle authentication and rate limiting

### Phase 2: User Interface
- [ ] Date range selection UI
- [ ] Origin/destination selector
- [ ] Flight listing with details (times, airlines, prices)
- [ ] Flight tracking selection

### Phase 3: Tracking & Visualization
- [ ] Database/storage for tracked flights
- [ ] Price change notifications
- [ ] Enhanced visualizations from original project
- [ ] Export functionality

## Original Project

This extends the functionality of [FlightsPlot](https://github.com/isaacambrogetti/FlightsPlot) which parses Skyscanner email alerts and visualizes price trends.

## Technology Stack (Planned)

- **Backend**: Python 3.8+
- **Data Fetching**: 
  - Option 1: Skyscanner RapidAPI
  - Option 2: Web scraping (Selenium/Playwright)
- **UI**: 
  - Option 1: Streamlit (simple web UI)
  - Option 2: Flask + HTML/CSS/JS
  - Option 3: PyQt/Tkinter (desktop app)
- **Data Storage**: SQLite or JSON files
- **Visualization**: matplotlib, plotly

## Setup (Coming Soon)

Instructions will be added as development progresses.

## Notes

This is a work-in-progress project. The implementation approach will be determined based on:
- Skyscanner API availability and costs
- Technical feasibility of web scraping
- User experience requirements
