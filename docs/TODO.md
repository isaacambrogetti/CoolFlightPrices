# TODO List

## Immediate Next Steps

### 1. API Research (Priority: HIGH)
- [ ] Sign up for RapidAPI account
- [ ] Check Skyscanner API on RapidAPI
  - [ ] Pricing tiers
  - [ ] Rate limits
  - [ ] Available endpoints
- [ ] Test Kiwi.com API as alternative
- [ ] Create simple test script to fetch one flight

### 2. Choose UI Framework (Priority: HIGH)
- [ ] Decide: Streamlit vs Flask vs Desktop
- [ ] Recommendation: Start with Streamlit for speed
- [ ] Install and test basic UI

### 3. Implement Basic Search (Priority: MEDIUM)
- [ ] Connect API client to chosen provider
- [ ] Implement search_flights() method
- [ ] Parse and normalize response data
- [ ] Display results in UI

### 4. Database Setup (Priority: MEDIUM)
- [ ] Design schema for tracked flights
- [ ] Implement SQLite database
- [ ] Create CRUD operations
- [ ] Add price history table

### 5. Tracking Functionality (Priority: LOW)
- [ ] "Add to tracking" feature
- [ ] View tracked flights
- [ ] Manual refresh prices
- [ ] Remove from tracking

### 6. Background Monitoring (Priority: LOW)
- [ ] Scheduled price checks
- [ ] Price change detection
- [ ] Notification system

### 7. Visualization (Priority: LOW)
- [ ] Port plotting code from original FlightsPlot
- [ ] Adapt to new data structure
- [ ] Interactive charts

## Questions to Resolve

- [ ] **Budget**: What's acceptable for API costs?
- [ ] **Frequency**: How often check prices? (hourly, daily?)
- [ ] **Notifications**: Email, desktop, or in-app only?
- [ ] **Deployment**: Local app or hosted web app?
- [ ] **Users**: Single user or multi-user?

## Code Structure Status

✅ Basic project structure
✅ Data models defined
✅ API client interface designed
✅ Rate limiter implemented
✅ Configuration system
❌ Actual API implementation
❌ Database layer
❌ UI implementation
❌ Tracking logic
❌ Visualization
❌ Tests

## Files Created

1. `README.md` - Project overview
2. `PROJECT_PLAN.md` - Detailed implementation plan
3. `RESEARCH.md` - API research notes
4. `.gitignore` - Git ignore rules
5. `requirements.txt` - Python dependencies
6. `.env.example` - Environment variables template
7. `src/api/skyscanner_client.py` - API client skeleton
8. `src/api/rate_limiter.py` - Rate limiting utility
9. `src/models/flight.py` - Data models
10. `config/settings.py` - Configuration management

## Commands to Run

```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (once we add more)
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Then edit .env with your API keys

# Run tests (when we have them)
pytest

# Run the app (when we build it)
python -m src.ui.app  # or streamlit run src/ui/app.py
```

## Git Workflow

```bash
# Link to original repo as upstream (for reference)
git remote add upstream https://github.com/isaacambrogetti/FlightsPlot.git

# Your development branch
git checkout -b feature/api-integration

# Regular commits
git add .
git commit -m "Description"
```
