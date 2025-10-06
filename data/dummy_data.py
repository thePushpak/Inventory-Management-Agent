import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from datetime import datetime, timedelta

from init_db import init_db
from db import SessionLocal
from models import Product, Transaction

init_db()

# Products
products = [
    {
        "product_id": f"P{str(i+1).zfill(3)}",
        "name": name,
        "category": cat,
        "unit_price": price,
        "supplier": supplier,
        "reorder_level": np.random.randint(5, 20),
        "qty_initial": np.random.randint(10, 100)
    }
    for i, (name, cat, price, supplier) in enumerate([
        ("Hammer", "Tools", 250.0, "Ace Hardware"),
        ("Screwdriver Set", "Tools", 180.0, "ToolPro"),
        ("Drill Machine", "Power Tools", 3200.0, "Bosch"),
        ("Paint Brush", "Paint", 60.0, "Asian Paints"),
        ("Measuring Tape", "Tools", 120.0, "Stanley"),
        ("Wrench", "Tools", 150.0, "Ace Hardware"),
        ("Cement Bag", "Building Material", 400.0, "UltraTech"),
        ("PVC Pipe", "Plumbing", 90.0, "Finolex"),
        ("Wire Cutter", "Electrical", 210.0, "Taparia"),
        ("LED Bulb", "Electrical", 80.0, "Philips"),
        ("Wall Putty", "Paint", 350.0, "Birla"),
        ("Angle Grinder", "Power Tools", 2700.0, "Bosch"),
        ("Sandpaper Pack", "Paint", 40.0, "Local"),
        ("Pipe Wrench", "Plumbing", 220.0, "Stanley"),
        ("Switch Board", "Electrical", 130.0, "Anchor"),
        ("Door Lock", "Hardware", 480.0, "Godrej"),
        ("Nails Pack", "Hardware", 35.0, "Local"),
        ("Ceiling Fan", "Electrical", 1800.0, "Usha"),
        ("Paint Roller", "Paint", 110.0, "Asian Paints"),
        ("Safety Gloves", "Safety", 90.0, "3M"),
    ])
]

np.random.seed(42)
transactions = []
for i in range(20):
    kind = np.random.choice(["purchase", "sale"])
    product = np.random.choice(products)
    qty = np.random.randint(1, 15)
    unit_price = product["unit_price"] * (1 + np.random.uniform(-0.1, 0.1))
    transactions.append({
        "tx_id": f"T{str(i+1).zfill(3)}",
        "ts": datetime.now() - timedelta(days=np.random.randint(0, 30)),
        "product_id": product["product_id"],
        "kind": kind,
        "qty": qty,
        "unit_price": round(unit_price, 2),
        "note": f"{kind.capitalize()} of {qty} units"
    })

db = SessionLocal()
try:
    # Clear old data
    db.query(Transaction).delete()
    db.query(Product).delete()
    db.commit()
    # Insert products
    for prod in products:
        db.merge(Product(**prod))
    db.commit()
    # Insert transactions
    for tx in transactions:
        db.merge(Transaction(**tx))
    db.commit()
    print(f"Inserted {len(products)} products and {len(transactions)} transactions.")
finally:
    db.close()