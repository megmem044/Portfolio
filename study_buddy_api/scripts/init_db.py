# scripts/init_db.py

from app.db import Base, engine
from app.models import Topic


# All tables registered on Base are created here.
# Importing models above is what ensures they are registered.
def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("tables created")


if __name__ == "__main__":
    main()
