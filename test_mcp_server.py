#!/usr/bin/env python3
"""
Test script for MCP server functionality
"""

import os
import sys
import time
import requests

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp_server import RedditClient, AIClient

def test_reddit_client():
    """Test Reddit client with retry logic"""
    print("Testing Reddit Client...")
    
    client = RedditClient()
    
    try:
        # Test search with retry logic
        print("Searching for 'python programming'...")
        data = client.search_posts("python programming", limit=5)
        print(f"Found {len(data.get('data', {}).get('children', []))} posts")
        print("✓ Reddit client search test passed")
        
        # Test post details with retry logic
        if data.get('data', {}).get('children'):
            post_id = data['data']['children'][0]['data']['id']
            print(f"Getting details for post {post_id}...")
            post_data = client.get_post_details(post_id)
            print(f"Post title: {post_data.get('title', 'No title')}")
            print("✓ Reddit client post details test passed")
            
        # Test comments with retry logic
        print(f"Getting comments for post {post_id}...")
        comments = client.get_post_comments(post_id, limit=5)
        print(f"Found {len(comments)} comments")
        print("✓ Reddit client comments test passed")
        
    except Exception as e:
        print(f"✗ Reddit client test failed: {e}")
        return False
        
    return True

def test_ai_client():
    """Test AI client with retry logic"""
    print("\nTesting AI Client...")
    
    client = AIClient()
    
    try:
        # Test summary generation with retry logic
        # We'll use a simple test case
        post_body = "This is a test post body for testing the AI summary functionality."
        comments = ["This is a test comment.", "Another test comment."]
        
        print("Generating AI summary...")
        summary = client.generate_summary(post_body, comments)
        print(f"Summary: {summary[:100]}...")
        print("✓ AI client test passed")
        
    except Exception as e:
        print(f"✗ AI client test failed: {e}")
        return False
        
    return True

def test_server_endpoints():
    """Test server endpoints"""
    print("\nTesting Server Endpoints...")
    
    try:
        # Test health check
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            print("✓ Health check endpoint works")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
            
        # Test OpenAPI spec
        response = requests.get('http://localhost:5000/openapi.json')
        if response.status_code == 200:
            print("✓ OpenAPI spec endpoint works")
        else:
            print(f"✗ OpenAPI spec failed: {response.status_code}")
            return False
            
        print("✓ Server endpoints test passed")
        
    except Exception as e:
        print(f"✗ Server endpoints test failed: {e}")
        return False
        
    return True

def main():
    """Main test function"""
    print("Running MCP Server Tests...")
    print("=" * 50)
    
    success = True
    
    # Test the core components
    success &= test_reddit_client()
    success &= test_ai_client()
    
    # Note: We can't easily test the full server endpoints without actually running it,
    # but we can test the components that would be used by the server
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())