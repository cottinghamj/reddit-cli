#!/usr/bin/env python3
"""
Reddit CLI Interface - Python Implementation
"""

import argparse
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class RedditClient:
    """Client for interacting with Reddit API"""

    def __init__(self):
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "RedditCLI/0.1 by User"})

    def search_posts(
        self, query: str, limit: int = 15, after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for Reddit posts matching the query

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
            response = self.session.get(
                f"{self.base_url}/search.json", params=params, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch posts: {str(e)}")

    def get_post_details(self, post_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific post

        Args:
            post_id: Reddit post ID

        Returns:
            Dictionary with post details
        """
        try:
            response = self.session.get(
                f"{self.base_url}/by_id/t3_{post_id}.json", timeout=10
            )
            response.raise_for_status()
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
        Get comments for a specific post

        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch

        Returns:
            List of comment dictionaries
        """
        try:
            response = self.session.get(
                f"{self.base_url}/comments/{post_id}.json",
                params={"limit": limit},
                timeout=10,
            )
            response.raise_for_status()
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
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


class AIClient:
    """Client for interacting with Ollama AI API"""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://192.168.8.223:11434")
        self.model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
        self.session = requests.Session()

    def generate_summary(self, post_body: str, comments: List[str]) -> str:
        """
        Generate AI summary of a post with comments

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
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            response.raise_for_status()

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


class RedditCLI:
    def __init__(self):
        self.console = Console()
        self.reddit_client = RedditClient()
        self.ai_client = AIClient()
        self.current_page = 0
        self.search_results = []
        self.current_post = None
        self.comments = []
        self.current_comment_index = 0
        self.search_query = ""
        self.after_token = None

    def run(self):
        """Main application entry point"""
        parser = argparse.ArgumentParser(description="Reddit CLI Interface")
        parser.add_argument("query", nargs="?", help="Search query for Reddit")
        args = parser.parse_args()

        if not args.query:
            # Show welcome screen
            self.show_welcome()
            # Get search query from user
            query = input("\nEnter search query: ").strip()
            if not query:
                self.console.print("[red]No query provided. Exiting.[/red]")
                return
            self.search(query)
        else:
            # Process the provided query
            self.search(args.query)

    def show_welcome(self):
        """Display welcome screen"""
        self.console.print(
            Panel(
                "Reddit CLI Interface\n\n"
                "Use 'n' to go to next page\n"
                "Press number to view post details\n"
                "Press 'c' to cycle comments\n"
                "Press 's' to get AI summary\n"
                "Press 'S' (capital S) for new search\n"
                "Press 'q' or Ctrl+C to quit",
                title="Welcome to Reddit CLI",
                border_style="blue",
            )
        )

    def search(self, query: str):
        """Perform search and display results"""
        self.search_query = query
        self.console.print(f"\nSearching for: [bold blue]{query}[/bold blue]")

        # Retry logic for initial search
        max_retries = 2
        retry_delay = 1  # seconds

        for attempt in range(max_retries + 1):
            try:
                # Reset pagination state
                self.after_token = None

                data = self.reddit_client.search_posts(query, limit=15)

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
                                }
                            )

                    # Get the after token for pagination
                    self.after_token = data["data"].get("after")

                if not posts:
                    self.console.print("[yellow]No results found[/yellow]")
                    return

                self.search_results = posts
                self.current_page = 0
                self.display_search_results()
                self.handle_user_input()
                return  # Success, exit retry loop

            except Exception as e:
                if attempt < max_retries:
                    self.console.print(
                        f"[yellow]Attempt {attempt + 1} failed: {e}[/yellow]"
                    )
                    self.console.print(
                        f"[yellow]Retrying in {retry_delay} seconds...[/yellow]"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    self.console.print(
                        f"[red]Error searching after {max_retries + 1} attempts: {e}[/red]"
                    )
                    self.console.print("[yellow]Please try a new search.[/yellow]")
                    # Re-raise exception so it can be handled by the main loop
                    raise e

    def next_page(self, query: str):
        """Load the next page of search results"""
        if not self.after_token:
            self.console.print("[yellow]No more pages available[/yellow]")
            return

        # Retry logic for network errors
        max_retries = 2
        retry_delay = 1  # seconds

        for attempt in range(max_retries + 1):
            try:
                data = self.reddit_client.search_posts(
                    query, limit=15, after=self.after_token
                )

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
                                }
                            )

                    # Get the after token for pagination
                    self.after_token = data["data"].get("after")

                if not posts:
                    self.console.print("[yellow]No more results found[/yellow]")
                    return

                self.search_results = posts
                self.current_page += 1

                self.display_search_results()
                self.handle_user_input()
                return  # Success, exit retry loop

            except Exception as e:
                if attempt < max_retries:
                    self.console.print(
                        f"[yellow]Attempt {attempt + 1} failed: {e}[/yellow]"
                    )
                    self.console.print(
                        f"[yellow]Retrying in {retry_delay} seconds...[/yellow]"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    self.console.print(
                        f"[red]Error loading next page after {max_retries + 1} attempts: {e}[/red]"
                    )
                    self.console.print(
                        "[yellow]Returning to current results. Try a new search.[/yellow]"
                    )
                    self.display_search_results()
                    # Re-raise exception so it can be handled by the main loop
                    raise e

    def display_search_results(self):
        """Display search results in a table format"""
        table = Table(title=f"Search Results (Page {self.current_page + 1})")
        table.add_column("Number", style="cyan", no_wrap=True)
        table.add_column("Subreddit", style="magenta")
        table.add_column("Date", style="green")
        table.add_column("Title", style="white")

        for i, post in enumerate(self.search_results):
            # Format date if available
            formatted_date = self.reddit_client.format_timestamp(post["created_utc"])

            table.add_row(str(i + 1), post["subreddit"], formatted_date, post["title"])

        self.console.print(table)
        self.console.print(
            "\n[blue]Press 'n' for next page, number to select a post, or 'q' to quit[/blue]"
        )

    def handle_user_input(self):
        """Handle user interaction and navigation"""
        try:
            while True:
                user_input = input("\nEnter selection: ").strip().lower()

                if user_input == "n":
                    # Move to next page
                    self.console.print("[yellow]Loading next page...[/yellow]")
                    try:
                        self.next_page(self.search_query)
                        break  # Break out of current loop so we can show new results
                    except Exception as e:
                        # If all retries failed, let user start a new search
                        pass  # Continue to main loop to allow new search

                elif user_input == "s":
                    # Perform new search
                    self.console.print("[blue]Starting new search...[/blue]")
                    query = input("Enter new search query: ").strip()
                    if query:
                        self.search(query)
                        break
                    else:
                        self.console.print(
                            "[yellow]No query provided. Returning to current results.[/yellow]"
                        )
                        self.display_search_results()

                elif user_input in ["q", "quit"]:
                    self.console.print("Goodbye!")
                    break

                elif user_input.isdigit():
                    index = int(user_input) - 1
                    if 0 <= index < len(self.search_results):
                        self.view_post(index)
                    else:
                        self.console.print("[red]Invalid selection[/red]")

                else:
                    self.console.print(
                        "[red]Unknown command. Use 'n' for next page, 's' for new search, number to select post, or 'q' to quit[/red]"
                    )

        except KeyboardInterrupt:
            self.console.print("\n[cyan]Goodbye![/cyan]")

    def view_post(self, index: int):
        """View a selected post with full details"""
        self.current_post = self.search_results[index]

        # Try to get more detailed info
        try:
            detailed_info = self.reddit_client.get_post_details(self.current_post["id"])
            if detailed_info:
                self.current_post.update(detailed_info)

            # Get comments
            self.comments = self.reddit_client.get_post_comments(
                self.current_post["id"], limit=100
            )

        except Exception as e:
            self.console.print(f"[red]Error fetching details: {e}[/red]")

        # Display post details
        self.display_post_details()

        # Handle post-specific navigation
        try:
            while True:
                user_input = (
                    input(
                        "\n[blue]Enter 'c' to view comments, 's' for AI summary, 'S' for new search, or any other key to return to search: [/blue]"
                    )
                    .strip()
                    .lower()
                )

                if user_input == "c":
                    self.view_comments()
                elif user_input == "s":
                    self.view_ai_summary()
                elif user_input == "S":  # Capital S for new search from post view
                    self.console.print("[blue]Starting new search...[/blue]")
                    query = input("Enter new search query: ").strip()
                    if query:
                        self.search(query)
                        break
                    else:
                        self.console.print(
                            "[yellow]No query provided. Returning to current post.[/yellow]"
                        )
                        self.display_post_details()
                else:
                    # Return to search results
                    self.display_search_results()
                    break

        except KeyboardInterrupt:
            self.console.print("\n[blue]Returning to search...[/blue]")

    def display_post_details(self):
        """Display full details of a post"""
        self.console.print(
            Panel(
                f"[bold blue]{self.current_post.get('title', 'No title')}[/bold blue]\n\n"
                f"Subreddit: [cyan]{self.current_post.get('subreddit', 'unknown')}[/cyan]\n"
                f"Created: {self.reddit_client.format_timestamp(self.current_post.get('created_utc', 0))}\n\n"
                f"[white]{self.current_post.get('body', '')}[/white]\n",
                title=f"Post #{self.search_results.index(self.current_post) + 1}",
                border_style="green",
            )
        )

    def view_comments(self):
        """View comments with cycling"""
        if not self.comments:
            self.console.print("[yellow]No comments available[/yellow]")
            return

        self.console.print(f"[blue]Showing comments: {len(self.comments)} total[/blue]")

        try:
            while True:
                # Display current comment
                comment = self.comments[self.current_comment_index]
                self.console.print(
                    Panel(
                        f"Author: [cyan]{comment.get('author', 'unknown')}[/cyan]\n"
                        f"Score: [magenta]{comment.get('score', 0)}[/magenta]\n\n"
                        f"[white]{comment.get('body', '')}[/white]",
                        title=f"Comment {self.current_comment_index + 1}",
                        border_style="yellow",
                    )
                )

                # Navigation options
                user_input = (
                    input(
                        "\n[blue]Press 'n' for next comment, 'p' for previous, or any key to return: [/blue]"
                    )
                    .strip()
                    .lower()
                )

                if user_input == "n":
                    self.current_comment_index = (self.current_comment_index + 1) % len(
                        self.comments
                    )
                elif user_input == "p":
                    self.current_comment_index = (self.current_comment_index - 1) % len(
                        self.comments
                    )
                else:
                    break

        except KeyboardInterrupt:
            self.console.print("\n[blue]Returning to post...[/blue]")

    def view_ai_summary(self):
        """Get and display AI-generated summary via Ollama"""
        if not self.current_post or not self.comments:
            self.console.print("[red]No content available for summarization[/red]")
            return

        try:
            body = self.current_post.get("body", "")

            # Get the first 100 comments (or fewer)
            comment_bodies = [comment.get("body", "") for comment in self.comments]

            summary = self.ai_client.generate_summary(body, comment_bodies)

            if summary:
                self.console.print(
                    Panel(
                        f"[bold green]AI Summary:[/bold green]\n\n{summary}",
                        title="AI Generated Summary",
                        border_style="magenta",
                    )
                )
            else:
                self.console.print("[red]Failed to generate AI summary[/red]")

        except Exception as e:
            self.console.print(f"[red]Error generating AI summary: {e}[/red]")


def main():
    """Main function to run the CLI application"""
    app = RedditCLI()
    app.run()


if __name__ == "__main__":
    main()
