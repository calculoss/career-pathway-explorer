# enhanced_auth.py
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict
import smtplib
from email.mime.text import MimeText
import streamlit as st


class EnhancedAuthSystem:
    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path
        self.init_auth_tables()

    def init_auth_tables(self):
        """Initialize enhanced authentication tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enhanced families table with email/password auth
        cursor.execute('''
            ALTER TABLE families ADD COLUMN password_hash TEXT;
        ''')

        cursor.execute('''
            ALTER TABLE families ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
        ''')

        cursor.execute('''
            ALTER TABLE families ADD COLUMN reset_token TEXT;
        ''')

        cursor.execute('''
            ALTER TABLE families ADD COLUMN reset_token_expires DATETIME;
        ''')

        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                family_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                user_agent TEXT,
                ip_address TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (family_id) REFERENCES families (id)
            )
        ''')

        # Email verification tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id TEXT,
                token TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (family_id) REFERENCES families (id)
            )
        ''')

        conn.commit()
        conn.close()

    def hash_password(self, password: str) -> str:
        """Securely hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                            password.encode('utf-8'),
                                            salt.encode('utf-8'),
                                            100000)
        return f"{salt}:{password_hash.hex()}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256',
                                                      password.encode('utf-8'),
                                                      salt.encode('utf-8'),
                                                      100000)
            return password_hash_check.hex() == hash_value
        except:
            return False

    def register_family_with_password(self, family_name: str, email: str,
                                      password: str, location: str = "") -> Dict:
        """Register family with email/password authentication"""
        import uuid
        import random
        import string

        family_id = str(uuid.uuid4())
        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        password_hash = self.hash_password(password)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO families (id, family_name, email, location, access_code, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (family_id, family_name, email, location, access_code, password_hash))

        conn.commit()
        conn.close()

        # Send verification email
        verification_token = self.create_email_verification_token(family_id)
        self.send_verification_email(email, family_name, verification_token)

        return {
            'family_id': family_id,
            'access_code': access_code,
            'status': 'success',
            'message': 'Registration successful. Please check your email to verify your account.'
        }

    def authenticate_family(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate family with email/password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, family_name, email, location, access_code, password_hash, email_verified
            FROM families WHERE email = ?
        ''', (email,))

        result = cursor.fetchone()
        conn.close()

        if result and self.verify_password(password, result[5]):
            return {
                'id': result[0],
                'family_name': result[1],
                'email': result[2],
                'location': result[3],
                'access_code': result[4],
                'email_verified': result[6]
            }
        return None

    def create_session(self, family_id: str, user_agent: str = "", ip_address: str = "") -> str:
        """Create new user session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)  # 24-hour sessions

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_sessions (id, family_id, expires_at, user_agent, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, family_id, expires_at, user_agent, ip_address))

        conn.commit()
        conn.close()

        return session_id

    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate active session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.family_id, f.family_name, f.email, s.expires_at
            FROM user_sessions s
            JOIN families f ON s.family_id = f.id
            WHERE s.id = ? AND s.is_active = TRUE AND s.expires_at > ?
        ''', (session_id, datetime.now()))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'family_id': result[0],
                'family_name': result[1],
                'email': result[2],
                'expires_at': result[3]
            }
        return None

    def create_email_verification_token(self, family_id: str) -> str:
        """Create email verification token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO email_verification_tokens (family_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (family_id, token, expires_at))

        conn.commit()
        conn.close()

        return token

    def send_verification_email(self, email: str, family_name: str, token: str):
        """Send email verification (you'll need to configure SMTP)"""
        # This is a template - you'll need to configure your SMTP settings
        verification_url = f"https://your-app-url.com/verify-email?token={token}"

        message = f"""
        Hi {family_name},

        Welcome to CareerPath! Please verify your email address by clicking the link below:

        {verification_url}

        This link will expire in 24 hours.

        Best regards,
        CareerPath Team
        """

        # You'd implement actual email sending here
        print(f"Verification email would be sent to {email}")
        print(f"Verification URL: {verification_url}")


# Streamlit UI components for enhanced auth
def create_enhanced_login_form():
    """Enhanced login form with both email/password and access code options"""
    st.markdown("### Login to Your Family Account")

    login_method = st.radio("Login Method", ["Email & Password", "Access Code"])

    if login_method == "Email & Password":
        with st.form("email_login"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me for 30 days")

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Login", use_container_width=True)
            with col2:
                forgot_password = st.form_submit_button("Forgot Password?", use_container_width=True)

            if submitted and email and password:
                auth_system = EnhancedAuthSystem()
                family_info = auth_system.authenticate_family(email, password)

                if family_info:
                    if family_info['email_verified']:
                        # Create session
                        session_id = auth_system.create_session(family_info['id'])
                        st.session_state.family_session = session_id
                        st.session_state.authenticated_family = family_info
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.warning("Please verify your email address before logging in.")
                else:
                    st.error("Invalid email or password.")

    else:  # Access Code method (backward compatibility)
        with st.form("access_code_login"):
            access_code = st.text_input("Family Access Code", placeholder="e.g., SMITH123")
            submitted = st.form_submit_button("Access Family", use_container_width=True)

            if submitted and access_code:
                # Your existing access code logic
                pass


def create_enhanced_registration_form():
    """Enhanced registration form with email verification"""
    st.markdown("### Create Your Family Account")

    with st.form("enhanced_registration"):
        col1, col2 = st.columns(2)

        with col1:
            family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
            email = st.text_input("Email Address *", placeholder="your.email@example.com")

        with col2:
            password = st.text_input("Password *", type="password",
                                     help="Minimum 8 characters, include letters and numbers")
            confirm_password = st.text_input("Confirm Password *", type="password")
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

        st.markdown("### First Student")
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input("Student Name *")
            age = st.number_input("Age", min_value=14, max_value=20, value=16)

        with col2:
            year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)
            interests = st.text_area("Interests", placeholder="e.g., history, science, writing")

        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy *")

        submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            # Validation
            errors = []

            if not all([family_name, email, password, confirm_password, student_name]):
                errors.append("Please fill in all required fields.")

            if password != confirm_password:
                errors.append("Passwords do not match.")

            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")

            if not terms_accepted:
                errors.append("Please accept the Terms of Service.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create account
                auth_system = EnhancedAuthSystem()
                result = auth_system.register_family_with_password(
                    family_name, email, password, location
                )

                if result['status'] == 'success':
                    st.success(result['message'])
                    st.info("A verification link has been sent to your email address.")