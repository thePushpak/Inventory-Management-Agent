import pandas as pd
from sqlalchemy.orm import Session
from models import Product, Transaction

def load_frames(db: Session) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load products and transactions as DataFrames."""
    prods = pd.read_sql(db.query(Product).statement, db.bind)
    tx = pd.read_sql(db.query(Transaction).statement, db.bind)
    return prods, tx

def inventory_state(db: Session) -> pd.DataFrame:
    """Return inventory state including stock and low stock flag."""
    prods, tx = load_frames(db)
    if tx.empty:
        tx = pd.DataFrame(columns=['product_id', 'kind', 'qty'])
    purchases = tx[tx['kind'] == 'purchase'].groupby('product_id')['qty'].sum().rename('in_qty')
    sales = tx[tx['kind'] == 'sale'].groupby('product_id')['qty'].sum().rename('out_qty')
    inv = prods.join(purchases, on='product_id', how='left').join(sales, on='product_id', how='left')
    inv = inv.copy()
    inv["in_qty"] = inv["in_qty"].fillna(0).astype(int)
    inv["out_qty"] = inv["out_qty"].fillna(0).astype(int)
    inv["qty_on_stock"] = inv["qty_initial"] + inv["in_qty"] - inv["out_qty"]
    inv["low_stock"] = inv["qty_on_stock"] <= inv["reorder_level"]
    return inv

def top_sellers(db: Session, n: int = 5) -> pd.DataFrame:
    """Return top n selling products."""
    _, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['product_id', 'qty_sold'])
    tops = (tx[tx['kind'] == 'sale'].groupby('product_id')['qty'].sum()
            .nlargest(n).reset_index(name="qty_sold"))
    return tops

def sales_summary(db: Session) -> pd.DataFrame:
    """Return total sales and revenue."""
    _, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['total_sales', 'total_revenue'])
    sales = tx[tx['kind'] == 'sale']
    total_sales = sales['qty'].sum()
    total_revenue = (sales['qty'] * sales['unit_price']).sum()
    summary = pd.DataFrame({'total_sales': [total_sales], 'total_revenue': [total_revenue]})
    return summary

def purchase_summary(db: Session) -> pd.DataFrame:
    """Return total purchases and expenditure."""
    _, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['total_purchases', 'total_expenditure'])
    purchases = tx[tx['kind'] == 'purchase']
    total_purchases = purchases['qty'].sum()
    total_expenditure = (purchases['qty'] * purchases['unit_price']).sum()
    summary = pd.DataFrame({'total_purchases': [total_purchases], 'total_expenditure': [total_expenditure]})
    return summary

def category_performance(db: Session) -> pd.DataFrame:
    """Return sales and revenue grouped by category."""
    prods, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['category', 'total_sales', 'total_revenue'])
    sales = tx[tx['kind'] == 'sale']
    sales = sales.merge(prods[['product_id', 'category']], on='product_id', how='left')
    category_perf = (sales.groupby('category')
                     .agg(total_sales=('qty', 'sum'),
                          total_revenue=('unit_price', lambda x: (sales.loc[x.index, 'qty'] * x).sum()))
                     .reset_index())
    return category_perf

def monthly_sales_trend(db: Session) -> pd.DataFrame:
    """Return monthly sales and revenue trend."""
    _, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['month', 'total_sales', 'total_revenue'])
    sales = tx[tx['kind'] == 'sale'].copy()
    sales['month'] = pd.to_datetime(sales['ts']).dt.to_period('M')
    monthly_trend = (sales.groupby('month')
                     .agg(total_sales=('qty', 'sum'),
                          total_revenue=('unit_price', lambda x: (sales.loc[x.index, 'qty'] * x).sum()))
                     .reset_index())
    monthly_trend['month'] = monthly_trend['month'].dt.to_timestamp()
    return monthly_trend

def monthly_purchase_trend(db: Session) -> pd.DataFrame:
    """Return monthly purchase and expenditure trend."""
    _, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['month', 'total_purchases', 'total_expenditure'])
    purchases = tx[tx['kind'] == 'purchase'].copy()
    purchases['month'] = pd.to_datetime(purchases['ts']).dt.to_period('M')
    monthly_trend = (purchases.groupby('month')
                     .agg(total_purchases=('qty', 'sum'),
                          total_expenditure=('unit_price', lambda x: (purchases.loc[x.index, 'qty'] * x).sum()))
                     .reset_index())
    monthly_trend['month'] = monthly_trend['month'].dt.to_timestamp()
    return monthly_trend

def supplier_performance(db: Session) -> pd.DataFrame:
    """Return total purchases grouped by supplier."""
    prods, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['supplier', 'total_purchased'])
    purchases = tx[tx['kind'] == 'purchase']
    purchases = purchases.merge(prods[['product_id', 'supplier']], on='product_id', how='left')
    supplier_perf = (purchases.groupby('supplier')
                     .agg(total_purchased=('qty', 'sum'))
                     .reset_index())
    return supplier_perf

def profit_margin(db: Session) -> pd.DataFrame:
    """Estimate profit margin per product (if purchase and sale prices available)."""
    prods, tx = load_frames(db)
    if tx.empty:
        return pd.DataFrame(columns=['product_id', 'profit_margin'])
    sales = tx[tx['kind'] == 'sale']
    purchases = tx[tx['kind'] == 'purchase']
    avg_sale_price = sales.groupby('product_id')['unit_price'].mean()
    avg_purchase_price = purchases.groupby('product_id')['unit_price'].mean()
    margin = (avg_sale_price - avg_purchase_price).rename('profit_margin')
    result = prods[['product_id', 'name']].join(margin, on='product_id', how='left')
    return result