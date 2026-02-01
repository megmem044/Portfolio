from sqlalchemy import Column, Integer, String, Float, Date

from app.db.base import Base

# Transaction table definition is declared
# Each class attribute maps to a database column
class Transaction(Base):
    # Table name is defined
    __tablename__ = "transactions"

    # Primary key column is defined
    id = Column(Integer, primary_key=True, index=True)

    # Transaction amount is stored
    amount = Column(Float, nullable=False)

    # Merchant name is stored
    merchant = Column(String, nullable=False)

    # Category label is stored
    category = Column(String, nullable=False)

    # Transaction date is stored
    date = Column(Date, nullable=False)
