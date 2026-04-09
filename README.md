# Game Price Tracker

A web application for tracking game prices on various sites over time. Search for games, add them to your watchlist, and monitor price changes — including discounts — with an automatically updating price history.

---

## Features

- **Game Search** — Search by title and browse results
- **Price Tracking** — Track a game's current price, original price, and active discount percentage
- **Price History** — Stores a full history of price snapshots per game with timestamps
- **Price Change Calculation** — Compares the two most recent price records and surfaces the difference and percentage change
- **Automatic Refresh** — A background scheduler rechecks prices for all tracked games every hour
- **Retailer Search (Loaded)** — Searches the Loaded retailer alongside Steam results using dynamically resolved Algolia credentials

---

## Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| Framework      | FastAPI 0.135                     |
| ORM            | SQLAlchemy 2.0                    |
| Database       | PostgreSQL (via `DATABASE_URL`)   |
| Scheduler      | APScheduler 3.11                  |
| Web Scraping   | cloudscraper 1.2, BeautifulSoup 4 |
| Templating     | Jinja2 (via FastAPI)              |
| Config         | python-dotenv 1.2                 |

---

## Project Structure

```
app/
├── main.py                  # FastAPI application entry point, lifespan hooks
├── db/
│   ├── database.py          # SQLAlchemy engine and session setup
│   └── init_db.py           # Creates database tables from ORM models
├── models/
│   ├── game.py              # Game ORM model (id, steam_app_id, name, steam_url)
│   └── price_history.py     # PriceHistory ORM model (price snapshots with timestamps)
├── routes/
│   └── games.py             # All HTTP route handlers
├── services/
│   ├── game_service.py      # Database CRUD operations for games and price records
│   ├── price_service.py     # Price comparison and change calculation logic
│   ├── steam_service.py     # Steam Store API integration
│   ├── loaded_service.py    # Loaded retailer search via Algolia
│   └── scheduler_service.py # Background price refresh scheduler
└── templates/
    ├── index.html           # Home / search page
    ├── search_results.html  # Search results page
    └── tracked_games.html   # Tracked games watchlist page
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (or another SQLAlchemy-compatible database)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/game_price_tracker.git
   cd game_price_tracker
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example environment file and fill in your values:

   ```bash
   cp .env.example .env
   ```

   | Variable       | Description                                    |
   |----------------|------------------------------------------------|
   | `DATABASE_URL` | SQLAlchemy connection string for your database |

   Example for PostgreSQL:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/game_price_tracker
   ```

5. **Initialise the database**

   ```bash
   python -m app.db.init_db
   ```

6. **Run the development server**

   ```bash
   uvicorn app.main:app --reload
   ```

   The application will be available at `http://127.0.0.1:8000`.

---

## API Endpoints

| Method | Path                          | Description                                       |
|--------|-------------------------------|---------------------------------------------------|
| GET    | `/`                           | Home page                                         |
| GET    | `/search?query=<title>`       | Search Steam for a game (JSON response)           |
| POST   | `/search-page`                | Search Steam and render results page              |
| POST   | `/track`                      | Start tracking a game by Steam app ID (JSON)      |
| POST   | `/track-page`                 | Start tracking a game, redirects to watchlist     |
| GET    | `/tracked-games`              | List all tracked games with latest prices (JSON)  |
| GET    | `/tracked-games-page`         | Render the tracked games watchlist page           |
| POST   | `/recheck-price/{game_id}`    | Manually trigger a price recheck for one game     |

---

## Background Scheduler

On startup, APScheduler launches a background job (`auto_recheck_all_games`) that iterates over every tracked game and fetches its latest price from the Steam API. This job runs on a **60-minute interval** and is stopped cleanly when the application shuts down.

---

## Environment Variables

| Variable       | Required | Description                            |
|----------------|----------|----------------------------------------|
| `DATABASE_URL` | Yes      | SQLAlchemy-compatible connection string |

See [.env.example](.env.example) for a template.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

---

## License

This project is licensed under the MIT License.
