from sqlalchemy import Column, Date, Integer, Numeric, String

from app.db.base import Base

# Transaction table definition is declared
# Each class attribute maps to a database column
class Transaction(Base):
    # Table name is defined
    __tablename__ = "transactions"

    # Primary key column is defined
    id = Column(Integer, primary_key=True, index=True)

    # Numeric avoids the rounding errors that floating-point money can cause.
    amount = Column(Numeric(12, 2), nullable=False)

    # Merchant name is stored
    merchant = Column(String(200), nullable=False)

    # Category label is stored
    category = Column(String(100), nullable=False)

    # Transaction date is stored
    date = Column(Date, nullable=False)
