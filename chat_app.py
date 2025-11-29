import streamlit as st
import sqlite3
from datetime import datetime
import time
import hashlib

# Database file
DB_FILE = "chat_app.db"

# Database initialization
def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read INTEGER DEFAULT 0,
            FOREIGN KEY (sender) REFERENCES users(username),
            FOREIGN KEY (receiver) REFERENCES users(username)
        )
    ''')
    
    # Online status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS online_status (
            username TEXT PRIMARY KEY,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    conn.close()

# Hash password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User management functions
def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                      (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                  (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users ORDER BY username')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# Message management functions
def send_message(sender, receiver, content):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO messages (sender, receiver, content, timestamp) 
        VALUES (?, ?, ?, ?)
    ''', (sender, receiver, content, current_time))
    conn.commit()
    conn.close()

def get_conversation(user1, user2):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, sender, receiver, content, timestamp, read
        FROM messages
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp ASC
    ''', (user1, user2, user2, user1))
    messages = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": msg[0],
            "sender": msg[1],
            "receiver": msg[2],
            "content": msg[3],
            "timestamp": msg[4],
            "read": msg[5]
        }
        for msg in messages
    ]

def mark_messages_as_read(receiver, sender):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE messages 
        SET read = 1 
        WHERE receiver = ? AND sender = ? AND read = 0
    ''', (receiver, sender))
    conn.commit()
    conn.close()

def get_unread_count(receiver, sender):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) 
        FROM messages 
        WHERE receiver = ? AND sender = ? AND read = 0
    ''', (receiver, sender))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_contacts(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT 
            CASE 
                WHEN sender = ? THEN receiver 
                ELSE sender 
            END AS contact
        FROM messages
        WHERE sender = ? OR receiver = ?
        ORDER BY contact
    ''', (username, username, username))
    contacts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return contacts

def get_last_message_time(user1, user2):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(timestamp)
        FROM messages
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
    ''', (user1, user2, user2, user1))
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else ""

# Online status management
def update_online_status(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT OR REPLACE INTO online_status (username, last_seen)
        VALUES (?, ?)
    ''', (username, current_time))
    conn.commit()
    conn.close()

