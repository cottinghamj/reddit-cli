# Reddit CLI Interface - Project Plan

## Overview
Create a command-line interface for browsing Reddit posts with intuitive navigation, search capabilities, and interactive post viewing.

## Core Features

### 1. Search Functionality
- Search for Reddit posts by keyword/terms
- Display first 15 results per page
- Pagination support (press 'n' for next 15 posts)
- Posts numbered for easy selection
- Table format with:
  - Post number
  - Subreddit name
  - Post creation date
  - Post title (main column)

### 2. Post Navigation
- Click on post number to view full post details
- View main body text of the post
- Interactive comments viewing (press 'c' to cycle through comments)
- Summary functionality (press 's' to get AI-generated summary)

### 3. AI Integration
- Use Ollama API at IP 192.168.8.223:11434
- Model: gpt-oss:20b
- Send post body + 100 random comments to AI for summarization
- Display AI-generated summary to user

## Technical Implementation Plan

### Phase 1: Project Structure and Basic Setup
- Create directory structure
- Initialize project with dependencies
- Set up basic CLI framework using a library like `clap` for Rust or `commander` for Node.js
- Implement file-based data storage for caching Reddit data

### Phase 2: Search Functionality
- Implement Reddit API integration (using official Reddit API or third-party)
- Create search endpoint handler
- Design result table format with required columns
- Implement pagination logic ('n' key to load next page)

### Phase 3: Post Viewing Interface
- Create post detail view
- Display post body text
- Implement interactive comment viewing system (press 'c' for comments)
- Add UI for showing current post information

### Phase 4: AI Integration
- Set up connection to Ollama server at 192.168.8.223:11434
- Implement summary request functionality (press 's')
- Process and display AI-generated summaries
- Handle error scenarios for AI service unavailability

### Phase 5: User Experience Optimization
- Add keyboard navigation hints to UI
- Implement input validation
- Create error handling for API failures
- Add loading indicators for data fetching
- Optimize performance for large comment sets

## Data Structure Requirements

### Post Representation
```json
{
  "id": "string",
  "title": "string",
  "body": "string",
  "subreddit": "string",
  "created_utc": "timestamp",
  "url": "string",
  "comments": ["comment1", "comment2", ...]
}
```

### UI Components
1. Search Interface
2. Results Table View
3. Post Detail View
4. Comments Viewer
5. AI Summary Display

## Detailed Technical Specifications

### API Integration Layer
- Use Reddit's official API (https://www.reddit.com/dev/api/)
- Authentication handling (OAuth or API key if needed)
- Rate limiting implementation
- Data caching to reduce API calls
- Error handling for network issues and API errors

### CLI Interface Components
- Main search screen with table view
- Post detail screen showing:
  - Title
  - Author and subreddit info
  - Creation date
  - Body text
- Comment viewer with cycling through posts
- Summary screen showing AI output
- Navigation controls with clear key hints

### Terminal UI Considerations
- Use a library like `tui-rs` for Rust or `blessed` for Node.js for advanced terminal rendering
- Support for color-coded UI elements (subreddit colors, etc.)
- Responsiveness to different terminal sizes
- Keyboard navigation support (arrows, enter, etc.)

### Data Management
- Local cache storage using JSON files or a simple database
- Cache invalidation strategy for fresh data
- Efficient data parsing and storage formats

## Dependencies and Tools

### Core Libraries
- CLI library (e.g., `clap` for Rust or `inquirer.js` for Node.js)
- HTTP client for Reddit API communication (e.g., `reqwest` for Rust or `axios` for Node.js)
- JSON parsing/serialization
- Terminal UI framework (for enhanced display)

### AI Integration
- Ollama client library for connecting to local AI server
- Connection pooling and error handling for AI service
- Request/response data formatting for the AI model

## Development Timeline

### Week 1
- Project setup and core CLI framework
- Basic Reddit API integration
- Search functionality implementation
- Initial terminal UI design

### Week 2
- Results table formatting and pagination
- Post detail view creation
- Comments viewing system
- Keyboard input handling

### Week 3
- AI integration with Ollama server
- Summary generation and display
- Error handling for both API and AI service
- Testing and UI refinement

### Week 4
- Performance optimization
- Error handling and edge case management
- Documentation and final testing
- User experience improvements

## Implementation Considerations

### Error Handling
- Implement graceful degradation when services are unavailable
- Network timeout handling
- Data validation and sanitization
- Clear error messages to user

### Usability Features
- Clear visual feedback for user actions
- Helpful key bindings documentation
- Progress indicators for loading content
- Responsive design for different terminal sizes

### Performance Optimization
- Efficient data fetching strategies
- Local caching of frequently accessed data
- Asynchronous loading where appropriate
- Memory management for large comment sets

## Testing Strategy
- Unit tests for core logic functions
- Integration tests for API interactions
- End-to-end tests for full user flows
- UI component testing for terminal interaction
- Performance testing with larger datasets