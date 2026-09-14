import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from db import load_customers
from clustering import predict_cluster, CLUSTER_LABELS
from purchase_predictor import predict_purchase_probability
from chatbot import ask_cohere

st.set_page_config(page_title="E-commerce Intelligence", page_icon="🛒", layout="wide")

SEGMENT_COLORS = {"Loyal customers": "#2ECC71", "At-risk / churned": "#E74C3C", "High-value whales": "#3498DB"}
SEGMENT_ACTIONS = {0: "🎁 Send loyalty reward.", 1: "📧 Trigger win-back campaign.", 2: "💎 Assign personal outreach."}

@st.cache_data(ttl=3600)
def get_data():
    return load_customers()

df = get_data()

with st.sidebar:
    st.title("🛒 E-commerce Intelligence")
    st.caption("Production-grade customer segmentation")
    st.markdown("---")
    selected_segments = st.multiselect("Filter segments", options=list(CLUSTER_LABELS.values()), default=list(CLUSTER_LABELS.values()))
    st.markdown("---")
    st.caption(f"🟢 {len(df):,} customers loaded")

filtered_df = df[df["cluster_label"].isin(selected_segments)]

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔮 Predict segment", "🔍 Customer lookup", "🤖 AI Analyst"])

with tab1:
    st.header("Customer segmentation dashboard")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total customers", f"{len(df):,}")
    k2.metric("Avg spend", f"${df['monetary'].mean():,.0f}")
    k3.metric("Avg recency", f"{df['recency'].mean():.0f} days")
    k4.metric("Avg order frequency", f"{df['frequency'].mean():.1f}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Segment distribution")
        counts = filtered_df["cluster_label"].value_counts().reset_index()
        counts.columns = ["Segment", "Count"]
        fig = px.pie(counts, names="Segment", values="Count", color="Segment", color_discrete_map=SEGMENT_COLORS, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Cluster summary")
        summary = filtered_df.groupby("cluster_label").agg(Customers=("customer_id", "count"), Avg_Recency=("recency", "mean"), Avg_Frequency=("frequency", "mean"), Avg_Spend=("monetary", "mean")).round(1).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader("RFM scatter")
    c1, c2 = st.columns(2)
    x_axis = c1.selectbox("X axis", ["recency", "frequency", "monetary"])
    y_axis = c2.selectbox("Y axis", ["monetary", "frequency", "recency"])
    fig2 = px.scatter(filtered_df, x=x_axis, y=y_axis, color="cluster_label", color_discrete_map=SEGMENT_COLORS, size="monetary", size_max=20, hover_data=["customer_id", "recency", "frequency", "monetary"], opacity=0.7)
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Predict segment for a new customer")
    c1, c2, c3 = st.columns(3)
    recency = c1.number_input("Days since last purchase", min_value=0, value=30)
    frequency = c2.number_input("Number of orders placed", min_value=1, value=5)
    monetary = c3.number_input("Total amount spent ($)", min_value=0.0, value=500.0)
    if st.button("Run prediction", type="primary"):
        cluster_id, cluster_label = predict_cluster(recency, frequency, monetary)
        prob = predict_purchase_probability(recency, frequency, monetary, cluster_id)
        r1, r2, r3 = st.columns(3)
        r1.metric("Predicted segment", cluster_label)
        r2.metric("Purchase probability", f"{prob}%")
        r3.metric("Cluster ID", cluster_id)
        st.info(SEGMENT_ACTIONS.get(cluster_id, ""))

with tab3:
    st.header("Customer lookup")
    cid = st.text_input("Enter customer ID")
    if cid:
        row = df[df["customer_id"].str.contains(cid.strip(), case=False)]
        if len(row) > 0:
            r = row.iloc[0]
            st.success(f"Customer found — **{r['cluster_label']}**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Customer ID", r["customer_id"])
            c2.metric("Recency", f"{r['recency']:.0f} days")
            c3.metric("Orders", f"{r['frequency']:.0f}")
            c4.metric("Total spent", f"${r['monetary']:,.0f}")
        else:
            st.error("No customer found with that ID.")

            # ── TAB 4 — AI Analyst Chatbot ────────────────────────────────────────────────
with tab4:
    st.header("AI Data Analyst")
    st.caption("Ask anything about your customer data — powered by Claude AI with live database access")

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "display_history" not in st.session_state:
        st.session_state.display_history = []

    # Suggested questions
    st.markdown("**Try asking:**")
    col1, col2, col3 = st.columns(3)
    suggestions = [
        "Which segment has the highest average spend?",
        "How many at-risk customers do we have?",
        "Who are my top 5 customers by spend?",
        "What's the total revenue from loyal customers?",
        "How should I target high-value whales?",
        "What win-back strategy do you recommend?"
    ]
    if col1.button(suggestions[0], use_container_width=True):
        st.session_state.pending_question = suggestions[0]
    if col2.button(suggestions[1], use_container_width=True):
        st.session_state.pending_question = suggestions[1]
    if col3.button(suggestions[2], use_container_width=True):
        st.session_state.pending_question = suggestions[2]
    if col1.button(suggestions[3], use_container_width=True):
        st.session_state.pending_question = suggestions[3]
    if col2.button(suggestions[4], use_container_width=True):
        st.session_state.pending_question = suggestions[4]
    if col3.button(suggestions[5], use_container_width=True):
        st.session_state.pending_question = suggestions[5]

    st.markdown("---")

    # Display chat history
    for msg in st.session_state.display_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask about your customers...")
    
    # Handle suggestion button clicks
    if "pending_question" in st.session_state and st.session_state.pending_question:
        user_input = st.session_state.pending_question
        st.session_state.pending_question = None

    if user_input:
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.display_history.append({"role": "user", "content": user_input})

        # Get Claude response
        with st.chat_message("assistant"):
            with st.spinner("Querying database and thinking..."):
                try:
                    response = ask_cohere(user_input, st.session_state.chat_history)
                    st.write(response)
                    # Update histories
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.session_state.display_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Clear chat button
    if st.session_state.display_history:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.session_state.display_history = []
            st.rerun()
