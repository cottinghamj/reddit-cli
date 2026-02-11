# MCP Server Testing

The MCP server is now running at `http://home.ms:5000`. Here are the curl commands to test all endpoints:

## 1. Health Check
```bash
curl -X GET http://home.ms:5000/health
```

## 2. Search Posts
```bash
curl -X GET "http://home.ms:5000/search?q=python&limit=5"
```

## 3. Get Post Details
```bash
curl -X GET http://home.ms:5000/posts/xyz123
```

## 4. Get Post Comments
```bash
curl -X GET "http://home.ms:5000/posts/xyz123/comments?limit=10"
```

## 5. Get AI Summary
```bash
curl -X GET http://home.ms:5000/posts/xyz123/summary
```

## 6. Get Trending Posts
```bash
curl -X GET "http://home.ms:5000/trending?limit=5"
```

## 7. OpenAPI Specification
```bash
curl -X GET http://home.ms:5000/openapi.json
```

## Example Response Format

### Search Response:
```json
{
  "posts": [
    {
      "id": "xyz123",
      "title": "Example Post Title",
      "subreddit": "example",
      "created_utc": 1634567890,
      "url": "http://reddit.com/r/example/comments/xyz123",
      "body": "Post content here...",
      "score": 123
    }
  ],
  "after": "next_token",
  "query": "python",
  "limit": 5
}
```

### AI Summary Response:
```json
{
  "post_id": "xyz123",
  "summary": "AI-generated summary of the post and comments...",
  "post_title": "Example Post Title",
  "subreddit": "example"
}
```

## Authentication

All AI-related endpoints require the API key in the Authorization header:
```bash
curl -X GET http://home.ms:5000/posts/xyz123/summary \
  -H "Authorization: Bearer 111"