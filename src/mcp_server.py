#!/usr/bin/env python3
"""
MCP Server for Reddit CLI
Exposes Reddit querying capabilities through MCP endpoints with resilience and retry logic.
"""

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.8.223:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
REDDIT_BASE_URL = "https://www.reddit.com"

class RedditClient:
    """Client for interacting with Reddit API with retry logic"""

    def __init__(self):
        self.base_url = REDDIT_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "RedditCLI/0.1 by User"})

    def _make_request_with_retry(self, url: str, params: Dict = None, max_retries: int = 3, 
                               retry_delay: float = 1.0) -> requests.Response:
        """
        Make HTTP request with exponential backoff retry logic
        
        Args:
            url: Request URL
            params: Request parameters
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.RequestException: If all retries fail
        """
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All {max_retries + 1} attempts failed for {url}")
                    raise e

    def search_posts(
        self, query: str, limit: int = 15, after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for Reddit posts matching the query with retry logic

        Args:
            query: Search terms
            limit: Number of posts to return (default 15)
            after: Pagination token for next page

        Returns:
            Dictionary containing search results and pagination info
        """
        params = {"q": query, "limit": limit, "sort": "hot", "type": "link"}

        if after:
            params["after"] = after

        try:
            response = self._make_request_with_retry(
                f"{self.base_url}/search.json", params=params
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch posts: {str(e)}")

    def get_post_details(self, post_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific post with retry logic

        Args:
            post_id: Reddit post ID

        Returns:
            Dictionary with post details
        """
        try:
            response = self._make_request_with_retry(
                f"{self.base_url}/by_id/t3_{post_id}.json"
            )
            data = response.json()

            # Extract post from the response structure
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("data", {})
            elif isinstance(data, dict):
                return data.get("data", {})

            return {}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch post details: {str(e)}")

    def get_post_comments(self, post_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get comments for a specific post with retry logic

        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch

        Returns:
            List of comment dictionaries
        """
        try:
            response = self._make_request_with_retry(
                f"{self.base_url}/comments/{post_id}.json",
                params={"limit": limit}
            )
            data = response.json()

            # Extract comments from the nested structure
            comments = []
            if isinstance(data, list) and len(data) > 1:
                comment_data = data[1].get("data", {}).get("children", [])
                for child in comment_data:
                    comment = child.get("data", {})
                    # Flatten the comment structure to include author and body
                    comments.append(
                        {
                            "author": comment.get("author", "unknown"),
                            "body": comment.get("body", ""),
                            "score": comment.get("score", 0),
                            "created_utc": comment.get("created_utc", 0),
                        }
                    )

            return comments
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch comments: {str(e)}")

    def format_timestamp(self, timestamp: int) -> str:
        """
        Format Unix timestamp into readable date string

        Args:
            timestamp: Unix timestamp

        Returns:
            Formatted date string
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


class AIClient:
    """Client for interacting with Ollama AI API with retry logic"""

    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.session = requests.Session()

    def _make_request_with_retry(self, url: str, json_data: Dict = None, max_retries: int = 3, 
                               retry_delay: float = 1.0) -> requests.Response:
        """
        Make HTTP request with exponential backoff retry logic
        
        Args:
            url: Request URL
            json_data: JSON data to send
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.RequestException: If all retries fail
        """
        for attempt in range(max_retries + 1):
            try:
                response = self.session.post(url, json=json_data, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All {max_retries + 1} attempts failed for {url}")
                    raise e

    def generate_summary(self, post_body: str, comments: List[str]) -> str:
        """
        Generate AI summary of a post with comments and retry logic

        Args:
            post_body: The main body text of the post
            comments: List of comment strings

        Returns:
            Generated summary from AI
        """
        # Select 100 random comments (or all if less than 100)
        selected_comments = comments[:100]

        # Format prompt for the AI model
        prompt = self._create_prompt(post_body, selected_comments)

        try:
            response = self._make_request_with_retry(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False}
            )
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to generate AI summary: {str(e)}")

    def _create_prompt(self, post_body: str, comments: List[str]) -> str:
        """
        Create a formatted prompt for the AI with post and comments

        Args:
            post_body: The main body text of the post
            comments: List of comment strings

        Returns:
            Formatted prompt string
        """
        # Join comments into a single string with proper formatting
        comments_text = "\n".join(
            [f"Comment {i + 1}: {comment}" for i, comment in enumerate(comments)]
        )

        if not comments_text:
            comments_text = "No comments available."

        prompt = f"""
        Summarize the following Reddit post and its comments in 2-3 sentences.

        Post:
        {post_body}

        Comments:
        {comments_text}

        Summary:
        """

        return prompt


# Initialize clients
reddit_client = RedditClient()
ai_client = AIClient()

@app.route('/search', methods=['GET'])
def search_posts():
    """Search for Reddit posts"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 15))
        after = request.args.get('after', None)
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
            
        data = reddit_client.search_posts(query, limit, after)
        
        # Extract posts from response
        posts = []
        
        # Check if we have data in the expected response format
        if "data" in data and "children" in data["data"]:
            for child in data["data"]["children"]:
                post_data = child.get("data", {})
                if post_data:
                    posts.append(
                        {
                            "id": post_data.get("id"),
                            "title": post_data.get("title", "No title"),
                            "subreddit": post_data.get("subreddit", "unknown"),
                            "created_utc": post_data.get("created_utc", 0),
                            "url": post_data.get("url", ""),
                            "body": post_data.get(
                                "selftext", post_data.get("body", "")
                            ),
                            "score": post_data.get("score", 0),
                        }
                    )
            
            # Get the after token for pagination
            after_token = data["data"].get("after")
        else:
            after_token = None
            
        response_data = {
            "posts": posts,
            "after": after_token,
            "query": query,
            "limit": limit
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in search_posts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/posts/<post_id>', methods=['GET'])
def get_post_details(post_id):
    """Get detailed information about a specific post"""
    try:
        post_data = reddit_client.get_post_details(post_id)
        
        if not post_data:
            return jsonify({"error": "Post not found"}), 404
            
        # Format the response
        response_data = {
            "id": post_data.get("id"),
            "title": post_data.get("title", "No title"),
            "subreddit": post_data.get("subreddit", "unknown"),
            "created_utc": post_data.get("created_utc", 0),
            "url": post_data.get("url", ""),
            "body": post_data.get("selftext", post_data.get("body", "")),
            "score": post_data.get("score", 0),
            "author": post_data.get("author", "unknown"),
            "permalink": post_data.get("permalink", ""),
            "num_comments": post_data.get("num_comments", 0)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_post_details: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/posts/<post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """Get comments for a specific post"""
    try:
        limit = int(request.args.get('limit', 100))
        comments = reddit_client.get_post_comments(post_id, limit)
        
        response_data = {
            "post_id": post_id,
            "comments": comments,
            "count": len(comments)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_post_comments: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/posts/<post_id>/summary', methods=['GET'])
def get_post_summary(post_id):
    """Get AI-generated summary for a post"""
    try:
        # First get the post details
        post_data = reddit_client.get_post_details(post_id)
        if not post_data:
            return jsonify({"error": "Post not found"}), 404
            
        # Get comments
        comments = reddit_client.get_post_comments(post_id, limit=100)
        
        # Generate summary
        post_body = post_data.get("selftext", post_data.get("body", ""))
        comment_bodies = [comment.get("body", "") for comment in comments]
        
        summary = ai_client.generate_summary(post_body, comment_bodies)
        
        response_data = {
            "post_id": post_id,
            "summary": summary,
            "post_title": post_data.get("title", "No title"),
            "subreddit": post_data.get("subreddit", "unknown")
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_post_summary: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/trending', methods=['GET'])
def get_trending():
    """Get trending posts"""
    try:
        limit = int(request.args.get('limit', 15))
        after = request.args.get('after', None)
        
        # Use the same search parameters but with different sort
        params = {"q": "all", "limit": limit, "sort": "top", "type": "link"}
        
        if after:
            params["after"] = after
            
        data = reddit_client.search_posts("all", limit, after)
        
        # Extract posts from response
        posts = []
        
        # Check if we have data in the expected response format
        if "data" in data and "children" in data["data"]:
            for child in data["data"]["children"]:
                post_data = child.get("data", {})
                if post_data:
                    posts.append(
                        {
                            "id": post_data.get("id"),
                            "title": post_data.get("title", "No title"),
                            "subreddit": post_data.get("subreddit", "unknown"),
                            "created_utc": post_data.get("created_utc", 0),
                            "url": post_data.get("url", ""),
                            "body": post_data.get(
                                "selftext", post_data.get("body", "")
                            ),
                            "score": post_data.get("score", 0),
                        }
                    )
            
            # Get the after token for pagination
            after_token = data["data"].get("after")
        else:
            after_token = None
            
        response_data = {
            "posts": posts,
            "after": after_token,
            "limit": limit
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_trending: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "reddit-mcp-server"})


@app.route('/openapi.json', methods=['GET'])
def openapi_spec():
    """Serve OpenAPI specification"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Reddit MCP API",
            "version": "1.0.0",
            "description": "API for querying Reddit posts with MCP server capabilities"
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/search": {
                "get": {
                    "summary": "Search Reddit posts",
                    "description": "Search for Reddit posts by query term",
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Search query"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 15
                            },
                            "description": "Number of posts to return"
                        },
                        {
                            "name": "after",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Pagination token"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "posts": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "subreddit": {"type": "string"},
                                                        "created_utc": {"type": "integer"},
                                                        "url": {"type": "string"},
                                                        "body": {"type": "string"},
                                                        "score": {"type": "integer"}
                                                    }
                                                }
                                            },
                                            "after": {"type": "string"},
                                            "query": {"type": "string"},
                                            "limit": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/posts/{post_id}": {
                "get": {
                    "summary": "Get post details",
                    "description": "Get detailed information about a specific post",
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Reddit post ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "subreddit": {"type": "string"},
                                            "created_utc": {"type": "integer"},
                                            "url": {"type": "string"},
                                            "body": {"type": "string"},
                                            "score": {"type": "integer"},
                                            "author": {"type": "string"},
                                            "permalink": {"type": "string"},
                                            "num_comments": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/posts/{post_id}/comments": {
                "get": {
                    "summary": "Get post comments",
                    "description": "Get comments for a specific post",
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Reddit post ID"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 100
                            },
                            "description": "Maximum number of comments to return"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "post_id": {"type": "string"},
                                            "comments": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "author": {"type": "string"},
                                                        "body": {"type": "string"},
                                                        "score": {"type": "integer"},
                                                        "created_utc": {"type": "integer"}
                                                    }
                                                }
                                            },
                                            "count": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/posts/{post_id}/summary": {
                "get": {
                    "summary": "Get AI summary",
                    "description": "Get AI-generated summary for a post",
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Reddit post ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "post_id": {"type": "string"},
                                            "summary": {"type": "string"},
                                            "post_title": {"type": "string"},
                                            "subreddit": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/trending": {
                "get": {
                    "summary": "Get trending posts",
                    "description": "Get trending Reddit posts",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 15
                            },
                            "description": "Number of posts to return"
                        },
                        {
                            "name": "after",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Pagination token"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "posts": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "subreddit": {"type": "string"},
                                                        "created_utc": {"type": "integer"},
                                                        "url": {"type": "string"},
                                                        "body": {"type": "string"},
                                                        "score": {"type": "integer"}
                                                    }
                                                }
                                            },
                                            "after": {"type": "string"},
                                            "limit": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "summary": "Health check",
                    "description": "Check if the service is running",
                    "responses": {
                        "200": {
                            "description": "Service is healthy"
                        }
                    }
                }
            }
        }
    }
    
    return jsonify(spec)


def main():
    """Main function to start the MCP server"""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Reddit MCP Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    main()