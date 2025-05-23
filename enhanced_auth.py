# enhanced_auth.py - Clean version with NO email dependencies
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict
import streamlit as st


class EnhancedAuthSystem:
    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path
        self.init_auth_tables()

    def init_auth_tables(self):
        """Initialize enhanced authentication tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('ALTER TABLE families ADD COLUMN password_hash TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute('ALTER TABLE families ADD COLUMN email_verified BOOLEAN DEFAULT TRUE')
        except sqlite3.OperationalError:
            pass  # Column already exists

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

        # Login events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id TEXT,
                login_method TEXT,
                login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
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
            INSERT INTO families (id, family_name, email, location, access_code, password_hash, email_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (family_id, family_name, email, location, access_code, password_hash, True))

        conn.commit()
        conn.close()

        return {
            'family_id': family_id,
            'access_code': access_code,
            'status': 'success',
            'message': 'Registration successful!'
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

        if result and result[5] and self.verify_password(password, result[5]):
            return {
                'id': result[0],
                'family_name': result[1],
                'email': result[2],
                'location': result[3],
                'access_code': result[4],
                'email_verified': True
            }
        return None

    def create_session(self, family_id: str, user_agent: str = "", ip_address: str = "") -> str:
        """Create new user session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)

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
            SELECT s.family_id, f.family_name, f.email, f.location, s.expires_at
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
                'location': result[3],
                'expires_at': result[4]
            }
        return None

    def logout_session(self, session_id: str):
        """Logout session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE user_sessions SET is_active = FALSE WHERE id = ?
        ''', (session_id,))

        conn.commit()
        conn.close()

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE user_sessions SET is_active = FALSE 
            WHERE expires_at < ? AND is_active = TRUE
        ''', (datetime.now(),))

        conn.commit()
        conn.close()


def create_enhanced_login_form():
    """Enhanced login form"""
    st.markdown("### 🔐 Login to Your Family Account")

    tab1, tab2 = st.tabs(["📧 Email & Password", "🔑 Access Code"])

    with tab1:
        with st.form("email_login"):
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Login", use_container_width=True)
            with col2:
                forgot_button = st.form_submit_button("Forgot Password?", use_container_width=True)

            if submitted and email and password:
                auth_system = st.session_state.get('enhanced_auth')
                if auth_system:
                    family_info = auth_system.authenticate_family(email, password)

                    if family_info:
                        session_id = auth_system.create_session(family_info['id'])
                        st.session_state.family_session = session_id
                        st.session_state.authenticated_family = family_info

                        track_login_event(family_info['id'], 'email_password')

                        st.success(f"Welcome back, {family_info['family_name']}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

            if forgot_button:
                st.info("💡 Try logging in with your access code in the other tab.")

    with tab2:
        with st.form("access_code_login"):
            access_code = st.text_input("Family Access Code", placeholder="e.g., SMITH123")
            submitted = st.form_submit_button("Access Family", use_container_width=True)

            if submitted and access_code:
                db = st.session_state.get('secure_db')
                if db:
                    family_info = db.verify_family_access(access_code.upper())

                    if family_info:
                        auth_system = st.session_state.get('enhanced_auth')
                        if auth_system:
                            session_id = auth_system.create_session(family_info['id'])
                            st.session_state.family_session = session_id

                        st.session_state.authenticated_family = family_info

                        track_login_event(family_info['id'], 'access_code')

                        st.success(f"Welcome back, {family_info['family_name']}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid access code.")


def create_enhanced_registration_form():
    """Enhanced registration form - Fixed form validation"""
    st.markdown("### 👨‍👩‍👧‍👦 Create Your Family Account")

    method = st.radio(
        "Registration Method",
        ["📧 Email & Password (Recommended)", "🔑 Access Code Only"],
        help="Email registration provides better security"
    )

    if method.startswith("📧"):
        with st.form("enhanced_registration"):
            st.markdown("#### Family Information")

            col1, col2 = st.columns(2)
            with col1:
                family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
                email = st.text_input("Email Address *", placeholder="your.email@example.com")

            with col2:
                password = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Confirm Password *", type="password")
                location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

            st.markdown("#### First Student")
            student_name = st.text_input("Student Name *", placeholder="e.g., Emma")

            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=14, max_value=20, value=16)
                year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)

            with col2:
                timeline = st.selectbox("University Timeline",
                                        ["Applying in 2+ years", "Applying in 12 months", "Applying now"])
                location_pref = st.text_input("Study Location Preference", placeholder="e.g., NSW/ACT")

            interests = st.text_area("Interests", placeholder="e.g., psychology, science, writing")
            terms = st.checkbox("I agree to the Terms of Service *")

            # THIS IS THE ONLY BUTTON ALLOWED IN THE FORM
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        # HANDLE FORM SUBMISSION OUTSIDE THE FORM
        if submitted:
            errors = []

            if not all([family_name, email, password, student_name]):
                errors.append("Please fill in all required fields.")

            if password != confirm_password:
                errors.append("Passwords do not match.")

            if len(password) < 8:
                errors.append("Password must be at least 8 characters.")

            if not terms:
                errors.append("Please accept the Terms of Service.")

            # Check for existing email
            if not errors:
                try:
                    conn = sqlite3.connect("community_career_explorer.db")
                    cursor = conn.cursor()
                    cursor.execute('SELECT id FROM families WHERE email = ?', (email,))
                    if cursor.fetchone():
                        errors.append("An account with this email already exists.")
                    conn.close()
                except:
                    pass

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # SUCCESS - CREATE ACCOUNT
                try:
                    auth_system = st.session_state.get('enhanced_auth')
                    if auth_system:
                        result = auth_system.register_family_with_password(
                            family_name, email, password, location
                        )

                        if result['status'] == 'success':
                            # Add student
                            db = st.session_state.get('secure_db')
                            if db:
                                student_data = {
                                    'name': student_name,
                                    'age': age,
                                    'year_level': year_level,
                                    'interests': [i.strip() for i in interests.split(',') if i.strip()],
                                    'preferences': [],
                                    'timeline': timeline,
                                    'location_preference': location_pref,
                                    'career_considerations': [],
                                    'goals': []
                                }
                                db.add_student(result['family_id'], student_data)

                            # Show success message
                            st.success("🎉 Account created successfully!")

                            # Store registration success in session state
                            st.session_state.registration_success = {
                                'family_id': result['family_id'],
                                'family_name': family_name,
                                'email': email,
                                'location': location,
                                'access_code': result['access_code']
                            }

                            st.balloons()  # Celebration!

                        else:
                            st.error("Registration failed. Please try again.")
                    else:
                        st.error("Authentication system not available.")
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")

        # SHOW SUCCESS INFO AND CONTINUE BUTTON OUTSIDE THE FORM
        if 'registration_success' in st.session_state:
            reg_info = st.session_state.registration_success

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4CAF50, #45a049); 
                        color: white; padding: 2rem; border-radius: 10px; 
                        margin: 1rem 0; text-align: center;">
                <h3>🎉 Welcome to CareerPath, {reg_info['family_name']}!</h3>
                <p>Your account has been created successfully.</p>
            </div>
            """, unsafe_allow_html=True)

            # Show login details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border: 1px solid #e9ecef;">
                    <h4>📧 Email Login</h4>
                    <p><strong>Email:</strong> {}</p>
                    <p><strong>Password:</strong> As entered above</p>
                    <small>Use these to log in anytime</small>
                </div>
                """.format(reg_info['email']), unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #ffeaa7;">
                    <h4>🔑 Backup Access Code</h4>
                    <p style="font-size: 24px; font-weight: bold; color: #856404; font-family: monospace;">
                        {reg_info['access_code']}
                    </p>
                    <small>Save this code as backup!</small>
                </div>
                """, unsafe_allow_html=True)

            # Continue button OUTSIDE the form
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Continue to Dashboard", use_container_width=True, type="primary"):
                    # Auto-login the user
                    auth_system = st.session_state.get('enhanced_auth')
                    if auth_system:
                        session_id = auth_system.create_session(reg_info['family_id'])
                        st.session_state.family_session = session_id
                        st.session_state.authenticated_family = reg_info

                    # Clear registration success state
                    del st.session_state.registration_success
                    if 'show_registration' in st.session_state:
                        del st.session_state.show_registration

                    st.rerun()

    else:
        # Legacy access code registration (simplified)
        st.info("🔑 Legacy registration - you'll only receive an access code")

        with st.form("legacy_registration"):
            family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
            email = st.text_input("Email Address (Optional)", placeholder="your.email@example.com")
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

            student_name = st.text_input("Student Name *", placeholder="e.g., Emma")
            age = st.number_input("Age", min_value=14, max_value=20, value=16)

            submitted = st.form_submit_button("Create Account (Access Code Only)")

        if submitted and family_name and student_name:
            try:
                db = st.session_state.get('secure_db')
                if db:
                    family_id, access_code = db.create_family(family_name, email, location)

                    # Add basic student
                    student_data = {
                        'name': student_name,
                        'age': age,
                        'year_level': 11,
                        'interests': [],
                        'preferences': [],
                        'timeline': 'Not specified',
                        'location_preference': location,
                        'career_considerations': [],
                        'goals': []
                    }
                    db.add_student(family_id, student_data)

                    st.success("🎉 Account created!")

                    st.markdown(f"""
                    <div style="background: #fff3cd; padding: 2rem; border-radius: 10px; 
                                text-align: center; margin: 1rem 0;">
                        <h3>Your Access Code</h3>
                        <p style="font-size: 36px; font-weight: bold; color: #856404; 
                                   font-family: monospace; letter-spacing: 4px;">
                            {access_code}
                        </p>
                        <p>Save this code - it's your only way to access your account!</p>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Registration failed: {str(e)}")


def track_login_event(family_id: str, method: str):
    """Track login events"""
    try:
        conn = sqlite3.connect("community_career_explorer.db")
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO login_events (family_id, login_method)
            VALUES (?, ?)
        ''', (family_id, method))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Login tracking error: {e}")