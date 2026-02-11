# Reddit CLI

A command-line interface for browsing Reddit posts with search capabilities, interactive post viewing, and AI-powered summarization.

## Features

- **Search Functionality**: Search for Reddit posts by keyword/terms
- **Results Display**: Table view showing:
  - Post number
  - Subreddit name
  - Post creation date
  - Post title (main column)
- **Post Navigation**: Click on post number to view full post details
- **Comments Viewer**: Cycle through comments using 'c' key
- **AI Integration**: Get AI-generated summaries using Ollama API
- **Pagination**: Navigate between pages of results ('n' key)
- **MCP Server**: REST API endpoints for Reddit querying with resilience and retry logic

## Project Structure

```
reddit-cli/
├── src/
│   ├── __init__.py
│   ├── main.py          # Main application entrypoint
│   ├── mcp_server.py    # MCP server implementation with REST endpoints
│   └── ai_client.py     # Ollama AI integration
├── tests/
│   └── test_cli.py      # Unit tests
├── setup.sh             # Setup script for environment
├── run.sh               # Run script to execute the application
├── requirements.txt     # Project dependencies
└── README.md            # This file
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd reddit-cli
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the CLI Interface
Run the CLI interface with a search query:
```bash
python -m src.main "python programming"
```

Or run without arguments to enter interactive mode:
```bash
python -m src.main
```

### Running the MCP Server
Start the MCP server:
```bash
python src/mcp_server.py
```

The server will be available at `http://localhost:5000`

### MCP Server Endpoints

#### Search Posts
```
GET /search?q={query}&limit={limit}&after={after}
```

#### Get Post Details
```
GET /posts/{post_id}
```

#### Get Post Comments
```
GET /posts/{post_id}/comments?limit={limit}
```

#### Get AI Summary
```
GET /posts/{post_id}/summary
```

#### Get Trending Posts
```
GET /trending?limit={limit}&after={after}
```

#### Health Check
```
GET /health
```

#### OpenAPI Specification
```
GET /openapi.json
```

## Keyboard Controls

- `n` - Go to next page of results
- `c` - Cycle through comments when viewing a post  
- `s` - Get AI-generated summary for current post
- `q` or Ctrl+C - Quit the application
- Number keys - Select specific post by number

## Configuration

The application uses environment variables for configuration:

- `OLLAMA_BASE_URL` - Ollama server address (default: http://192.168.8.223:11434)
- `OLLAMA_MODEL` - AI model to use (default: gpt-oss:20b)
- `PORT` - MCP server port (default: 5000)

## Requirements

- Python 3.7+
- requests
- rich
- pyyaml
- flask
- flask-cors
- pytest
- pytest-cov

## Testing

Run tests with:
```bash
python -m pytest tests/
```

Or run basic functionality checks:
```bash
python test_cli.py
```

Run MCP server tests:
```bash
python test_mcp_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.