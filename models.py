from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from db import Base

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, nullable=True)
    unit_price = Column(Float, nullable=False)
    supplier = Column(String)
    reorder_level = Column(Integer, default=0)
    qty_initial = Column(Integer, default=0)
    

class Transaction(Base):
    __tablename__ = 'transactions'
    
    tx_id = Column(String, primary_key=True, index=True)
    ts = Column(DateTime(timezone=True), server_default=func.now())
    product_id = Column(String, nullable=False)
    kind = Column(Enum('sale', 'purchase', name='tx_kind'), nullable=False)
    qty = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    note = Column(String)
