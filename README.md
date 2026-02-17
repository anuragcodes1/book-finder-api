# Book Finder API

A modular Python REST API to search for books by author using the Open Library API. Hosted on Railway.

## Features
- Fetches ALL books using proper pagination (no arbitrary limits)
- Robust error handling with automatic retries
- Graceful degradation when API fails
- Input validation and sanitization
- Comprehensive logging for debugging
- Book cover images from Open Library
- Backend pagination (50 books per page)
- Consistent results with caching

## Features

- REST API for searching books by author name
- Fetches data from both Open Library and Google Books APIs
- Returns title, published year, and URL for each book
- Modular architecture with separate API clients
- Automatic deduplication of results
- Results sorted by publication year (newest first)
- Ready for Railway deployment

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web API

Start the server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

#### Endpoints

- `GET /` - API documentation
- `GET /health` - Health check
- `GET /api/books?author=<name>` - Search books by author

#### Example Request

```bash
curl "http://localhost:5000/api/books?author=Isaac%20Asimov"
```

#### Example Response

```json
{
  "author": "Isaac Asimov",
  "count": 45,
  "books": [
    {
      "title": "Foundation",
      "published_year": 1951,
      "url": "https://openlibrary.org/works/OL46125W",
      "source": "open_library"
    }
  ]
}
```

### Command Line

```bash
python book_finder.py "Author Name"
```

Example:
```bash
python book_finder.py "J.K. Rowling"
```

### As a Module

```python
from book_finder import search_books_by_author

books = search_books_by_author("Isaac Asimov")

for book in books:
    print(f"{book.title} ({book.published_year})")
    print(f"URL: {book.url}")
```

## Deploy to Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize and deploy:
```bash
railway init
railway up
```

4. Your API will be live at the Railway-provided URL

### Alternative: Deploy via GitHub

1. Push your code to GitHub
2. Go to [Railway](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect the Python app and deploy it

The `Procfile` and `runtime.txt` files configure Railway to run the Flask app with Gunicorn.

## Project Structure

```
.
├── book_finder.py          # Main entry point
├── models/
│   ├── __init__.py
│   └── book.py            # Book data model
├── api_clients/
│   ├── __init__.py
│   ├── open_library.py    # Open Library API client
│   └── google_books.py    # Google Books API client
├── utils/
│   ├── __init__.py
│   └── formatter.py       # Output formatting utilities
├── requirements.txt
└── README.md
```

## Architecture

The tool is designed with modularity in mind:

- **Models**: Data structures (Book class)
- **API Clients**: Separate clients for each API with consistent interface
- **Utils**: Formatting and helper functions
- **Main Module**: Orchestrates the search and deduplication

## Adding New APIs

To add a new book API:

1. Create a new client in `api_clients/`
2. Implement `get_books_by_author()` method returning `list[Book]`
3. Add the client to `book_finder.py`

Example:
```python
from api_clients.new_api import NewAPIClient

new_api = NewAPIClient()
new_books = new_api.get_books_by_author(author_name)
all_books.extend(new_books)
```
