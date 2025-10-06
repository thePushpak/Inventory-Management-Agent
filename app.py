import streamlit as st
from sqlalchemy.orm import Session
from db import SessionLocal
from init_db import init_db
from models import Base, Product, Transaction
from services.analytics import (inventory_state, top_sellers, sales_summary, 
                                purchase_summary, category_performance)
from ai.gemini import summarize_day, answer_query

st.set_page_config(page_title="Inventory Dashboard", layout="wide")
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

st.title("Inventory Management Assistant")
st.caption("Made in India")

tab1, tab2, tab3, tab4 = st.tabs([
    "Catalog", "Transactions", "Dashboard", "Ask Assistant"
])

with tab1:
    st.subheader("Add / Edit Products")
    with st.form("product_form"):
        pid = st.text_input("Product ID", help="Unique code for the product (e.g. P001)")
        name = st.text_input("Product Name", help="Name of the product (e.g. Hammer)")
        cat = st.text_input("Category", help="Product category (e.g. Tools)")
        price = st.number_input("Unit Price (₹)", min_value=0.0, step=1.0, format="%.2f", help="Selling price per unit in INR")
        supplier = st.text_input("Supplier", help="Supplier name")
        reorder = st.number_input("Reorder Level", min_value=0, step=1, help="Minimum stock before reorder")
        qty_init = st.number_input("Initial Quantity", min_value=0, step=1, help="Opening stock quantity")
        
        if st.form_submit_button("Save"):
            if not pid or not name or price <= 0:
                st.error("Product ID, Name, and Price are required.")
            else:
                db : Session = next(get_db())
                db.merge(Product(
                    product_id=pid,
                    name=name,
                    category=cat,
                    unit_price=price,
                    supplier=supplier,
                    reorder_level=reorder,
                    qty_initial=qty_init
                ))
                db.commit()
                st.success(f"Product {pid} saved.")

    st.markdown("### Product Catalog")
    db: Session = next(get_db())
    inv = inventory_state(db)
    st.dataframe(inv[['product_id', 'name', 'category', 'unit_price', 'qty_on_stock', 'reorder_level', 'low_stock']].rename(columns={
        "unit_price": "Unit Price (₹)",
        "qty_on_stock": "Stock Qty",
        "reorder_level": "Reorder Level",
        "low_stock": "Low Stock"
    }))

with tab2:
    st.subheader("Record Transactions")
    with st.form("transaction_form"):
        tid = st.text_input("Transaction ID", help="Unique transaction code (e.g. T001)")
        pid = st.text_input("Product ID", help="Enter Product ID from catalog")
        kind = st.selectbox("Transaction Type", ["purchase", "sale"], help="Select purchase or sale")
        qty = st.number_input("Quantity", min_value=1, step=1, help="Number of units")
        price = st.number_input("Unit Price (₹)", min_value=0.0, step=1.0, format="%.2f", help="Transaction price per unit in INR")
        note = st.text_area("Note", help="Any remarks for this transaction")
        
        if st.form_submit_button("Add"):
            if not tid or not pid or price <= 0:
                st.error("Transaction ID, Product ID, and Price are required.")
            else:
                db: Session = next(get_db())
                db.merge(Transaction(
                    tx_id=tid,
                    product_id=pid,
                    kind=kind,
                    qty=qty,
                    unit_price=price,
                    note=note
                ))
                db.commit()
                st.success(f"Transaction {tid} added.")

with tab3:
    st.subheader("Inventory Dashboard")
    db: Session = next(get_db())
    inv = inventory_state(db)
    tops = top_sellers(db, n=5)
    stats = sales_summary(db)
    purchases = purchase_summary(db)
    cat_perf = category_performance(db)

    st.metric("Total Sales (Qty)", f"{int(stats['total_sales'][0]):,}")
    st.metric("Total Revenue (₹)", f"₹ {stats['total_revenue'][0]:,.2f}")
    st.metric("Total Purchases (Qty)", f"{int(purchases['total_purchases'][0]):,}")
    st.metric("Total Expenditure (₹)", f"₹ {purchases['total_expenditure'][0]:,.2f}")

    st.markdown("#### Low Stock Products")
    low = inv[inv['low_stock']][["product_id", "name", "qty_on_stock"]]
    st.dataframe(low)

    st.markdown("#### Top Sellers")
    st.dataframe(tops)

    st.markdown("#### Category Performance")
    st.dataframe(cat_perf)

    if st.button("Summarize Today"):
        st.write(summarize_day(stats, tops, low))

with tab4:
    st.subheader("Ask the Assistant")
    q = st.text_area("Ask a question about inventory", help="Type your query (e.g. Which products are low in stock?)")
    if st.button("Ask") and q.strip():
        db: Session = next(get_db())
        inv = inventory_state(db)
        tops = top_sellers(db, n=5)
        st.write(answer_query(q, inv, tops))