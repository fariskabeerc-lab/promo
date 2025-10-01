import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Promotion Performance Dashboard", layout="wide")

# --- Load Data Function ---
@st.cache_data
def load_data():
    df = pd.read_excel("promotion AUG & SEP.Xlsx")
    df.columns = df.columns.str.strip()

    # Convert date columns
    df["Promo_Start Date"] = pd.to_datetime(df["Promo_Start Date"])
    df["Promo_End Date"] = pd.to_datetime(df["Promo_End Date"])

    # Month & Week breakdown
    df["Month_Num"] = df["Promo_Start Date"].dt.month
    df["Month_Name"] = df["Promo_Start Date"].dt.month_name()
    df["Year"] = df["Promo_Start Date"].dt.year
    df["Week_of_Month"] = df["Promo_Start Date"].apply(lambda d: (d.day - 1) // 7 + 1)

    return df

# --- Load ---
df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filters")

years = sorted(df["Year"].unique())
years.insert(0, "All")
selected_year = st.sidebar.selectbox("Select Year", years)

if selected_year != "All":
    df_year_filtered = df[df["Year"] == selected_year]
else:
    df_year_filtered = df.copy()

months = df_year_filtered["Month_Name"].unique().tolist()
months.sort(key=lambda x: pd.to_datetime(x, format='%B').month)
months.insert(0, "All")
selected_month = st.sidebar.selectbox("Select Month", months)

if selected_month != "All":
    df_month_filtered = df_year_filtered[df_year_filtered["Month_Name"] == selected_month]
else:
    df_month_filtered = df_year_filtered.copy()

weeks = sorted(df_month_filtered["Week_of_Month"].unique())
week_labels = {1: "First Week", 2: "Second Week", 3: "Third Week", 4: "Fourth Week", 5: "Fifth Week"}
week_options = [week_labels[w] for w in weeks]
week_options.insert(0, "All")
selected_week_label = st.sidebar.selectbox("Select Week", week_options)

if selected_week_label != "All":
    selected_week = [k for k, v in week_labels.items() if v == selected_week_label][0]
    week_df = df_month_filtered[df_month_filtered["Week_of_Month"] == selected_week]
else:
    week_df = df_month_filtered.copy()

# --- Insights ---
st.subheader(f"📊 SAFA oud mehta Promotion Sales Insights")

# Summary Table with Tran No, Start & End Dates
summary = (
    week_df.groupby(["Tran No", "Promotion Name", "Promo_Start Date", "Promo_End Date"])
    .agg({"Sales Qty": "sum", "Sales Value": "sum"})
    .reset_index()
    .sort_values(by="Sales Value", ascending=False)
)

st.dataframe(summary)

# --- Top & Bottom Promotions ---
if not summary.empty:
    top_promo = summary.iloc[0]
    bottom_promo = summary.iloc[-1]

    st.success(f"✅ Best Promotion: **{top_promo['Promotion Name']}** → Sales Value: {top_promo['Sales Value']:,}")
    st.error(f"⚠️ Least Performing Promotion: **{bottom_promo['Promotion Name']}** → Sales Value: {bottom_promo['Sales Value']:,}")

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

# --- Promotion Periods Table ---
st.markdown("📅 **Promotion Details (Selected Filter):**")
st.table(week_df[["Tran No", "Promotion Name", "Promo_Start Date", "Promo_End Date", "Sales Qty", "Sales Value"]])
