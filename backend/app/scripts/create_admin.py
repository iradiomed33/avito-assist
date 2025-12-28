import argparse
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        u = db.query(User).filter(User.username == args.username).first()
        if u:
            u.password_hash = hash_password(args.password)
            u.role = "admin"
            u.is_active = True
            db.commit()
            print(f"[OK] updated admin user: {u.username} (id={u.id})")
            return

        u = User(
            username=args.username,
            password_hash=hash_password(args.password),
            role="admin",
            is_active=True,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        print(f"[OK] created admin user: {u.username} (id={u.id})")
    finally:
        db.close()

if __name__ == "__main__":
    main()
