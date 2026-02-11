#!/bin/bash

# Script to run the MCP server
# This script demonstrates how to start the MCP server with proper environment setup

echo "Starting Reddit MCP Server..."

# Set default environment variables if not already set
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://host.docker.internal:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-gpt-oss:20b}"
export PORT="${PORT:-5000}"

echo "Environment variables:"
echo "  OLLAMA_BASE_URL: $OLLAMA_BASE_URL"
echo "  OLLAMA_MODEL: $OLLAMA_MODEL"
echo "  PORT: $PORT"

echo ""
echo "Starting MCP server on port $PORT..."
echo "Server will be available at http://localhost:$PORT"
echo ""
echo "Available endpoints:"
echo "  GET /search?q={query}&limit={limit}&after={after}"
echo "  GET /posts/{post_id}"
echo "  GET /posts/{post_id}/comments?limit={limit}"
echo "  GET /posts/{post_id}/summary"
echo "  GET /trending?limit={limit}&after={after}"
echo "  GET /health"
echo "  GET /openapi.json"
echo ""
echo "Press Ctrl+C to stop the server"

# Run the MCP server directly with python3
python3 src/mcp_server.py

echo "Server stopped."
