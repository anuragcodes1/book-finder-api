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
    Get books by author.
    
    Query Parameters:
        author (str): The name of the author to search for
        
    Returns:
        JSON response with books list
    """
    author_name = request.args.get('author', '').strip()
    
    if not author_name:
        return jsonify({
            "error": "Missing required parameter: author",
            "usage": "/api/books?author=Author Name"
        }), 400
    
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
        
        # Build response with warnings if some sources failed
        response = {
            "author": author_name,
            "count": len(books),
            "books": format_json(books),
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
