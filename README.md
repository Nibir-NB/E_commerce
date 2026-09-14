# E-commerce Customer Intelligence Platform

> A production-ready customer analytics and decision-support platform that transforms e-commerce transaction data into actionable customer insights, segmentation, KPIs, and business recommendations.

**Live Demo:** https://e-commerce-customer-segmentation-fzcm6wwnmow7wzvwe48wnl.streamlit.app/

**Dataset:** UCI Online Retail — 541,909 transactions across 38 countries  
**Customers Analyzed:** 4,338 unique customers

---

## 📌 Business Problem

E-commerce businesses generate large volumes of transaction data, but raw transaction records alone do not provide clear answers to important business questions:

- Which customers are the most valuable?
- Which customers are becoming inactive or at risk?
- Which customer segments contribute most to revenue?
- How frequently do different customer groups purchase?
- Which customers should be prioritized for engagement?
- How can business teams access customer insights without writing SQL?

This project addresses these questions by converting transactional data into **customer-level metrics, meaningful segments, KPIs, predictive scores, and actionable recommendations**.

The goal was to build the solution as a **usable business analytics application**, rather than limiting the analysis to a static notebook.

---

## 🎯 Business Objectives

The platform was designed to:

1. **Understand customer purchasing behavior** using transactional data.
2. **Measure customer value and engagement** through RFM analysis.
3. **Segment customers** into meaningful groups based on their behavior.
4. **Identify high-value and at-risk customers** for targeted business actions.
5. **Provide purchase-propensity scores** to help prioritize customer engagement.
6. **Track important business KPIs** through an interactive dashboard.
7. **Enable self-service analytics** for non-technical stakeholders.
8. **Automate data and model updates** so that insights remain current.

---

## 📊 What the Platform Provides

The application combines customer analytics, business intelligence, predictive scoring, and AI-powered data querying in one platform.

### 1. Customer & KPI Dashboard

Provides a high-level view of customer performance and behavior through:

- Total customer count
- Average customer spend
- Average recency
- Average order frequency
- Customer segment distribution
- RFM-based interactive visualizations
- Aggregated statistics for each customer segment

These KPIs provide stakeholders with a quick overview of **customer value, engagement, and purchasing behavior**.

---

### 2. Customer Segmentation

Customers are segmented using **Recency, Frequency, and Monetary (RFM)** metrics.

- **Recency:** Days since the customer's last purchase
- **Frequency:** Number of orders placed
- **Monetary:** Total customer spending

The RFM features are standardized and analyzed using **K-Means clustering**.

The resulting clusters are interpreted from a business perspective to identify groups such as:

- Loyal customers
- At-risk / inactive customers
- High-value customers

The segmentation helps translate customer behavior into **actionable marketing and retention strategies**.

---

### 3. Purchase-Propensity Analysis

A **Gradient Boosting Classifier** is used to generate purchase-propensity scores from customer behavioral characteristics.

The model uses a composite RFM-based score with:

- 40% Recency
- 35% Frequency
- 25% Monetary

The platform converts these results into an easy-to-understand **0–100% purchase-propensity score**.

Business users can enter customer RFM values and receive:

- Predicted customer segment
- Purchase-propensity score
- Segment-based recommendation

This provides a practical way to **prioritize customer engagement and identify customers requiring attention**.

---

### 4. Customer Lookup

The Customer Lookup feature provides customer-level visibility in real time.

Users can search for a customer by ID and view:

- Customer segment
- Total spending
- Order count
- Days since last purchase
- Customer RFM information

This enables business teams to move from **high-level KPI analysis to individual customer investigation**.

---

### 5. 🤖 AI Analyst

The AI Analyst provides a natural-language interface for querying the live customer database.

Instead of writing SQL, business users can ask questions such as:

> "Give me 5 at-risk customer IDs."

> "What strategy should we use for customer 12791?"

> "Which customer segment drives the most revenue?"

The chatbot queries the **live PostgreSQL database** and returns insights based on the actual customer data.

This creates a **self-service analytics layer** for non-technical stakeholders.

---

## 💡 Key Business Insights

The analysis identified three major customer groups:

| Customer Segment | Customers | Avg. Days Inactive | Avg. Orders | Avg. Spend |
|---|---:|---:|---:|---:|
| Loyal Customers | 3,245 (74.8%) | 41 days | 103 | $2,029 |
| At-risk / Churned | 1,080 (24.9%) | 247 days | 28 | $637 |
| High-value Customers | 13 (0.3%) | 5 days | 2,565 | $126,118 |

### Key observations

- **Loyal customers** form the largest customer group, indicating a strong base of recurring purchasers.
- **At-risk customers** show significantly higher inactivity and lower purchasing frequency, making them an important segment for re-engagement initiatives.
- **High-value customers** represent a very small portion of the customer base but have exceptionally high order frequency and spending.
- The high-value segment demonstrates a strong concentration of customer value, highlighting the importance of **customer prioritization and retention**.

These insights can support decisions around **customer targeting, retention campaigns, personalization, and account prioritization**.

---

## 📈 Business Analytics Workflow

```text
Raw Transaction Data
        │
        ▼
Data Cleaning & Loading
        │
        ▼
PostgreSQL Database
        │
        ▼
Customer-Level RFM Analysis
        │
        ├───────────────┐
        ▼               ▼
K-Means             RFM-Based
Segmentation        Propensity Scoring
        │               │
        └───────┬───────┘
                ▼
       Business Insights
                │
        ┌───────┴────────┐
        ▼                ▼
Interactive          AI Analyst
Dashboard            Chatbot
        │                │
        └───────┬────────┘
                ▼
       Data-Driven Decisions
