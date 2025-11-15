# LeetSearch 🔍

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> Find and track LeetCode users from your college campus!

Ever wondered which of your college friends is secretly solving LeetCode at 2 AM instead of doing assignments? This extension lets you totally not creepily find every LeetCoder in your campus. You can spot hidden tryhards, sleepy grinders, fake humble toppers, and all the people who pretend they barely code but actually never stop, lol.

## ✨ Features

- 🎓 **College-based Search**: Find LeetCode users from your specific college or university
- 📊 **User Statistics**: View comprehensive stats for each user including:
  - Problems solved (Easy, Medium, Hard)
  - Rankings and ratings
  - Recent activity
  - Submission history
- 🔄 **Real-time Updates**: Automatically scrape and update user data
- 🎯 **Campus Leaderboard**: Compare coding activity within your campus community
- 🌐 **Chrome Extension**: Easy-to-use browser extension interface

## 📁 Project Structure

```
LeetSearch/
├── backend/              # Backend server for data scraping and API
│   ├── db.py            # Database operations
│   ├── main.py          # Main backend server
│   ├── models.py        # Data models
│   ├── scraper.py       # LeetCode data scraper
│   ├── stats.py         # Statistics processing
│   ├── updater.py       # Automated data updates
│   └── requirements.txt # Python dependencies
├── extension/           # Chrome extension files
│   ├── manifest.json   # Extension manifest
│   ├── popup.html      # Extension popup UI
│   ├── popup.js        # Extension logic
│   └── style.css       # Extension styles
├── LICENSE             # Apache 2.0 License
└── README.md          # This file
```

## 🚀 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.7+** for the backend
- **Google Chrome** or **Chromium-based browser** for the extension
- **pip** (Python package manager)

## 🔧 Installation & Setup

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/saaj376/LeetSearch.git
   cd LeetSearch
   ```

2. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the backend**
   - Set up your database connection
   - Configure any necessary API keys or environment variables

5. **Run the backend server**
   ```bash
   python main.py
   ```

### Chrome Extension Setup

1. **Update the backend URL** in `extension/manifest.json`:
   ```json
   "host_permissions": [
     "https://your-backend-url.com/*"
   ]
   ```
   Replace `your-backend-url.com` with your actual backend server URL.

2. **Load the extension in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in the top-right corner)
   - Click "Load unpacked"
   - Select the `extension` folder from the cloned repository

3. **Verify installation**:
   - You should see the LeetCode College Finder icon in your Chrome toolbar
   - Click the icon to open the extension popup

## 📖 Usage

1. **Launch the Extension**
   - Click on the LeetCode College Finder icon in your Chrome toolbar

2. **Search for Users**
   - Enter your college/university name or domain
   - Browse through the list of LeetCode users from your campus

3. **View User Stats**
   - Click on any user to view their detailed statistics
   - See their problem-solving progress and rankings

4. **Track Progress**
   - The extension automatically updates user data periodically
   - Check back regularly to see how your campus community is progressing

## ⚙️ Configuration

### Backend Configuration

The backend can be configured through environment variables or a configuration file:

- **Database URL**: Connection string for your database
- **Scraping Interval**: How often to update user data
- **API Rate Limits**: Configure request throttling

### Extension Configuration

Customize the extension by modifying:
- `manifest.json`: Update permissions and backend URL
- `style.css`: Customize the appearance
- `popup.js`: Adjust functionality and behavior

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

Please make sure to:
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LeetCode for providing an amazing platform for coding practice
- The open-source community for inspiration and tools

## ⚠️ Disclaimer

This tool is for educational and community-building purposes. Please respect LeetCode's Terms of Service and use this extension responsibly. Do not use it for any malicious purposes or to violate anyone's privacy.

---

**Made with ❤️ for the coding community**
