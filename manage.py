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
                print(f" ID: {u.id} | Username: {u.username} | Email: {u.email} | Name: {u.get_display_name()} | Created: {created}")
            print("=" * 60)
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

    # Default: Start Development Server
    print("=" * 60)
    print(" CineSentiment AI - Movie Discovery & Sentiment Intelligence ")
    print(" Server running on: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)

