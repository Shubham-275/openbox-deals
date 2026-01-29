# Open-Box Deals Aggregator

**Warehouse Receipt Edition** — A retro-styled deal finder with live browser streaming and dynamic savings calculation.

```
┌─────────────────────────────────────────────────┐
│          OPEN-BOX DEALS                         │
│       Warehouse Outlet Pricing                  │
│         |||||||||||||||||||                     │
│           *38472910*                            │
├─────────────────────────────────────────────────┤
│ [Search Inventory___________] [Max $] [SEARCH]  │
├─────────────────────────────────────────────────┤
│ TXN #38472910    01/29/2026 14:32:07   8 SITES  │
├─────────────────────────────────────────────────┤
│  AMAZON   │  BEST BUY │  NEWEGG  │  BACKMARKET  │
│  ● LIVE   │  ● LIVE   │  ○ WAIT  │  ○ WAIT      │
│ [browser] │ [browser] │ [ready]  │ [ready]      │
├─────────────────────────────────────────────────┤
│ ITEM DESCRIPTION              WAS        NOW    │
│─────────────────────────────────────────────────│
│ AirPods Pro 2nd Gen         $249.00   $189.99  │
│ Condition: LIKE NEW                  SAVE $59   │
│ VIA AMAZON WAREHOUSE        [OPEN BOX]  (24%)   │
│.............................................    │
├─ ✂ ─────────────────────────────────────────────┤
│ ITEMS FOUND:                              24    │
│ SITES SEARCHED:                         8 / 8   │
│ SEARCH TIME:                         42.3 SEC   │
│ AVG SAVINGS:                           27% OFF  │
│─────────────────────────────────────────────────│
│ POTENTIAL SAVINGS:               UP TO 45% OFF  │
├─────────────────────────────────────────────────┤
│                   ★ ★ ★                         │
│         THANK YOU FOR SHOPPING SMART            │
│          DEALS REFRESH EVERY 30 MIN             │
│                   ★ ★ ★                         │
└─────────────────────────────────────────────────┘
```

## Features

- 🧾 **Warehouse Receipt UI** — Retro thermal printer aesthetic
- 🖥️ **8 Live Browser Windows** — Watch Mino scrape in real-time
- 💰 **Dynamic Savings** — Per-item and aggregate calculations
- ⚡ **Parallel Scraping** — All 8 sites simultaneously
- 📊 **Smart Sorting** — Best deals (highest % off) first

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Set API key
export MINO_API_KEY=your_key

# Run
uvicorn app.main:app --reload

# Open
open http://localhost:8000
```

## Savings Calculation

```javascript
// Per Product
original_price = $249.00
sale_price = $189.99
savings_amount = $249.00 - $189.99 = $59.01
savings_percent = ($59.01 / $249.00) × 100 = 24%

// Aggregate (Footer)
max_percent = highest % across all products
avg_percent = average % across products with savings
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Warehouse Receipt UI |
| `GET /api/search/live?q=airpods` | SSE stream with live browsers |
| `GET /api/sites` | List all supported sites |

## Supported Sites

| Site | Speciality |
|------|------------|
| Amazon Warehouse | Everything |
| Best Buy Outlet | Electronics |
| Newegg Open Box | PC Parts |
| BackMarket | Phones, Refurbished |
| B&H Photo | Cameras, Audio |
| eBay Refurbished | Certified Items |
| Target Clearance | General Deals |
| Micro Center | PC Components |

## Deploy to Railway

1. Push to GitHub
2. Connect in Railway
3. Add `MINO_API_KEY` env variable
4. Deploy ✅

## Tech Stack

- **Backend:** FastAPI + aiohttp
- **Frontend:** Vanilla JS + IBM Plex Mono
- **Scraping:** Mino API (parallel SSE streams)
- **Styling:** Custom receipt/thermal printer CSS

## License

MIT
