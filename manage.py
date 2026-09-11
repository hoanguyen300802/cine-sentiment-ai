import sys
from app import app
from app.models import db, User

if __name__ == '__main__':
    args = sys.argv[1:]

    # CLI Utility: List all users
    if args and args[0] == 'list-users':
        with app.app_context():
            users = User.query.all()
            print("=" * 60)
            print(f" TOTAL REGISTERED USERS: {len(users)}")
            print("=" * 60)
            for u in users:
                created = u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else 'N/A'
                role = "ADMIN" if getattr(u, 'is_admin', False) else "USER"
                print(f" ID: {u.id} | [{role}] {u.username} | Email: {u.email} | Name: {u.get_display_name()} | Created: {created}")
            print("=" * 60)
        sys.exit(0)

    # CLI Utility: Create an Administrator account
    elif args and args[0] == 'create-admin':
        if len(args) < 4:
            print("Usage: python manage.py create-admin <username> <email> <password> [display_name]")
            sys.exit(1)
        uname = args[1].strip()
        email = args[2].strip().lower()
        pwd = args[3].strip()
        dname = args[4].strip() if len(args) > 4 else uname
        with app.app_context():
            existing = User.query.filter((User.username == uname) | (User.email == email)).first()
            if existing:
                existing.is_admin = True
                existing.set_password(pwd)
                db.session.commit()
                print(f"[SUCCESS] User '{existing.username}' updated to ADMINISTRATOR with new password.")
            else:
                new_admin = User(
                    username=uname,
                    email=email,
                    display_name=dname,
                    is_admin=True
                )
                new_admin.set_password(pwd)
                db.session.add(new_admin)
                db.session.commit()
                print("=" * 60)
                print("[SUCCESS] Administrator account created successfully!")
                print(f" Username    : {uname}")
                print(f" Email       : {email}")
                print(f" Display Name: {dname}")
                print(f" Role        : ADMINISTRATOR (is_admin=True)")
                print("=" * 60)
        sys.exit(0)

    # CLI Utility: Promote existing user to Admin
    elif args and args[0] == 'set-admin':
        if len(args) < 2:
            print("Usage: python manage.py set-admin <username_or_email>")
            sys.exit(1)
        target = args[1].strip()
        with app.app_context():
            u = User.query.filter((User.username == target) | (User.email == target.lower())).first()
            if not u:
                print(f"[ERROR] User '{target}' not found.")
                sys.exit(1)
            u.is_admin = True
            db.session.commit()
            print(f"[SUCCESS] User '{u.username}' promoted to ADMINISTRATOR.")
        sys.exit(0)

    # CLI Utility: Delete a specific user by username or email
    elif args and args[0] == 'delete-user':
        if len(args) < 2:
            print("Usage: python manage.py delete-user <username_or_email>")
            sys.exit(1)
        target = args[1].strip()
        with app.app_context():
            user = User.query.filter((User.username == target) | (User.email == target.lower())).first()
            if not user:
                print(f"[ERROR] User '{target}' not found in database.")
                sys.exit(1)
            
            uname = user.username
            uid = user.id
            db.session.delete(user)
            db.session.commit()
            print(f"[SUCCESS] Successfully deleted user '{uname}' (ID: {uid}) and all associated data!")
        sys.exit(0)

    # CLI Utility: Delete all users
    elif args and args[0] == 'delete-all-users':
        with app.app_context():
            count = User.query.count()
            confirm = input(f"[WARNING] Are you sure you want to delete ALL {count} users? (y/N): ")
            if confirm.strip().lower() == 'y':
                User.query.delete()
                db.session.commit()
                print(f"[SUCCESS] Deleted all {count} users from database.")
            else:
                print("Cancelled.")
        sys.exit(0)

    # CLI Utility: Test Telegram Neutral Comment Alert
    elif args and args[0] == 'test-neutral-alert':
        with app.app_context():
            from app.telegram_bot import telegram_bot
            from app.sentiment_analysis import analyze_sentiment
            sample_text = args[1] if len(args) > 1 else "Phim xem bình thường, nội dung tạm ổn, không quá xuất sắc."
            movie_title = args[2] if len(args) > 2 else "Inception (Test)"
            res = analyze_sentiment(sample_text)
            print("=" * 60)
            print(" TESTING TELEGRAM NEUTRAL REVIEW NOTIFICATION")
            print("=" * 60)
            print(f" Movie Title : {movie_title}")
            print(f" Review Text : {sample_text}")
            print(f" Sentiment   : {res.get('sentiment')}")
            print(f" Polarity    : {res.get('polarity')}")
            print(f" Confidence  : Neu {res.get('neutral_pct')}% | Pos {res.get('positive_pct')}% | Neg {res.get('negative_pct')}%")
            print("-" * 60)
            success, msg = telegram_bot.notify_neutral_alert(
                movie_title=movie_title,
                review_text=sample_text,
                sentiment_data=res,
                username="Admin Tester"
            )
            print(f" Telegram Dispatch: {'[SUCCESS]' if success else '[FAILED]'}")
            print(f" Server Message   : {msg}")
            print("=" * 60)
        sys.exit(0)

    # Default: Start Development Server
    print("=" * 60)
    print(" CineSentiment AI - Movie Discovery & Sentiment Intelligence ")
    print(" Server running on: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)

