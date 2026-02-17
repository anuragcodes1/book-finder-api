"""Flask API for Book Finder."""

from flask import Flask, jsonify, request, render_template
from book_finder import search_books_by_author
from utils.formatter import format_json
import os

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
    author_name = request.args.get('author')
    
    if not author_name:
        return jsonify({
            "error": "Missing required parameter: author",
            "usage": "/api/books?author=Author Name"
        }), 400
    
    try:
        books = search_books_by_author(author_name)
        
        return jsonify({
            "author": author_name,
            "count": len(books),
            "books": format_json(books)
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
