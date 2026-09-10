"""
Telegram Chatbot & Notification Service for CineSentiment AI
Handles real-time alerts for user registrations, extreme sentiment detection,
and interactive Telegram bot commands (/search, /sentiment, /popular, /stats).
"""

import os
import html
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class TelegramService:
    """
    Service wrapper for Telegram Bot API.
    Designed to be resilient and fail-safe: will not raise exceptions that break
    the Flask application if network fails or bot token is unconfigured.
    """

    def __init__(self):
        self.reload_config()

    def reload_config(self):
        """Reloads credentials from environment variables."""
        self.token = os.getenv('TELEGRAM_BOT_TOKEN', '8815093093:AAFWza3YjYqGfyGPPWdpc9lEu5XPq6T5Njs').strip()
        self.admin_chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID', '8997921567').strip()
        enabled_str = os.getenv('TELEGRAM_NOTIFICATIONS_ENABLED', 'true').strip().lower()
        self.enabled = enabled_str in ('true', '1', 'yes')
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    def is_configured(self):
        """Checks if bot is properly configured and enabled."""
        return bool(self.token and self.admin_chat_id and self.enabled)

    def send_message(self, text, chat_id=None, parse_mode='HTML'):
        """
        Sends an HTML-formatted message to a specified chat or the default admin chat.
        Returns (success: bool, response_or_error: str).
        """
        target_chat_id = chat_id or self.admin_chat_id
        if not self.token or not target_chat_id:
            logger.info("Telegram notification skipped: Token or Chat ID not configured.")
            return False, "Telegram token or chat ID not set"

        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': target_chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': False
        }

        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                logger.info(f"Telegram message delivered to chat {target_chat_id}")
                return True, "Message sent successfully"
            else:
                err_msg = f"Telegram API error {resp.status_code}: {resp.text}"
                logger.warning(err_msg)
                return False, err_msg
        except Exception as e:
            err_msg = f"Failed to send Telegram message: {str(e)}"
            logger.warning(err_msg)
            return False, err_msg

    def notify_registration(self, user, ip_address=None):
        """
        Notifies the admin when a new user registers on the CineSentiment AI website.
        """
        if not self.enabled and not (self.token and self.admin_chat_id):
            return False, "Notifications disabled"

        time_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        safe_username = html.escape(user.username)
        safe_email = html.escape(user.email)
        safe_name = html.escape(user.get_display_name())
        safe_ip = html.escape(ip_address or 'Unknown')

        msg = (
            "🎉 <b>CineSentiment AI — New User Registration!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Username:</b> <code>{safe_username}</code>\n"
            f"📧 <b>Email:</b> <code>{safe_email}</code>\n"
            f"🏷️ <b>Display Name:</b> {safe_name}\n"
            f"🕒 <b>Time:</b> <code>{time_str}</code>\n"
            f"🌐 <b>IP Address:</b> <code>{safe_ip}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ <i>User successfully created an account!</i>"
        )
        return self.send_message(msg)

    def notify_sentiment_alert(self, movie_title, review_text, sentiment_data, username=None):
        """
        Notifies admin when an extreme or notable sentiment review is submitted.
        """
        if not self.enabled and not (self.token and self.admin_chat_id):
            return False, "Notifications disabled"

        sentiment = sentiment_data.get('sentiment', 'neutral').upper()
        polarity = sentiment_data.get('polarity', 0.0)
        lang_name = sentiment_data.get('detected_lang_name', 'Unknown')
        tone = sentiment_data.get('tone_description', '')

        # Select appropriate badge
        if sentiment == 'POSITIVE':
            icon = '🟢 😍'
        elif sentiment == 'NEGATIVE':
            icon = '🔴 😡'
        else:
            icon = '🟡 😐'

        excerpt = (review_text[:280] + '...') if len(review_text) > 280 else review_text
        safe_excerpt = html.escape(excerpt)
        safe_movie = html.escape(movie_title or 'General Review')
        safe_user = html.escape(username or 'Guest Visitor')

        msg = (
            f"🧠 <b>CineSentiment AI — Review Analyzed</b> {icon}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 <b>Movie:</b> <b>{safe_movie}</b>\n"
            f"👤 <b>Reviewer:</b> {safe_user}\n"
            f"📊 <b>Sentiment:</b> <b>{sentiment}</b> (Polarity: <code>{polarity:+.2f}</code>)\n"
            f"🌐 <b>Language:</b> {lang_name}\n"
            f"🎭 <b>Tone:</b> {tone}\n"
            f"💬 <b>Review:</b>\n<i>\"{safe_excerpt}\"</i>\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        return self.send_message(msg)

    def notify_watchlist_added(self, user, movie_title, movie_id=None):
        """Notifies admin when a user bookmarks a movie."""
        if not self.enabled:
            return False, "Notifications disabled"

        safe_user = html.escape(user.username)
        safe_movie = html.escape(movie_title)
        msg = (
            "⭐ <b>Watchlist Activity</b>\n"
            f"User <code>{safe_user}</code> added <b>{safe_movie}</b> to their Watchlist."
        )
        return self.send_message(msg)

    def process_command(self, text, chat_id):
        """
        Processes chatbot incoming commands (/start, /search, /sentiment, /popular, /stats).
        Returns the response message text.
        """
        if not text:
            return "Please enter a valid command. Type /help for assistance."

        text = text.strip()
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''

        # Import dependencies lazily to avoid circular imports
        from app.api_config import search_movies, get_popular_movies
        from app.sentiment_analysis import analyze_sentiment
        from app.models import User, Watchlist, ReviewHistory

        if cmd in ('/start', '/help'):
            return (
                "🎬 <b>Welcome to CineSentiment AI Chatbot!</b>\n\n"
                "Available commands:\n"
                "🔍 <code>/search &lt;movie name&gt;</code> - Search movies on TMDb\n"
                "🧠 <code>/sentiment &lt;review text&gt;</code> - Instant NLP sentiment analysis\n"
                "🔥 <code>/popular</code> - Top trending movies today\n"
                "📊 <code>/stats</code> - Website overview & statistics\n"
                "ℹ️ <code>/help</code> - Show this menu"
            )

        elif cmd == '/search':
            if not args:
                return "⚠️ Usage: <code>/search Inception</code>"
            results = search_movies(args)[:4]
            if not results:
                return f"❌ No movies found matching <b>{html.escape(args)}</b>."
            lines = [f"🎬 <b>Search Results for '{html.escape(args)}':</b>\n"]
            for m in results:
                title = html.escape(m.get('title', 'Unknown'))
                year = m.get('year', 'N/A')
                rating = m.get('rating', 0.0)
                mid = m.get('id')
                tmdb_link = f"https://www.themoviedb.org/movie/{mid}"
                lines.append(f"• <b>{title}</b> ({year}) - ⭐ {rating}/10\n  🔗 <a href='{tmdb_link}'>View on TMDb</a>")
            return "\n".join(lines)

        elif cmd == '/sentiment':
            if not args:
                return "⚠️ Usage: <code>/sentiment Spectacular movie with great visuals!</code>"
            res = analyze_sentiment(args)
            sent = res.get('sentiment', 'neutral').upper()
            pol = res.get('polarity', 0.0)
            lang = res.get('detected_lang_name', 'en')
            tone = res.get('tone_description', '')
            icon = '🟢' if sent == 'POSITIVE' else ('🔴' if sent == 'NEGATIVE' else '🟡')
            return (
                f"{icon} <b>Sentiment Analysis Result:</b>\n\n"
                f"🏷️ <b>Verdict:</b> {sent}\n"
                f"📊 <b>Polarity:</b> <code>{pol:+.3f}</code>\n"
                f"🎭 <b>Tone:</b> {tone}\n"
                f"🌐 <b>Language:</b> {lang}\n"
                f"📈 <b>Confidence:</b> Pos {res.get('positive_pct')}% | Neu {res.get('neutral_pct')}% | Neg {res.get('negative_pct')}%\n\n"
                f"💬 <i>\"{html.escape(args[:200])}\"</i>"
            )

        elif cmd == '/popular':
            movies = get_popular_movies()[:5]
            lines = ["🔥 <b>Top Trending Movies Right Now:</b>\n"]
            for idx, m in enumerate(movies, 1):
                title = html.escape(m.get('title', 'Unknown'))
                year = m.get('year', 'N/A')
                rating = m.get('rating', 0.0)
                lines.append(f"{idx}. <b>{title}</b> ({year}) — ⭐ {rating}/10")
            return "\n".join(lines)

        elif cmd == '/stats':
            try:
                users_count = User.query.count()
                watchlist_count = Watchlist.query.count()
                reviews_count = ReviewHistory.query.count()
                return (
                    "📊 <b>CineSentiment AI Platform Statistics:</b>\n\n"
                    f"👥 <b>Registered Users:</b> {users_count}\n"
                    f"⭐ <b>Bookmarked Movies:</b> {watchlist_count}\n"
                    f"🧠 <b>Reviews Analyzed:</b> {reviews_count}\n"
                    f"⚡ <b>Engine:</b> TextBlob + VADER + Vietnamese Lexicon"
                )
            except Exception as e:
                return f"⚠️ Could not query statistics: {html.escape(str(e))}"

        return "❓ Unknown command. Type <code>/help</code> for a list of valid commands."


# Singleton instance for application-wide usage
telegram_bot = TelegramService()
