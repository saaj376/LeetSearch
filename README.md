# LeetSearch 

> Find and track LeetCode users from your college campus!

Ever wondered which of your college friends is secretly solving LeetCode at 2 AM instead of doing assignments? This extension lets you totally not creepily find every LeetCoder in your campus. You can spot hidden tryhards, sleepy grinders, fake humble toppers, and all the people who pretend they barely code but actually never stop, lol.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
  - [Step 1: Obtaining LeetCode Session Token and CSRF Token](#step-1-obtaining-leetcode-session-token-and-csrf-token)
  - [Step 2: Backend Setup](#step-2-backend-setup)
  - [Step 3: Chrome Extension Setup](#step-3-chrome-extension-setup)
- [Hosting the Backend on Render](#hosting-the-backend-on-render)
- [Alternative: Using Supabase for Database (Not Implemented)](#alternative-using-supabase-for-database-not-implemented)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **College-based Search**: Find LeetCode users from your specific college or university
- **User Statistics**: View comprehensive stats for each user including:
  - Real name and school affiliation
  - Global rankings
  - Country information
  - Direct links to LeetCode profiles
- **Real-time Updates**: Automatically scrape and update user data via background tasks
- **Campus Discovery**: Compare and discover coding activity within your campus community
- **Chrome Extension**: Easy-to-use browser extension interface with search and filter capabilities
- **Local Caching**: Fast searches using locally cached user profiles stored in JSON format
- **RESTful API**: FastAPI-powered backend with comprehensive endpoints for data access

## Project Structure

```
LeetSearch/
├── backend/              # Backend server for data scraping and API
│   ├── main.py          # FastAPI application and REST endpoints
│   ├── models.py        # Pydantic data models for API contracts
│   ├── scraper.py       # LeetCode GraphQL scraper with authentication
│   ├── updater.py       # Background task for periodic data updates
│   ├── search.py        # Search utilities and helpers
│   ├── requirements.txt # Python dependencies
│   ├── users.json       # Local JSON database cache (auto-generated)
│   └── test_main.py     # Unit tests for backend endpoints
├── extension/           # Chrome extension files
│   ├── manifest.json    # Extension manifest configuration
│   ├── popup.html       # Extension popup UI structure
│   ├── popup.js         # Extension logic and API communication
│   └── style.css        # Extension styling
├── .gitignore           # Git ignore patterns
├── LICENSE              # Apache 2.0 License
└── README.md            # This comprehensive guide
```

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.7+** installed on your system
- **pip** (Python package manager)
- **Google Chrome** or any Chromium-based browser (Edge, Brave, etc.)
- **LeetCode Account** (required for accessing LeetCode's GraphQL API)
- **Text Editor** (VS Code, Sublime Text, etc.) for configuration files
- **Git** (optional, for cloning the repository)

## Installation & Setup

### Step 1: Obtaining LeetCode Session Token and CSRF Token

The backend needs to authenticate with LeetCode's GraphQL API to fetch user profiles and contest data. LeetCode requires session cookies for accessing their internal APIs.

#### Why These Tokens Are Needed

LeetCode's public profile data and contest rankings are behind authentication. To programmatically access this data:

1. **LEETCODE_SESSION**: This is your session cookie that identifies you as an authenticated user to LeetCode's servers
2. **CSRFTOKEN**: Cross-Site Request Forgery token used for security verification on POST requests to LeetCode's API

Without these tokens, the scraper cannot access LeetCode's GraphQL endpoints and will fail to fetch user data.

#### How to Get Your Tokens

1. **Open Chrome/Firefox** and navigate to [https://leetcode.com](https://leetcode.com)

2. **Log in to your LeetCode account**

3. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)

4. **Navigate to the Application/Storage Tab**:
   - In Chrome/Edge: Click on the "Application" tab
   - In Firefox: Click on the "Storage" tab

5. **Find Cookies**:
   - Expand "Cookies" in the left sidebar
   - Click on `https://leetcode.com`

6. **Locate and Copy Tokens**:
   - Find the cookie named `LEETCODE_SESSION` and copy its **Value**
   - Find the cookie named `csrftoken` and copy its **Value**

   The values will be long alphanumeric strings. Copy these values carefully.

7. **Keep These Tokens Secure**: These tokens give access to your LeetCode account, so never share them publicly or commit them to version control.

### Step 2: Backend Setup

#### 2.1 Clone the Repository

```bash
git clone https://github.com/saaj376/LeetSearch.git
cd LeetSearch
```

#### 2.2 Navigate to Backend Directory

```bash
cd backend
```

#### 2.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `fastapi` - Modern web framework for building APIs
- `uvicorn` - ASGI server for running FastAPI
- `requests` - HTTP library for making API calls to LeetCode
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework
- `httpx` - Async HTTP client for testing

#### 2.4 Create Environment File

Create a `.env` file in the `backend` directory:

```bash
touch .env
```

Open the `.env` file in your text editor and add your tokens:

```env
LEETCODE_SESSION=your_leetcode_session_token_here
CSRFTOKEN=your_csrf_token_here
```

**Important Notes:**
- Replace `your_leetcode_session_token_here` and `your_csrf_token_here` with the actual tokens you copied earlier
- The `.env` file is already included in `.gitignore` to prevent accidentally committing your credentials
- Never share these tokens or commit them to version control

#### 2.5 Run the Backend Server

For local development:

```bash
python main.py
```

The server will start on `http://localhost:8000` with auto-reload enabled.

Alternatively, use uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2.6 Verify Backend is Running

Open your browser and navigate to:
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

You should see the FastAPI Swagger documentation and a JSON response showing the health status.

#### 2.7 Initial Data Population

To populate the database with user data, trigger a refresh cycle:

```bash
curl -X POST "http://localhost:8000/refresh" \
  -H "Content-Type: application/json" \
  -d '{"pages": 2, "max_users": 25}'
```

This will:
1. Scrape the first 2 pages of LeetCode's global contest rankings
2. Fetch detailed profiles for up to 25 users
3. Store the data in `users.json`

The process may take several minutes depending on the number of users.

### Step 3: Chrome Extension Setup

#### 3.1 Update Backend URL in Extension

Before loading the extension, you need to configure it to communicate with your backend.

**For Local Development:**

Open `extension/manifest.json` and ensure the `host_permissions` includes your local backend:

```json
{
  "host_permissions": [
    "http://localhost:8000/*"
  ]
}
```

Open `extension/popup.js` and verify the `DEFAULT_API_BASE` constant:

```javascript
const DEFAULT_API_BASE = "http://localhost:8000";
```

**For Production (Hosted Backend):**

If you're hosting the backend on a service like Render (see next section), update both files:

In `manifest.json`:
```json
{
  "host_permissions": [
    "https://your-app-name.onrender.com/*"
  ]
}
```

In `popup.js`:
```javascript
const DEFAULT_API_BASE = "https://your-app-name.onrender.com";
```

Replace `your-app-name.onrender.com` with your actual hosted backend URL.

#### 3.2 Load Extension in Chrome

1. **Open Chrome** and navigate to `chrome://extensions/`

2. **Enable Developer Mode**:
   - Look for the toggle in the top-right corner
   - Click to enable it

3. **Load the Extension**:
   - Click the "Load unpacked" button
   - Navigate to the `LeetSearch/extension` folder
   - Select the folder and click "Open"

4. **Verify Installation**:
   - You should see "LeetCode College Finder" appear in your extensions list
   - The extension icon should appear in your Chrome toolbar (you may need to click the puzzle piece icon to pin it)

#### 3.3 Test the Extension

1. Click the extension icon in your Chrome toolbar
2. Enter a college name (e.g., "MIT", "Stanford", "Waterloo")
3. Click "Search"
4. You should see a list of LeetCode users from that college

If you get an error, verify:
- Backend is running and accessible
- `manifest.json` has the correct permissions
- `popup.js` has the correct API base URL

## Hosting the Backend on Render

To make your LeetSearch extension accessible from anywhere, you can host the backend on Render (a free cloud platform).

### Step-by-Step Guide to Deploy on Render

#### 1. Prepare Your Repository

Ensure your code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

#### 2. Create a Render Account

1. Go to [https://render.com](https://render.com)
2. Sign up for a free account (you can use your GitHub account)

#### 3. Create a New Web Service

1. From your Render dashboard, click "New +" and select "Web Service"
2. Connect your GitHub repository (authorize Render to access your repos)
3. Select the `LeetSearch` repository

#### 4. Configure the Web Service

Fill in the following settings:

- **Name**: `leetsearch-backend` (or any name you prefer)
- **Region**: Choose the closest region to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 5. Add Environment Variables

In the "Environment" section, add your tokens:

- Click "Add Environment Variable"
- Add `LEETCODE_SESSION` with your session token value
- Add `CSRFTOKEN` with your CSRF token value

#### 6. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the deployment to complete (this may take a few minutes)
4. Once deployed, you'll receive a URL like `https://leetsearch-backend.onrender.com`

#### 7. Test Your Deployed Backend

Visit your deployed backend's health endpoint:

```
https://leetsearch-backend.onrender.com/health
```

You should see a JSON response with the health status.

Visit the API documentation:

```
https://leetsearch-backend.onrender.com/docs
```

#### 8. Update Chrome Extension with Production URL

Follow the instructions in [Step 3: Chrome Extension Setup](#step-3-chrome-extension-setup) to update the `manifest.json` and `popup.js` files with your Render URL.

#### 9. Reload Extension

1. Go to `chrome://extensions/`
2. Find LeetCode College Finder
3. Click the refresh icon
4. Test the extension with your hosted backend

### Important Notes for Render Deployment

- **Free Tier Limitations**: Render's free tier puts your app to sleep after 15 minutes of inactivity. The first request after sleep may take 30-60 seconds to respond.
- **Persistent Storage**: The `users.json` file will be stored on Render's ephemeral disk, which means data may be lost on redeploys. For production use, consider implementing a persistent database solution.
- **Environment Variables**: Never hardcode your tokens in the code. Always use environment variables.
- **CORS**: The backend already includes CORS middleware to allow requests from browser extensions.

## Alternative: Using Supabase for Database (Not Implemented)

Initially, I considered using Supabase (an open-source Firebase alternative) to host the user profile database online. This would provide:

### Potential Benefits of Supabase

1. **Persistent Storage**: Data wouldn't be lost between deployments
2. **Real-time Updates**: Multiple users could see synchronized data
3. **Scalability**: Better handling of concurrent requests
4. **Backup & Recovery**: Automatic database backups
5. **PostgreSQL**: Full-featured relational database with complex queries

### Why Supabase Wasn't Implemented

While integrating Supabase, I encountered several challenges that made the implementation difficult:

1. **Authentication Complexity**: Supabase's Row Level Security (RLS) policies required additional authentication layer that complicated the simple scraper architecture

2. **Schema Migration Issues**: Converting the flat JSON structure to Supabase's PostgreSQL schema resulted in:
   - Type conversion errors for optional fields
   - Null handling inconsistencies
   - Complex nested object storage (like `websites` array)

3. **API Rate Limiting**: Supabase's free tier has connection limits that conflicted with the scraper's bulk update operations

4. **Development Overhead**: The additional complexity wasn't justified for a project that works well with local JSON caching

5. **Cost Considerations**: While Supabase has a free tier, scaling would require paid plans

### Current Solution: Local JSON Database

The current implementation uses a local `users.json` file for data storage, which:

- ✅ Simple and fast for read operations
- ✅ No external dependencies or API keys
- ✅ Easy to backup and version control
- ✅ Works perfectly for college-sized datasets (hundreds to thousands of users)
- ❌ Not suitable for multiple backend instances
- ❌ Data lost on container restarts (on platforms like Render)

### If You Want to Implement Supabase

If you want to tackle the Supabase integration yourself, here's what you'd need:

1. **Create Supabase Project**: Sign up at [https://supabase.com](https://supabase.com)

2. **Create Users Table**:
   ```sql
   CREATE TABLE profiles (
     username TEXT PRIMARY KEY,
     real_name TEXT,
     about_me TEXT,
     country_name TEXT,
     ranking INTEGER,
     school TEXT,
     company TEXT,
     websites TEXT[],
     updated_at TIMESTAMP DEFAULT NOW()
   );
   ```

3. **Install Supabase Client**:
   ```bash
   pip install supabase
   ```

4. **Replace JSON Operations**: Update `main.py` to use Supabase client instead of file I/O

5. **Environment Variables**: Add `SUPABASE_URL` and `SUPABASE_KEY` to your `.env`

## Usage

### Using the Chrome Extension

1. **Launch the Extension**:
   - Click on the "LeetCode College Finder" icon in your Chrome toolbar
   - The popup window will appear

2. **Search for a College**:
   - Enter your college or university name in the search box
   - Examples: "MIT", "Stanford", "IIT", "Waterloo", "Berkeley"
   - The search is case-insensitive and matches partial strings
   - Click the "Search" button or press Enter

3. **View Results**:
   - Users from the matching college will be displayed in a card format
   - Each card shows:
     - Username (clickable link to their LeetCode profile)
     - Global ranking
     - Real name (if available)
     - Country
     - School affiliation

4. **Filter Results**:
   - After a search, a filter box appears
   - Type to filter results by username, real name, or country
   - The filter updates in real-time as you type

5. **Check Statistics**:
   - The statistics card shows:
     - Total profiles matched from your search
     - Number of profiles currently displayed (after filtering)
     - Last refresh timestamp

### Using the Backend API

#### Health Check

Check if the backend is running and how many profiles are cached:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "profiles_cached": 150,
  "last_updated": "2025-11-24T10:30:00Z"
}
```

#### Search by College

Find all users from a specific college:

```bash
curl "http://localhost:8000/search/college?query=Stanford"
```

Response:
```json
{
  "query": "Stanford",
  "total": 5,
  "results": [
    {
      "username": "john_doe",
      "realName": "John Doe",
      "school": "Stanford University",
      "ranking": 1234,
      "country": "United States"
    }
  ]
}
```

#### Get User Profile

Retrieve detailed profile for a specific user:

```bash
curl http://localhost:8000/profiles/john_doe
```

To force a fresh fetch from LeetCode:

```bash
curl "http://localhost:8000/profiles/john_doe?refresh=true"
```

#### Trigger Data Refresh

Manually trigger a background scrape and update cycle:

```bash
curl -X POST "http://localhost:8000/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "pages": 3,
    "max_users": 50
  }'
```

Parameters:
- `pages`: Number of contest ranking pages to scrape (1-10)
- `max_users`: Maximum number of user profiles to fetch (1-200)

## API Endpoints

### GET `/health`

**Description**: Health check endpoint that returns backend status and cache information.

**Response**:
```json
{
  "status": "ok",
  "profiles_cached": 150,
  "last_updated": "2025-11-24T10:30:00Z"
}
```

### GET `/search/college`

**Description**: Search for users by college/university name.

**Query Parameters**:
- `query` (required): College name or substring to search for (minimum 2 characters)

**Response**:
```json
{
  "query": "MIT",
  "total": 10,
  "results": [
    {
      "username": "alice",
      "realName": "Alice Johnson",
      "school": "Massachusetts Institute of Technology",
      "ranking": 5678,
      "country": "United States"
    }
  ]
}
```

### GET `/profiles/{username}`

**Description**: Get detailed profile for a specific user.

**Path Parameters**:
- `username`: LeetCode username

**Query Parameters**:
- `refresh` (optional): Set to `true` to fetch fresh data from LeetCode instead of using cache

**Response**:
```json
{
  "cached": true,
  "profile": {
    "username": "alice",
    "realName": "Alice Johnson",
    "aboutMe": "Software Engineer",
    "countryName": "United States",
    "ranking": 5678,
    "school": "Massachusetts Institute of Technology",
    "company": "Google",
    "websites": ["https://alice.dev"]
  }
}
```

### POST `/refresh`

**Description**: Trigger a background task to scrape LeetCode and update cached profiles.

**Request Body**:
```json
{
  "pages": 2,
  "max_users": 25
}
```

**Response**:
```json
{
  "started": true,
  "pages": 2,
  "max_users": 25,
  "message": "Refresh cycle scheduled."
}
```

## How It Works

### Backend Architecture

1. **FastAPI Server** (`main.py`):
   - Exposes RESTful API endpoints
   - Handles CORS for Chrome extension requests
   - Manages background tasks for data updates
   - Implements caching with JSON file storage

2. **Scraper** (`scraper.py`):
   - Authenticates with LeetCode using session tokens
   - Uses GraphQL queries to fetch:
     - Global contest rankings (paginated)
     - Individual user profiles
   - Implements polite rate limiting with random delays
   - Handles retries for failed requests
   - Rotates user agents to avoid detection

3. **Data Storage** (`users.json`):
   - Simple JSON file acting as a local database
   - Stores cached user profiles with all fetched fields
   - Atomic writes to prevent corruption
   - Automatically created on first data population

4. **Models** (`models.py`):
   - Pydantic models for type safety and validation
   - Defines data contracts for API requests/responses
   - Ensures consistent data structure across the application

### Extension Architecture

1. **Popup UI** (`popup.html` + `style.css`):
   - Clean, minimal interface
   - Input field for college search
   - Results display with user cards
   - Statistics dashboard
   - Filter functionality

2. **Business Logic** (`popup.js`):
   - Communicates with backend API
   - Handles user interactions (search, filter)
   - Manages Chrome storage for API URL persistence
   - Renders dynamic content based on API responses

3. **Manifest** (`manifest.json`):
   - Defines extension metadata and permissions
   - Specifies host permissions for backend communication
   - Configures popup behavior

### Data Flow

1. **Initial Setup**:
   ```
   User -> Backend Setup -> .env tokens -> Scraper Authentication
   ```

2. **Data Population**:
   ```
   Refresh Trigger -> Scrape Contest Rankings -> Fetch User Profiles -> Cache to JSON
   ```

3. **College Search**:
   ```
   Extension UI -> Search Input -> Backend API -> Filter JSON Cache -> Return Results -> Display Cards
   ```

4. **Profile Refresh**:
   ```
   Extension/API Request -> Check Cache -> Optionally Fetch Fresh Data -> Update Cache -> Return Profile
   ```

## Troubleshooting

### Backend Issues

#### Error: "Missing LEETCODE_SESSION or CSRFTOKEN"

**Problem**: Backend can't authenticate with LeetCode.

**Solution**:
1. Verify `.env` file exists in `backend` directory
2. Check tokens are correctly copied (no extra spaces)
3. Ensure tokens haven't expired (they can expire after a few weeks)
4. Re-obtain fresh tokens from LeetCode following [Step 1](#step-1-obtaining-leetcode-session-token-and-csrf-token)

#### Error: "GraphQL status 403" or "Status 429"

**Problem**: LeetCode is rate limiting or blocking requests.

**Solution**:
1. Wait a few minutes before trying again
2. Check if your tokens are still valid
3. Reduce `pages` and `max_users` in refresh requests
4. The scraper already includes delays and retries, but aggressive scraping can still trigger limits

#### Error: "users.json is corrupted"

**Problem**: JSON file was corrupted during write.

**Solution**:
1. Delete `backend/users.json`
2. Restart backend server
3. Trigger a new refresh cycle

#### Backend Won't Start: "Address already in use"

**Problem**: Port 8000 is already being used.

**Solution**:
```bash
# Find and gracefully terminate the process using port 8000
lsof -ti:8000 | xargs kill

# If the process doesn't stop, force kill it
lsof -ti:8000 | xargs kill -9

# Or run on a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Extension Issues

#### Error: "Failed to fetch results"

**Problem**: Extension can't reach backend.

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `manifest.json` has correct `host_permissions`
3. Check `popup.js` has correct `DEFAULT_API_BASE`
4. Look for errors in Chrome DevTools console (right-click extension popup > Inspect)

#### Extension Doesn't Load

**Problem**: Chrome rejects the extension.

**Solution**:
1. Ensure `manifest.json` is valid JSON (no syntax errors)
2. Check all referenced files exist (`popup.html`, `popup.js`, `style.css`)
3. Look for errors in `chrome://extensions/` page

#### No Results for College Search

**Problem**: Database might be empty or college name doesn't match.

**Solution**:
1. Check if database is populated: `curl http://localhost:8000/health`
2. If `profiles_cached` is 0, trigger a refresh
3. Try different search terms (abbreviations, full names, partial matches)
4. Remember: only users who have filled in their school field will be found

### Render Deployment Issues

#### App Goes to Sleep

**Problem**: Free tier apps sleep after 15 minutes of inactivity.

**Solution**:
1. Accept the 30-60 second cold start on first request
2. Consider upgrading to a paid Render plan for 24/7 uptime
3. Use a service like UptimeRobot to ping your app every 14 minutes (keeps it awake)

#### Data Lost After Redeploy

**Problem**: `users.json` is stored on ephemeral disk.

**Solution**:
1. Trigger a refresh after each deployment
2. Consider implementing Supabase for persistent storage
3. Or use Render's persistent disk feature (paid plans)

#### Environment Variables Not Working

**Problem**: Tokens not accessible in deployed app.

**Solution**:
1. Double-check environment variables in Render dashboard
2. Ensure there are no leading/trailing spaces
3. Redeploy after adding/updating environment variables

## Contributing

Contributions are welcome! Here's how you can help improve LeetSearch:

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/LeetSearch.git
   cd LeetSearch
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```

### Making Changes

1. **Backend Changes**:
   - Follow PEP 8 style guide
   - Add type hints for new functions
   - Update tests in `test_main.py`
   - Run tests: `pytest backend/test_main.py`

2. **Extension Changes**:
   - Follow existing code style
   - Test thoroughly in Chrome
   - Ensure backward compatibility with backend API

3. **Documentation**:
   - Update README.md if adding new features
   - Add inline comments for complex logic
   - Update API documentation in docstrings

### Running Tests

```bash
cd backend
pytest test_main.py -v
```

### Submitting Changes

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Add some AmazingFeature"
   ```

2. Push to your fork:
   ```bash
   git push origin feature/AmazingFeature
   ```

3. Open a Pull Request from your fork to the main repository

4. Describe your changes clearly:
   - What problem does it solve?
   - How did you test it?
   - Any breaking changes?

### Code Style Guidelines

- **Python**: Follow PEP 8, use type hints, write docstrings
- **JavaScript**: Use ES6+ features, meaningful variable names
- **Commits**: Use clear, descriptive commit messages
- **Testing**: Add tests for new features and bug fixes

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.



**Disclaimer**: This tool is for educational purposes. Please use LeetCode's API responsibly and respect their rate limits. The tokens you use are tied to your personal LeetCode account - keep them secure and never share them publicly.

