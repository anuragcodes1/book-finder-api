"""Flask API for Book Finder."""

from flask import Flask, jsonify, request, render_template
from book_finder import search_books_by_author
from utils.formatter import format_json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def home():
    """Home page with search UI."""
    return render_template('index.html')


@app.route('/api')
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        "name": "Book Finder API",
        "version": "1.0.0",
        "endpoints": {
            "/": "Web UI for searching books",
            "/api": "API documentation",
            "/health": "Health check",
            "/api/books": "Search books by author (GET with ?author=name)"
        },
        "usage": {
            "example": "/api/books?author=Isaac Asimov",
            "parameters": {
                "author": "Author name (required)"
            }
        }
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route('/api/books', methods=['GET'])
def get_books():
    """
    Get books by author with pagination support.
    
    Query Parameters:
        author (str): The name of the author to search for
        page (int): Page number (default: 1)
        limit (int): Books per page (default: 50, max: 100)
        
    Returns:
        JSON response with paginated books list
    """
    author_name = request.args.get('author', '').strip()
    
    if not author_name:
        return jsonify({
            "error": "Missing required parameter: author",
            "usage": "/api/books?author=Author Name&page=1&limit=50"
        }), 400
    
    # Get pagination parameters
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
    except ValueError:
        return jsonify({
            "error": "Invalid pagination parameters",
            "message": "page and limit must be integers"
        }), 400
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if limit < 1:
        limit = 50
    if limit > 100:
        limit = 100
    
    try:
        result = search_books_by_author(author_name)
        
        # Check if there was a validation error
        if "error" in result and not result.get("books"):
            return jsonify({
                "error": result["error"],
                "author": author_name
            }), 400
        
        books = result["books"]
        sources = result["sources"]
        
        # Check if all sources failed
        all_failed = all(
            source.get("status") == "error" 
            for source in sources.values()
        )
        
        if all_failed and len(books) == 0:
            return jsonify({
                "error": "All book sources are currently unavailable",
                "author": author_name,
                "sources": sources,
                "message": "Please try again later"
            }), 503
        
        # Calculate pagination
        total_books = len(books)
        total_pages = (total_books + limit - 1) // limit  # Ceiling division
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get paginated books
        paginated_books = books[start_idx:end_idx]
        
        # Build response with pagination info
        response = {
            "author": author_name,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_books": total_books,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "books": format_json(paginated_books),
            "sources": sources
        }
        
        # Add warning if some sources failed
        failed_sources = [
            name for name, info in sources.items() 
            if info.get("status") == "error"
        ]
        
        if failed_sources:
            response["warning"] = f"Some sources unavailable: {', '.join(failed_sources)}"
            response["partial_results"] = True
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Unexpected error in get_books: {e}", exc_info=True)
        return jsonify({
            "error": "An unexpected error occurred",
            "message": "Please try again later"
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
