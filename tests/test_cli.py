#!/usr/bin/env python3
"""
Reddit CLI - Unit Tests

This module contains unit tests for the Reddit CLI application components.
"""

import os
import sys
import unittest

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_client import AIClient
from reddit_client import RedditClient


class TestRedditClient(unittest.TestCase):
    """Test cases for RedditClient class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.client = RedditClient()

    def test_client_initialization(self):
        """Test that RedditClient initializes correctly"""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.base_url, "https://www.reddit.com")

    def test_prompt_creation(self):
        """Test prompt creation functionality"""
        client = AIClient()

        # Test with sample data
        post_body = "This is a test post body"
        comments = ["First comment", "Second comment"]

        prompt = client._create_prompt(post_body, comments)

        self.assertIn("Summarize", prompt)
        self.assertIn(post_body, prompt)
        self.assertIn("Comment 1:", prompt)


class TestAIClient(unittest.TestCase):
    """Test cases for AIClient class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.client = AIClient()

    def test_client_initialization(self):
        """Test that AIClient initializes correctly"""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.model, "gpt-oss:20b")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
