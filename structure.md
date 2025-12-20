# Reddit CLI Project Structure

This document describes the purpose and functionality of each file in the Reddit CLI project, excluding those ignored by .gitignore.

## Core Application Files

### `src/main.py`
Main application entrypoint that implements the Reddit CLI interface. Contains:
- `RedditClient` class for interacting with Reddit API
- `AIClient` class for AI-powered summarization using Ollama API
- `RedditCLI` class that manages the user interface and application flow
- Main execution logic that handles user input and navigation

### `src/__init__.py`
Python package initialization file. Currently empty but required for proper module structure.

### `src/pagination.md`
Documentation file describing pagination implementation for navigating through multiple pages of search results from Reddit API.

## Setup and Execution Scripts

### `setup.sh`
Setup script that creates a Python virtual environment and installs all required dependencies from requirements.txt.

### `run.sh`
Run script that activates the virtual environment and executes the Reddit CLI application with given arguments.

## Testing

### `tests/test_cli.py`
Unit tests for the Reddit CLI application components:
- Tests for `RedditClient` class functionality
- Tests for `AIClient` class functionality
- Basic test structure for verifying core functionality

## Dependencies and Configuration

### `requirements.txt`
Lists all Python dependencies required for the project:
- `requests`: For making HTTP requests to Reddit API
- `rich`: For creating formatted terminal output
- `pyyaml`: For YAML configuration handling
- `pytest` and `pytest-cov`: For testing framework and coverage reporting

## Documentation

### `README.md`
Main documentation file that explains:
- Project overview and features
- Installation instructions
- Usage examples with keyboard controls
- Configuration details
- Testing procedures
- Contributing guidelines
- License information

### `plan.md`
Project plan or roadmap documenting planned features and development steps for the Reddit CLI application.

### `prompt.md`
AI prompt template used for generating summaries of Reddit posts. This file contains instructions for how to format the request sent to the AI model for summarization.