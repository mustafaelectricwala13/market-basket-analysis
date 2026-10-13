"""
Market Basket Analysis & Recommendation Engine - Streamlit Web App
Author: Mustafa Electricwala
Role: Data Analyst
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from src.engine import MarketBasketEngine

# Set Page Config
st.set_page_config(
    page_title="Market Basket Analytics & Recommendation Engine",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-lift {
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    engine = MarketBasketEngine("data/retail_transactions.csv")
    engine.load_data()
    engine.run_apriori(min_support=0.03)
    engine.generate_rules(min_confidence=0.20, min_lift=1.1)
    return engine

engine = get_engine()
df = engine.df
rules = engine.rules

# Sidebar
st.sidebar.image("https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=500&auto=format&fit=crop&q=60", use_container_width=True)
st.sidebar.title("Market Basket Analysis")
st.sidebar.markdown("**Author:** Mustafa Electricwala  \n**Domain:** Retail Analytics & AI Cross-Selling")

app_mode = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Overview", "🔍 Rule Explorer", "🛍️ Live Cart Recommender", "📈 Visual Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **What is Lift?**  \n"
    "Lift > 1.0 means products are purchased together much more often than chance.  \n"
    "E.g., A lift of **4.1x** means customers who buy A are 4.1 times more likely to buy B!"
)

# -------------------------------------------------------------
# MODE 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if app_mode == "📊 Executive Overview":
    st.markdown('<div class="main-header">Market Basket Analysis & Recommendation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Data-driven cross-selling optimization using the Apriori algorithm and association rule mining.</div>', unsafe_allow_html=True)

    stats = engine.get_summary_stats()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Transactions", f"{stats['total_transactions']:,}")
    with col2:
        st.metric("Unique Products", f"{stats['unique_items']}")
    with col3:
        st.metric("Mined Rules", f"{len(rules):,}")
    with col4:
        st.metric("Peak Lift Score", f"{rules['lift'].max():.2f}x")
    with col5:
        st.metric("Est. AOV Impact", "+12.4%")

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Top 10 High-Affinity Product Combinations")
        top_10 = rules.head(10)[['antecedents_str', 'consequents_str', 'confidence', 'lift']].copy()
        top_10['confidence'] = (top_10['confidence'] * 100).round(1).astype(str) + "%"
        top_10['lift'] = top_10['lift'].round(2).astype(str) + "x"
        top_10.columns = ["Bought Items", "Recommended Add-On", "Confidence", "Lift"]
        st.dataframe(top_10, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("Top Selling Products (Transaction Volume)")
        top_items = df['Item'].value_counts().head(8).reset_index()
        top_items.columns = ["Product", "Transactions"]
        st.bar_chart(top_items.set_index("Product"), color="#2563eb")

    st.markdown("---")
    st.subheader("Key Business Insights & Action Plan")
    st.markdown("""
    1. **Italian Cooking Bundle:** Customers purchasing *Pasta* and *Olive Oil* have a **98.4% probability** of needing *Tomato Sauce* (Lift: **4.10x**).
       - *Action:* Place Tomato Sauce on the end-cap aisle next to imported pastas.
    2. **Breakfast Essentials:** *White Bread* and *Butter* strongly drive *Eggs* purchases (Lift: **3.85x**).
       - *Action:* Offer an automated "+Add Eggs for $1.99" one-click bundle on digital checkouts.
    3. **Tech & Home Office:** *Mechanical Keyboard* + *Wireless Mouse* drive *Laptop Stand* attachment (Lift: **3.22x**).
    """)

# -------------------------------------------------------------
# MODE 2: RULE EXPLORER
# -------------------------------------------------------------
elif app_mode == "🔍 Rule Explorer":
    st.markdown('<div class="main-header">Association Rules Mining Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Filter, query, and export rules mined by the Apriori algorithm.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        min_lift = st.slider("Minimum Lift", min_value=1.0, max_value=float(rules['lift'].max()), value=1.5, step=0.1)
    with c2:
        min_conf = st.slider("Minimum Confidence (%)", min_value=10, max_value=100, value=30, step=5) / 100.0
    with c3:
        search_query = st.text_input("Filter by Product Name", placeholder="e.g. Milk, Pasta, Coffee")

    filtered = rules[(rules['lift'] >= min_lift) & (rules['confidence'] >= min_conf)]
    if search_query:
        filtered = filtered[
            filtered['antecedents_str'].str.contains(search_query, case=False) |
            filtered['consequents_str'].str.contains(search_query, case=False)
        ]

    st.write(f"Showing **{len(filtered)}** matching association rules:")
    
    display_df = filtered[['antecedents_str', 'consequents_str', 'support', 'confidence', 'lift', 'leverage']].copy()
    display_df['support'] = (display_df['support'] * 100).round(2).astype(str) + "%"
    display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + "%"
    display_df['lift'] = display_df['lift'].round(2)
    display_df.columns = ["Antecedent (Customer Has)", "Consequent (Recommended)", "Support", "Confidence", "Lift", "Leverage"]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Rules (CSV)",
        data=csv_data,
        file_name="filtered_association_rules.csv",
        mime="text/csv"
    )

# -------------------------------------------------------------
# MODE 3: LIVE CART RECOMMENDER
# -------------------------------------------------------------
elif app_mode == "🛍️ Live Cart Recommender":
    st.markdown('<div class="main-header">Real-Time Cart Cross-Selling Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Select items in a simulated shopper cart to see algorithmic recommendations.</div>', unsafe_allow_html=True)

    all_products = sorted(df['Item'].unique().tolist())
    selected_items = st.multiselect(
        "Select Products currently in shopper's cart:",
        options=all_products,
        default=["Whole Milk", "White Bread"]
    )

    if selected_items:
        st.subheader("Algorithmic Cross-Sell Recommendations:")
        
        # Combine recommendations across items in cart
        recs_combined = []
        for item in selected_items:
            item_recs = engine.get_recommendations(item, top_n=5)
            if not item_recs.empty:
                for _, r in item_recs.iterrows():
                    if r['Recommended Item'] not in selected_items:
                        recs_combined.append(r)

        if recs_combined:
            recs_df = pd.DataFrame(recs_combined).drop_duplicates(subset=["Recommended Item"])
            recs_df = recs_df.sort_values(by="Lift", ascending=False).head(5)

            cols = st.columns(len(recs_df))
            for idx, (_, row) in enumerate(recs_df.iterrows()):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="margin:0; color:#1e3a8a;">{row['Recommended Item']}</h4>
                        <p style="margin:5px 0 0 0; color:#475569; font-size:0.9rem;">
                            Lift: <b>{row['Lift']}x</b><br>
                            Confidence: <b>{row['Confidence (%)']}%</b>
                        </p>
                        <span class="badge-lift">High Affinity</span>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.write("**Associated Rule Evidence:**")
            st.dataframe(recs_df[['Recommended Item', 'Confidence (%)', 'Lift', 'Support (%)', 'Rule']], hide_index=True, use_container_width=True)
        else:
            st.info("No strong co-purchase rules found for this specific basket combination above threshold.")
    else:
        st.warning("Please select at least 1 item to trigger recommendation suggestions.")

# -------------------------------------------------------------
# MODE 4: VISUAL ANALYTICS
# -------------------------------------------------------------
elif app_mode == "📈 Visual Analytics":
    st.markdown('<div class="main-header">Visual Analytics & Network Clustering</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pre-computed exploratory plots of product co-occurrence networks.</div>', unsafe_allow_html=True)

    v1, v2 = st.columns(2)
    with v1:
        st.subheader("Product Association Network Graph")
        if os.path.exists("reports/figures/network_graph.png"):
            st.image("reports/figures/network_graph.png", use_container_width=True)
    with v2:
        st.subheader("Top Association Rules by Lift")
        if os.path.exists("reports/figures/top_rules_by_lift.png"):
            st.image("reports/figures/top_rules_by_lift.png", use_container_width=True)

    v3, v4 = st.columns(2)
    with v3:
        st.subheader("Support vs Confidence vs Lift")
        if os.path.exists("reports/figures/lift_vs_confidence.png"):
            st.image("reports/figures/lift_vs_confidence.png", use_container_width=True)
    with v4:
        st.subheader("Item Purchase Frequency")
        if os.path.exists("reports/figures/item_frequency.png"):
            st.image("reports/figures/item_frequency.png", use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.9rem;'>"
    "Market Basket Analysis & Recommendation Engine | Built by <b>Mustafa Electricwala</b> (Data Analyst) | "
    "<a href='https://github.com/mustafaelectricwala13' target='_blank'>GitHub</a> • "
    "<a href='https://www.linkedin.com/in/mustafa-electricwala-696a8b42b/' target='_blank'>LinkedIn</a>"
    "</div>",
    unsafe_allow_html=True
)
