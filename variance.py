import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Promotion Performance Dashboard", layout="wide")

# --- Load Data Function ---
@st.cache_data
def load_data():
    # Replace with your actual file path
    df = pd.read_excel("promotion AUG & SEP.Xlsx")
    df.columns = df.columns.str.strip()

    # Convert date columns
    df["Promo_Start Date"] = pd.to_datetime(df["Promo_Start Date"])
    df["Promo_End Date"] = pd.to_datetime(df["Promo_End Date"])

    # Month & Week breakdown
    df["Month"] = df["Promo_Start Date"].dt.to_period("M")
    df["Week"] = df["Promo_Start Date"].dt.isocalendar().week
    df["Year"] = df["Promo_Start Date"].dt.year

    return df

# --- Load ---
df = load_data()

# --- Filters ---
months = df["Month"].unique().tolist()
selected_month = st.selectbox("Select Month", months)

filtered_month_df = df[df["Month"] == selected_month]

weeks = filtered_month_df["Week"].unique().tolist()
selected_week = st.selectbox("Select Week", weeks)

week_df = filtered_month_df[filtered_month_df["Week"] == selected_week]

# --- Insights ---
st.subheader(f"📊 Promotion Sales Insights - {selected_month}, Week {selected_week}")

# Summary Table
summary = (
    week_df.groupby("Promotion Name")
    .agg({"Sales Qty": "sum", "Sales Value": "sum"})
    .reset_index()
    .sort_values(by="Sales Value", ascending=False)
)

st.dataframe(summary)

# --- Top & Bottom Promotions ---
if not summary.empty:
    top_promo = summary.iloc[0]
    bottom_promo = summary.iloc[-1]

    st.markdown(f"✅ **Best Promotion:** {top_promo['Promotion Name']} → Sales Value: {top_promo['Sales Value']:,}")
    st.markdown(f"⚠️ **Least Performing Promotion:** {bottom_promo['Promotion Name']} → Sales Value: {bottom_promo['Sales Value']:,}")

# --- Charts ---
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        summary,
        x="Promotion Name",
        y="Sales Value",
        title="Promotion Sales Value",
        text_auto=True
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(
        summary,
        names="Promotion Name",
        values="Sales Value",
        title="Sales Distribution by Promotion"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Promotion Periods ---
st.markdown("📅 **Promotion Periods (Selected Week):**")
st.table(week_df[["Promotion Name", "Promo_Start Date", "Promo_End Date", "Sales Value"]])
