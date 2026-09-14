import os
import re
import cohere
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def get_db_url() -> str:
    """Safely retrieves DATABASE_URL from Streamlit secrets or OS environment."""
    url = None
    try:
        import streamlit as st

        if "DATABASE_URL" in st.secrets:
            url = st.secrets["DATABASE_URL"]
    except Exception:
        pass

    if not url:
        url = os.environ.get("DATABASE_URL")

    if not url:
        raise ValueError(
            "DATABASE_URL not found. Add it to your .env file or Streamlit secrets."
        )

    return url


def get_cohere_key() -> str:
    """Safely retrieves COHERE_API_KEY from Streamlit secrets or OS environment."""
    api_key = None
    try:
        import streamlit as st

        if "COHERE_API_KEY" in st.secrets:
            api_key = st.secrets["COHERE_API_KEY"]
    except Exception:
        pass

    if not api_key:
        api_key = os.environ.get("COHERE_API_KEY")

    if not api_key:
        raise ValueError(
            "COHERE_API_KEY not found. Add it to your .env file or Streamlit secrets."
        )

    return api_key


def clean_markdown(text: str) -> str:
    """Strips markdown asterisks and underscores from Cohere output."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    return text.strip()


def get_db_context(question: str) -> str:
    """Queries Supabase dynamically based on the user question and builds LLM context."""
    engine = create_engine(get_db_url(), pool_pre_ping=True)
    context_parts = []
    q = question.lower()

    with engine.connect() as conn:
        summary = pd.read_sql(
            """
            SELECT cluster_label as segment, COUNT(*) as customers,
                   ROUND(AVG(recency)::numeric,1) as avg_recency_days,
                   ROUND(AVG(frequency)::numeric,1) as avg_orders,
                   ROUND(AVG(monetary)::numeric,2) as avg_spend,
                   ROUND(SUM(monetary)::numeric,2) as total_revenue
            FROM customers GROUP BY cluster_label ORDER BY avg_spend DESC
        """,
            conn,
        )
        context_parts.append(
            f"SEGMENT SUMMARY:\n{summary.to_string(index=False)}"
        )

        stats = pd.read_sql(
            """
            SELECT COUNT(*) as total_customers,
                   ROUND(AVG(monetary)::numeric,2) as avg_spend,
                   ROUND(MAX(monetary)::numeric,2) as max_spend,
                   ROUND(AVG(recency)::numeric,1) as avg_recency_days
            FROM customers
        """,
            conn,
        )
        context_parts.append(
            f"\nOVERALL STATS:\n{stats.to_string(index=False)}"
        )

        if any(
            k in q
            for k in ["risk", "churn", "inactive", "lost", "win", "at-risk"]
        ):
            at_risk = pd.read_sql(
                """
                SELECT customer_id, ROUND(recency::numeric,0) as days_inactive,
                       frequency as orders, ROUND(monetary::numeric,2) as total_spent
                FROM customers WHERE cluster_label = 'At-risk / churned'
                ORDER BY recency DESC LIMIT 20
            """,
                conn,
            )
            context_parts.append(
                f"\nAT-RISK CUSTOMERS (top 20 most inactive):\n{at_risk.to_string(index=False)}"
            )

        if any(
            k in q
            for k in [
                "top",
                "best",
                "highest",
                "most",
                "biggest",
                "largest",
                "spend",
                "revenue",
                "whale",
            ]
        ):
            top = pd.read_sql(
                """
                SELECT customer_id, cluster_label as segment,
                       ROUND(monetary::numeric,2) as total_spent,
                       frequency as orders, recency as days_since_purchase
                FROM customers ORDER BY monetary DESC LIMIT 10
            """,
                conn,
            )
            context_parts.append(
                f"\nTOP 10 CUSTOMERS BY SPEND:\n{top.to_string(index=False)}"
            )

        if any(k in q for k in ["loyal", "retention", "retain", "reward"]):
            loyal = pd.read_sql(
                """
                SELECT customer_id, ROUND(monetary::numeric,2) as total_spent,
                       frequency as orders, recency as days_since_purchase
                FROM customers WHERE cluster_label = 'Loyal customers'
                ORDER BY monetary DESC LIMIT 10
            """,
                conn,
            )
            context_parts.append(
                f"\nTOP LOYAL CUSTOMERS:\n{loyal.to_string(index=False)}"
            )

        if any(
            k in q
            for k in ["customer id", "customer_id", "id ", "who is", "strategy"]
        ) or re.search(r"\d{4,}", question):
            numbers = re.findall(r"\d{4,}", question)
            if numbers:
                for num in numbers[:3]:
                    specific = pd.read_sql(
                        "SELECT customer_id, cluster_label as segment, "
                        "ROUND(monetary::numeric,2) as total_spent, "
                        "frequency as orders, recency as days_since_purchase "
                        "FROM customers WHERE customer_id = %(cid)s LIMIT 1",
                        conn,
                        params={"cid": num},
                    )
                    if len(specific) > 0:
                        context_parts.append(
                            f"\nCUSTOMER {num} DETAILS:\n{specific.to_string(index=False)}"
                        )

        if any(k in q for k in ["whale", "high-value", "high value"]):
            whales = pd.read_sql(
                """
                SELECT customer_id, ROUND(monetary::numeric,2) as total_spent,
                       frequency as orders, recency as days_since_purchase
                FROM customers WHERE cluster_label = 'High-value whales'
                ORDER BY monetary DESC
            """,
                conn,
            )
            context_parts.append(
                f"\nALL HIGH-VALUE WHALES:\n{whales.to_string(index=False)}"
            )

    return "\n\n".join(context_parts)


def ask_cohere(question: str, chat_history: list) -> str:
    """Generates analytical answers from Cohere using context gathered from Supabase."""
    client = cohere.ClientV2(api_key=get_cohere_key())
    db_context = get_db_context(question)

    system_prompt = f"""You are a data analyst assistant for an e-commerce customer segmentation dashboard.
You have FULL access to live customer data. Use exact numbers and customer IDs from the data when answering.

LIVE DATABASE DATA:
{db_context}

CUSTOMER SEGMENTS:
- Loyal customers: High frequency buyers, consistent spenders. Recommend: retention rewards.
- At-risk / churned: Long inactive, haven't bought recently. Recommend: win-back campaigns.
- High-value whales: Very rare but massive spenders. Recommend: personal VIP outreach.

STRICT FORMATTING RULES:
- Never use asterisks or markdown formatting
- Write in plain clean English only
- Use numbers and customer IDs directly from the data
- Keep answers concise 3 to 5 sentences max unless asked for a list
- When listing customer IDs format them as a simple numbered list
- Be direct like a senior business analyst speaking to a manager"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:
        messages.append(msg)
    messages.append({"role": "user", "content": question})

    response = client.chat(
        model="command-a-03-2025", messages=messages, max_tokens=600
    )

    raw_text = response.message.content[0].text
    return clean_markdown(raw_text)