def remove_online_status(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM online_status WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def is_user_online(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT last_seen FROM online_status WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        last_seen = datetime.fromisoformat(result[0])
        # Consider online if last seen within 10 seconds
        time_diff = (datetime.now() - last_seen).total_seconds()
        return time_diff < 10
    return False

# Initialize database
init_database()

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "selected_contact" not in st.session_state:
    st.session_state.selected_contact = None
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Page configuration
st.set_page_config(page_title="Chat App", page_icon="💬", layout="wide")

# Custom CSS - Dark Theme Optimized
st.markdown("""
<style>
    .chat-message {
        padding: 10px 15px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 70%;
        word-wrap: break-word;
    }
    .sent-message {
        background: linear-gradient(135deg, #005c4b 0%, #00a884 100%);
        color: white;
        margin-left: auto;
        text-align: right;
        box-shadow: 0 2px 5px rgba(0, 168, 132, 0.3);
    }
    .received-message {
        background-color: #262730;
        color: #e4e4e7;
        margin-right: auto;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        border: 1px solid #3d3d47;
    }
    .chat-header {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d3a 100%);
        color: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #3d3d47;
    }
    .message-time {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.6);
        margin-top: 5px;
    }
    .sent-message .message-time {
        color: rgba(255, 255, 255, 0.7);
    }
    .received-message .message-time {
        color: rgba(228, 228, 231, 0.6);
    }
    .unread-badge {
        background-color: #00a884;
        color: white;
        border-radius: 50%;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0, 168, 132, 0.4);
    }
    .welcome-screen {
        text-align: center;
        padding: 100px 20px;
        color: #e4e4e7;
    }
    .welcome-screen h1 {
        color: #00a884;
        font-weight: 600;
    }
    .welcome-screen p {
        color: #a1a1aa;
    }
    /* Fix button styling for dark theme */
    .stButton button {
        background-color: #262730;
        color: #e4e4e7;
        border: 1px solid #3d3d47;
    }
    .stButton button:hover {
        background-color: #3d3d47;
        border-color: #00a884;
    }
    /* Info box styling for dark theme */
    .stAlert {
        background-color: #262730;
        color: #e4e4e7;
        border: 1px solid #3d3d47;
    }
</style>
""", unsafe_allow_html=True)

# Login/Register Page
if not st.session_state.logged_in:
    st.title("💬 Chat Application")
    st.markdown("### Connect with friends in real-time!")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit:
                if login_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    update_online_status(login_username)
                    st.success("✅ Logged in successfully!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
    
    with tab2:
        st.subheader("Create a new account")
        with st.form("register_form"):
            reg_username = st.text_input("Username")
            reg_password = st.text_input("Password", type="password")
            reg_password_confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register", type="primary", use_container_width=True)
            
            if submit:
                if not reg_username or not reg_password:
                    st.error("❌ Please fill in all fields")
                elif len(reg_username) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif reg_password != reg_password_confirm:
                    st.error("❌ Passwords do not match")
                elif len(reg_password) < 4:
                    st.error("❌ Password must be at least 4 characters")
                else:
                    if register_user(reg_username, reg_password):
                        st.success("✅ Account created successfully! Please login.")
                    else:
                        st.error("❌ Username already exists")

# Chat Interface
else:
    # Update online status
    update_online_status(st.session_state.username)
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title(f"💬 {st.session_state.username}")
    with col3:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            remove_online_status(st.session_state.username)
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.selected_contact = None
            st.rerun()
    
    st.divider()
    
    # Main chat layout
    col_contacts, col_chat = st.columns([1, 3])
    
    # Contacts sidebar
    with col_contacts:
        st.subheader("💭 Chats")
        
        # New chat section
        with st.expander("➕ New Chat", expanded=False):
            all_users = get_all_users()
            available_users = [u for u in all_users if u != st.session_state.username]
            
            if available_users:
                new_contact = st.selectbox("Select user", available_users, key="new_contact")
                if st.button("Start Chat", use_container_width=True):
                    st.session_state.selected_contact = new_contact
                    st.rerun()
            else:
                st.info("No other users registered yet")
        
        st.markdown("---")
        
        # Display contacts with unread messages
        contacts = get_all_contacts(st.session_state.username)
        
        if contacts:
            # Sort by last message time
            contacts_with_time = [(c, get_last_message_time(st.session_state.username, c)) for c in contacts]
            contacts_sorted = sorted(contacts_with_time, key=lambda x: x[1], reverse=True)
            
            for contact, _ in contacts_sorted:
                unread = get_unread_count(st.session_state.username, contact)
                online = is_user_online(contact)
                
                status_indicator = "🟢" if online else "⚫"
                
                col_btn, col_badge = st.columns([4, 1])
                with col_btn:
                    if st.button(
                        f"{status_indicator} **{contact}**",
                        key=f"contact_{contact}",
                        use_container_width=True
                    ):
                        st.session_state.selected_contact = contact
                        st.rerun()
                
                with col_badge:
                    if unread > 0:
                        st.markdown(f"<span class='unread-badge'>{unread}</span>", unsafe_allow_html=True)
        else:
            st.info("📭 No conversations yet.\n\nStart a new chat!")
    
    # Chat area
    with col_chat:
        if st.session_state.selected_contact:
            contact = st.session_state.selected_contact
            online = is_user_online(contact)
            status = "🟢 Online" if online else "⚫ Offline"
            
            # Chat header
            st.markdown(f"""
            <div class='chat-header'>
                <h2 style='margin: 0;'>{contact}</h2>
                <div style='font-size: 14px; margin-top: 5px;'>{status}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mark messages as read
            mark_messages_as_read(st.session_state.username, contact)
            
            # Display conversation
            conversation = get_conversation(st.session_state.username, contact)
            
            # Chat messages container
            chat_container = st.container(height=450)
            with chat_container:
                if conversation:
                    for msg in conversation:
                        is_sent = msg["sender"] == st.session_state.username
                        msg_class = "sent-message" if is_sent else "received-message"
                        
                        try:
                            msg_time = datetime.strptime(msg["timestamp"], '%Y-%m-%d %H:%M:%S')
                            timestamp = msg_time.strftime("%I:%M %p")
                        except:
                            timestamp = msg["timestamp"]
                        
                        st.markdown(f"""
                        <div class='chat-message {msg_class}'>
                            <div style='font-size: 15px;'>{msg["content"]}</div>
                            <div class='message-time'>{timestamp}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"👋 No messages yet. Say hi to {contact}!")
            
            # Message input
            with st.form("message_form", clear_on_submit=True):
                col_input, col_send = st.columns([5, 1])
                with col_input:
                    message = st.text_input("Type a message...", key="message_input", label_visibility="collapsed")
                with col_send:
                    send_btn = st.form_submit_button("📤", use_container_width=True)
                
                if send_btn and message.strip():
                    send_message(st.session_state.username, contact, message.strip())
                    st.rerun()
            
            # Auto-refresh every 2 seconds
            if time.time() - st.session_state.last_refresh > 2:
                st.session_state.last_refresh = time.time()
                st.rerun()
        
        else:
            # Welcome screen
            st.markdown("""
            <div class='welcome-screen'>
                <h1>💬 Welcome to Chat App!</h1>
                <p style='font-size: 18px;'>Select a contact from the left sidebar to start chatting</p>
                <p style='font-size: 16px;'>or create a new conversation</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show stats
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                total_users = len(get_all_users())
                st.metric("👥 Total Users", total_users)
            with col2:
                my_contacts = len(get_all_contacts(st.session_state.username))
                st.metric("💬 Your Chats", my_contacts)
            with col3:
                total_unread = sum(get_unread_count(st.session_state.username, c) 
                                  for c in get_all_contacts(st.session_state.username))
                st.metric("📬 Unread", total_unread)