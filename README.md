# 💬 Real-Time Chat Application

A fully-featured, real-time messaging application built with Python and Streamlit. This project demonstrates a complete chat system with user authentication, live messaging, online status tracking, and a modern dark-themed interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### 🔐 Authentication System
- **User Registration**: Secure account creation with password confirmation
- **Login System**: SHA-256 password hashing for security
- **Session Management**: Persistent login sessions

### 💬 Real-Time Messaging
- **Instant Messaging**: Send and receive messages in real-time
- **Auto-Refresh**: Automatic updates every 2 seconds
- **Message History**: Complete conversation history stored in database
- **Accurate Timestamps**: Messages timestamped with local system time

### 👥 Contact Management
- **Contact List**: View all users you've chatted with
- **New Conversations**: Start chats with any registered user
- **Smart Sorting**: Contacts sorted by most recent activity
- **User Search**: Easy-to-use contact selector

### 🔔 Notifications & Status
- **Unread Messages**: Badge indicators showing unread message count
- **Online/Offline Status**: Real-time presence indicators (🟢/⚫)
- **Read Receipts**: Messages automatically marked as read when viewed
- **Last Seen**: Track user activity with last seen timestamps

### 🎨 Modern UI/UX
- **Dark Theme**: Beautiful dark mode optimized interface
- **WhatsApp-Inspired**: Familiar chat bubble design
- **Responsive Layout**: Three-column layout with sidebar navigation
- **Gradient Messages**: Sleek teal gradient for sent messages
- **Stats Dashboard**: Overview of total users, chats, and unread messages

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/naakaarafr/Chat-App.git
cd Chat-App
```

2. **Install dependencies**
```bash
pip install streamlit
```

3. **Run the application**
```bash
streamlit run chat_app.py
```

4. **Open your browser**
The app will automatically open at `http://localhost:8501`

## 📖 Usage Guide

### Getting Started

1. **Register an Account**
   - Click on the "Register" tab
   - Enter a unique username (min 3 characters)
   - Create a password (min 4 characters)
   - Confirm your password
   - Click "Register"

2. **Login**
   - Enter your username and password
   - Click "Login"
   - You'll be redirected to the chat interface

3. **Start Chatting**
   - Click "➕ New Chat" to start a conversation
   - Select a user from the dropdown
   - Click "Start Chat"
   - Type your message and click "📤" to send

### Testing the App

To test real-time messaging:
1. Register two users (e.g., "Alice" and "Bob")
2. Login as Alice in one browser
3. Open an incognito/private window and login as Bob
4. Start a conversation and watch messages appear in real-time!

## 🗄️ Database Schema

The application uses SQLite3 with three main tables:

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- SHA-256 hashed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP,
    read INTEGER DEFAULT 0,  -- 0 = unread, 1 = read
    FOREIGN KEY (sender) REFERENCES users(username),
    FOREIGN KEY (receiver) REFERENCES users(username)
)
```

### Online Status Table
```sql
CREATE TABLE online_status (
    username TEXT PRIMARY KEY,
    last_seen TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
)
```

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Python-based web framework)
- **Database**: SQLite3 (embedded database)
- **Security**: SHA-256 password hashing
- **Styling**: Custom CSS for dark theme

### Project Structure
```
Chat-App/
├── chat_app.py          # Main application file
├── chat_app.db          # SQLite database (created on first run)
└── README.md           # Project documentation
```

### Key Components

1. **Database Layer**
   - `init_database()`: Initializes SQLite tables
   - User management functions (register, login, get users)
   - Message management functions (send, get conversation, mark as read)
   - Online status tracking functions

2. **Authentication**
   - Password hashing with SHA-256
   - Session state management
   - Login/logout functionality

3. **Chat Interface**
   - Contact sidebar with unread badges
   - Message display with timestamps
   - Real-time auto-refresh mechanism
   - Message input form

## 🔒 Security Features

- **Password Hashing**: All passwords stored as SHA-256 hashes
- **SQL Injection Protection**: Parameterized queries throughout
- **Session Management**: Secure session state handling
- **Input Validation**: Username and password requirements enforced

## 🎨 Customization

### Changing the Theme
Edit the CSS in the `st.markdown()` section to customize colors:
```python
.sent-message {
    background: linear-gradient(135deg, #005c4b 0%, #00a884 100%);
}
```

### Adjusting Auto-Refresh Rate
Modify the refresh interval (default: 2 seconds):
```python
if time.time() - st.session_state.last_refresh > 2:  # Change this value
```

### Online Status Timeout
Change how long users stay "online" after last activity:
```python
time_diff = (datetime.now() - last_seen).total_seconds()
return time_diff < 10  # Change this value (in seconds)
```

## 📝 Future Enhancements

Potential features to add:
- [ ] Group chat functionality
- [ ] File/image sharing
- [ ] Message deletion
- [ ] Typing indicators
- [ ] Message search
- [ ] User profiles with avatars
- [ ] End-to-end encryption
- [ ] Push notifications
- [ ] Voice/video calling
- [ ] Message reactions (emoji)
- [ ] Chat themes and customization
- [ ] Export chat history

## 🐛 Known Issues

- Auto-refresh may cause slight UI flicker
- Very long messages may overflow on small screens
- Multiple tabs with same user may cause status conflicts

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
