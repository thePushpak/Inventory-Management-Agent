from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

def summarize_day(stats, top_df, low_df):
    prompt = f"""
    Given the following daily inventory statistics, top selling products, and low stock products, provide a concise summary of the day's performance.

    Daily Statistics:
    {stats.to_dict(orient='records')[0]}

    Top Selling Products:
    {top_df.to_dict(orient='records')}

    Low Stock Products:
    {low_df.to_dict(orient='records')}

    Summarize the key insights and any notable trends or issues.
    Use Indian Rupee symbol (₹) for currency. Use Hindi terms where appropriate.
    Keep it under 120 words and professional.
    """
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return resp.text

    
def answer_query(question:str, inv_df, top_df):
    context = f"""Top sellers: {top_df.to_dict(orient='records')}
    Stock:
    {inv_df[['product_id', 'qty_on_stock', 'reorder_level']].to_dict(orient='records')}
    """
    prompt = f"""Context: {context}
    Answer briefly: {question}
    """
    
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return resp.text