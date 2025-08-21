import sys
from database.database import SessionLocal
from models.user import User
from auth.core import get_password_hash  # Убедитесь что путь правильный

def create_superuser(email: str, password: str):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print(f"❌ User {email} already exists!")
            return

        hashed_password = get_password_hash(password)
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        print(f"✅ Superuser {email} created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_superuser.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    create_superuser(email, password)