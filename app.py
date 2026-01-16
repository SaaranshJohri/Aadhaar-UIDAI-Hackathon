import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="UIDAI Aadhaar Demographic Dashboard",
    layout="wide"
)

st.title("📊 Aadhaar Demographic Analysis Dashboard")
st.markdown("State-wise, District-wise & Predictive Analysis of Aadhaar Enrolment and Updates")

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("aadhar_demographic2.csv")
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])
    return df

df = load_data()

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("🔍 Filters")

state_list = sorted(df['state'].unique())
selected_state = st.sidebar.selectbox("Select State", state_list)

state_df = df[df['state'] == selected_state]

district_list = sorted(state_df['district'].unique())
selected_district = st.sidebar.selectbox("Select District", district_list)

district_df = state_df[state_df['district'] == selected_district]

# ---------------------------
# KPI Metrics (State Level)
# ---------------------------
st.subheader(f"📍 State Overview: {selected_state}")

total_5_17 = state_df['demo_age_5_17'].sum()
total_18_plus = state_df['demo_age_17_'].sum()
total_all = total_5_17 + total_18_plus

col1, col2, col3 = st.columns(3)
col1.metric("👶 Age 5–17", f"{total_5_17:,}")
col2.metric("🧑 Age 18+", f"{total_18_plus:,}")
col3.metric("📌 Total Aadhaar Activity", f"{total_all:,}")

# ---------------------------
# State-wise Age Group Chart
# ---------------------------
age_df = pd.DataFrame({
    "Age Group": ["5–17", "18+"],
    "Count": [total_5_17, total_18_plus]
})

fig_age = px.bar(
    age_df,
    x="Age Group",
    y="Count",
    text="Count",
    title="Age Group Distribution (State Level)",
    color="Age Group"
)
st.plotly_chart(fig_age, use_container_width=True)

# ---------------------------
# District-wise Breakdown (State)
# ---------------------------
st.subheader("🏙️ District-wise Aadhaar Activity")

district_group = (
    state_df
    .groupby("district")[["demo_age_5_17", "demo_age_17_"]]
    .sum()
    .reset_index()
)

district_group["Total"] = (
    district_group["demo_age_5_17"] +
    district_group["demo_age_17_"]
)

fig_district = px.bar(
    district_group.sort_values("Total", ascending=False),
    x="district",
    y="Total",
    title="Total Aadhaar Activity by District"
)
fig_district.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_district, use_container_width=True)

# ---------------------------
# District Deep Dive
# ---------------------------
st.subheader(f"🔎 District Deep Dive: {selected_district}")

d_5_17 = district_df['demo_age_5_17'].sum()
d_18_plus = district_df['demo_age_17_'].sum()

col1, col2 = st.columns(2)
col1.metric("👶 Age 5–17", f"{d_5_17:,}")
col2.metric("🧑 Age 18+", f"{d_18_plus:,}")

district_age_df = pd.DataFrame({
    "Age Group": ["5–17", "18+"],
    "Count": [d_5_17, d_18_plus]
})

fig_district_age = px.pie(
    district_age_df,
    names="Age Group",
    values="Count",
    title="District Age Group Distribution"
)

st.plotly_chart(fig_district_age, use_container_width=True)

# ---------------------------
# Time Series Trend (District)
# ---------------------------
st.subheader("📈 Temporal Aadhaar Activity Trend")

time_df = (
    district_df
    .groupby("date")[["demo_age_5_17", "demo_age_17_"]]
    .sum()
    .reset_index()
)

fig_time = px.line(
    time_df,
    x="date",
    y=["demo_age_5_17", "demo_age_17_"],
    title="Aadhaar Activity Over Time",
    labels={"value": "Count", "variable": "Age Group"}
)

st.plotly_chart(fig_time, use_container_width=True)

# =====================================================
# 🔮 PREDICTIVE ANALYTICS SECTION (NEW PART)
# =====================================================
st.subheader("🔮 Aadhaar Demand Forecast (Predictive Analytics)")

forecast_level = st.radio(
    "Select Forecast Level",
    ["State", "District"],
    horizontal=True
)

forecast_days = st.slider(
    "Forecast Horizon (Days)",
    min_value=3,
    max_value=30,
    value=7
)

# Prepare time-series
if forecast_level == "State":
    ts_df = (
        state_df
        .groupby("date")[["demo_age_5_17", "demo_age_17_"]]
        .sum()
        .reset_index()
    )
    title_suffix = selected_state
else:
    ts_df = (
        district_df
        .groupby("date")[["demo_age_5_17", "demo_age_17_"]]
        .sum()
        .reset_index()
    )
    title_suffix = selected_district

ts_df["total"] = ts_df["demo_age_5_17"] + ts_df["demo_age_17_"]
ts_df = ts_df.sort_values("date")

# Moving Average Forecast
window = 7
rolling_avg = ts_df["total"].rolling(window=window).mean().iloc[-1]

future_dates = pd.date_range(
    start=ts_df["date"].max() + pd.Timedelta(days=1),
    periods=forecast_days
)

forecast_df = pd.DataFrame({
    "date": future_dates,
    "Predicted Aadhaar Activity": [rolling_avg] * forecast_days
})

# Plot Actual vs Forecast
fig_forecast = px.line(
    ts_df,
    x="date",
    y="total",
    title=f"Actual vs Predicted Aadhaar Demand ({title_suffix})",
    labels={"total": "Aadhaar Activity"}
)

fig_forecast.add_scatter(
    x=forecast_df["date"],
    y=forecast_df["Predicted Aadhaar Activity"],
    mode="lines+markers",
    name="Predicted",
    line=dict(dash="dash")
)

st.plotly_chart(fig_forecast, use_container_width=True)

st.info(
    f"📌 Based on recent trends, the expected Aadhaar activity for the next "
    f"{forecast_days} days is approximately **{int(rolling_avg):,} per day**. "
    "This enables proactive manpower and infrastructure planning."
)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("🚀 **UIDAI Hackathon Dashboard | Descriptive + Predictive Governance Insights**")
