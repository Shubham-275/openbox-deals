# Open-Box Deals Aggregator v5
## Warehouse Receipt Edition - Production Ready

A real-time open-box/refurbished deals aggregator with live browser streaming. Features a retro warehouse receipt UI theme.

```
┌─────────────────────────────────────────────────┐
│          OPEN-BOX DEALS                         │
│       Warehouse Outlet Pricing                  │
│         |||||||||||||||||||                     │
│           *38472910*                            │
├─────────────────────────────────────────────────┤
│ [Search Inventory___________] [Max $] [SEARCH]  │
├─────────────────────────────────────────────────┤
│  AMAZON   │  BEST BUY │  NEWEGG  │  BACKMARKET  │
│  ● LIVE   │  ● LIVE   │  ○ WAIT  │  ○ WAIT      │
├─────────────────────────────────────────────────┤
│ ITEM DESCRIPTION              WAS        NOW    │
│─────────────────────────────────────────────────│
│ AirPods Pro 2nd Gen         $249.00   $189.99  │
│ VIA AMAZON WAREHOUSE        [OPEN BOX]  (24%)   │
├─ ✂ ─────────────────────────────────────────────┤
│ ITEMS FOUND:                              24    │
│ AVG SAVINGS:                           27% OFF  │
└─────────────────────────────────────────────────┘
```

## Features

- 🧾 **Warehouse Receipt UI** — Retro thermal printer aesthetic
- 🖥️ **8 Live Browser Windows** — Watch Mino scrape in real-time
- 💰 **Dynamic Savings** — Per-item and aggregate calculations
- ⚡ **Parallel Scraping** — All 8 sites simultaneously
- 🔒 **Production Security** — Rate limiting, XSS protection, input validation

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

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Warehouse Receipt UI |
| `GET /api/search/live?q=airpods` | SSE stream with live browsers |
| `GET /api/search/status` | Check if user can search (rate limit) |
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

---

## V5 Security & Production Fixes

### Security
- ✅ **Rate Limiting**: 5 requests/minute per IP (in-memory, use Redis for multi-instance)
- ✅ **XSS Protection**: URL validation (only http/https allowed in product links)
- ✅ **Input Validation**: Query length limit (100 chars), dangerous character filtering
- ✅ **Product Sanitization**: All scraped data sanitized before sending to frontend

### Reliability  
- ✅ **Request Deduplication**: Prevents concurrent searches from same user
- ✅ **Session Health**: Auto-refreshes aiohttp session every hour
- ✅ **Strict Price Filtering**: Excludes items with unparseable prices when filter is set
- ✅ **Global Timeout**: 2 minute max search time (prevents orphaned tasks)
- ✅ **Per-Site Timeout**: 90 seconds max per retailer

### Frontend
- ✅ **Spam Prevention**: Disables search button during active search
- ✅ **Rate Limit UI**: Shows user-friendly error when rate limited
- ✅ **URL Validation**: Client-side XSS protection for product links

---

## V4 Changelog (Previous)

- Fixed `resultJson` parsing (Mino API response format)
- Handles AI responses with markdown code blocks
- Proper SSE buffering (no more split packet issues)
- Connection pooling (single aiohttp session)
- Stricter AI goals for cleaner JSON output

## License

MIT
