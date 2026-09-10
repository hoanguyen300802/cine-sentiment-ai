"""
Authentication and User Account Blueprint for CineSentiment AI
Handles registration, login, logout, profile settings, and Telegram test alerts.
"""

import re
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Watchlist, ReviewHistory
from app.telegram_bot import telegram_bot
from app.translations import get_translations, DEFAULT_LANGUAGE

auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    """Simple regex email validator."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip())) if email else False


def is_valid_username(username):
    """Username validator: alphanumeric and underscores only, length 3-30."""
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return bool(re.match(pattern, username.strip())) if username else False


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    t = get_translations(current_lang)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        display_name = request.form.get('display_name', '').strip() or username

        errors = []

        if not username or not email or not password:
            errors.append(t.get('err_required_fields', 'Please fill in all required fields.'))

        if not is_valid_username(username):
            errors.append(t.get('err_invalid_username', 'Username must be 3-30 characters (letters, numbers, underscore).'))

        if not is_valid_email(email):
            errors.append(t.get('err_invalid_email', 'Please enter a valid email address.'))

        if len(password) < 6:
            errors.append(t.get('err_password_short', 'Password must be at least 6 characters long.'))

        if password != confirm_password:
            errors.append(t.get('err_password_mismatch', 'Passwords do not match.'))

        # Check existing username & email
        if not errors:
            if User.query.filter_by(username=username).first():
                errors.append(t.get('err_username_exists', 'This username is already taken. Please choose another.'))
            elif User.query.filter_by(email=email).first():
                errors.append(t.get('err_email_exists', 'This email is already registered. Please log in.'))

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template(
                'auth/register.html',
                username=username,
                email=email,
                display_name=display_name
            )

        # Create new user
        new_user = User(
            username=username,
            email=email,
            display_name=display_name,
            created_at=datetime.utcnow()
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

            # Auto login user
            login_user(new_user, remember=True)

            # Trigger Telegram notification
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            telegram_bot.notify_registration(new_user, ip_address=client_ip)

            flash(t.get('msg_register_success', 'Account created successfully! Welcome to CineSentiment AI.'), 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", 'error')
            return render_template('auth/register.html', username=username, email=email)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication and login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    t = get_translations(current_lang)

    if request.method == 'POST':
        identifier = request.form.get('login_identifier', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not identifier or not password:
            flash(t.get('err_missing_credentials', 'Please enter your username/email and password.'), 'error')
            return render_template('auth/login.html', identifier=identifier)

        # Look up by username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=remember)
            flash(f"{t.get('msg_welcome_back', 'Welcome back')}, {user.get_display_name()}!", 'success')

            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('index'))
        else:
            flash(t.get('err_invalid_login', 'Invalid username/email or password.'), 'error')
            return render_template('auth/login.html', identifier=identifier)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logs the user out."""
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    t = get_translations(current_lang)

    logout_user()
    flash(t.get('msg_logged_out', 'You have been logged out successfully.'), 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management page."""
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    t = get_translations(current_lang)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_info':
            display_name = request.form.get('display_name', '').strip()
            bio = request.form.get('bio', '').strip()

            if display_name:
                current_user.display_name = display_name
            current_user.bio = bio[:300]
            db.session.commit()
            flash(t.get('msg_profile_updated', 'Profile updated successfully!'), 'success')

        elif action == 'change_password':
            old_pass = request.form.get('old_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_new = request.form.get('confirm_new_password', '')

            if not current_user.check_password(old_pass):
                flash(t.get('err_wrong_old_password', 'Current password is incorrect.'), 'error')
            elif len(new_pass) < 6:
                flash(t.get('err_password_short', 'New password must be at least 6 characters.'), 'error')
            elif new_pass != confirm_new:
                flash(t.get('err_password_mismatch', 'Passwords do not match.'), 'error')
            else:
                current_user.set_password(new_pass)
                db.session.commit()
                flash(t.get('msg_password_changed', 'Password changed successfully!'), 'success')

        return redirect(url_for('auth.profile'))

    watchlist_count = current_user.watchlist_items.count()
    reviews_count = current_user.reviews.count()
    recent_watchlist = current_user.watchlist_items.order_by(Watchlist.added_at.desc()).limit(6).all()
    recent_reviews = current_user.reviews.order_by(ReviewHistory.created_at.desc()).limit(5).all()

    return render_template(
        'auth/profile.html',
        watchlist_count=watchlist_count,
        reviews_count=reviews_count,
        recent_watchlist=recent_watchlist,
        recent_reviews=recent_reviews,
        telegram_configured=telegram_bot.is_configured()
    )


@auth_bp.route('/api/check_username')
def check_username():
    """AJAX check for username availability."""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'available': False, 'message': 'Username is empty'})

    if not is_valid_username(username):
        return jsonify({'available': False, 'message': 'Invalid format (3-30 chars, alphanumeric/_)'})

    exists = User.query.filter_by(username=username).first() is not None
    return jsonify({
        'available': not exists,
        'message': 'Username already taken' if exists else 'Username available'
    })


@auth_bp.route('/api/telegram/test_alert', methods=['POST'])
@login_required
def test_telegram_alert():
    """Endpoint allowing ONLY admin users to test Telegram Bot integration."""
    if not getattr(current_user, 'is_admin', False):
        return jsonify({
            'success': False,
            'message': 'Access denied: Only administrator accounts can test Telegram settings.'
        }), 403

    success, msg = telegram_bot.send_message(
        f"🧪 <b>CineSentiment AI — Test Notification</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Triggered by Administrator: <code>{current_user.username}</code>\n"
        f"🕒 Time: <code>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</code>\n"
        f"✅ Bot notification pipeline is functioning perfectly!"
    )
    return jsonify({'success': success, 'message': msg})


@auth_bp.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """Optional webhook receiver for interactive Telegram Bot commands."""
    data = request.get_json(silent=True) or {}
    message = data.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if chat_id and text:
        reply_text = telegram_bot.process_command(text, chat_id)
        telegram_bot.send_message(reply_text, chat_id=chat_id)

    return jsonify({'status': 'ok'})
