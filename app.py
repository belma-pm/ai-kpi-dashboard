import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------
# Page Config
# -----------------------
st.set_page_config(
    page_title="AI KPI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 AI-Powered Executive KPI Dashboard")
st.markdown(
    """
    **Expected CSV Format**

    This dashboard works with a **structured CSV file** containing the following columns:

    • **Month** – Time period (e.g. Jan-2024, 2024-01)  
    • **Revenue** – Monthly total revenue (numeric)  
    • **Orders** – Monthly total order count (numeric, non-zero)

    _Notes:_  
    Data should be ordered chronologically and include at least **2 rows** for MoM comparison.
    """
)


# -----------------------
# Sidebar - CSV Upload
# -----------------------
st.sidebar.header("Upload & Filters")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

# -----------------------
# Placeholder / CSV Handling
# -----------------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    required_columns = {"Month", "Revenue", "Orders"}
    if not required_columns.issubset(df.columns):
        st.sidebar.error("CSV must contain Month, Revenue, and Orders columns.")
        st.stop()
else:
    st.sidebar.warning("Please upload a CSV file to proceed.")

    # Placeholder KPI’lar
    st.subheader("📌 Dashboard Placeholder")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Revenue", "$0", delta="0%")
    col2.metric("Current Orders", 0, delta="0%")
    col3.metric("Average Order Value", "$0.00", delta="0%")
    col4.metric("Risk Score", 0)

    # Placeholder Grafik
    dummy_months = ["Jan", "Feb", "Mar", "Apr", "May"]
    dummy_revenue = [0, 0, 0, 0, 0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dummy_months, y=dummy_revenue,
        mode='lines+markers', name="Revenue Placeholder",
        line=dict(dash='dash', color='gray')
    ))
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("Upload a CSV file to see real-time KPIs and forecasts here.")
    st.stop()

# -----------------------
# KPI Calculations
# -----------------------
current_revenue = df["Revenue"].iloc[-1]
previous_revenue = df["Revenue"].iloc[-2]
mom_change = ((current_revenue - previous_revenue) / previous_revenue) * 100

current_orders = df["Orders"].iloc[-1]
previous_orders = df["Orders"].iloc[-2]
order_change = ((current_orders - previous_orders) / previous_orders) * 100

current_aov = current_revenue / current_orders
previous_aov = previous_revenue / previous_orders
aov_change = ((current_aov - previous_aov) / previous_aov) * 100

# -----------------------
# Risk Engine
# -----------------------
if mom_change <= -10:
    risk_level = "🔴 High Risk"
    risk_message = "Significant revenue decline detected. Immediate investigation required."
elif -10 < mom_change < 0:
    risk_level = "🟡 Medium Risk"
    risk_message = "Moderate revenue decline. Monitor closely."
else:
    risk_level = "🟢 Healthy"
    risk_message = "Revenue performance is stable or growing."

# -----------------------
# Diagnosis Engine
# -----------------------
if mom_change < 0 and order_change < 0:
    diagnosis = "Revenue and order volume declined together. Possible demand contraction."
elif mom_change < 0 and order_change >= 0:
    diagnosis = "Revenue declined while order volume remained stable. Potential pricing issue."
else:
    diagnosis = "No major structural performance issue detected."

# -----------------------
# Risk Score
# -----------------------
risk_score = min(round(abs(mom_change)*2 + abs(order_change)*1.5 + abs(aov_change)*1.2), 100)

# -----------------------
# Revenue Forecast
# -----------------------
x = np.arange(len(df))
y = df["Revenue"].values
coefficients = np.polyfit(x, y, 1)
trend_line = np.poly1d(coefficients)
next_month_index = len(df)
forecast_revenue = round(trend_line(next_month_index), 0)

# -----------------------
# AI Commentary
# -----------------------
def ai_diagnosis_layer(revenue_change, order_change, risk_level):
    if risk_level.startswith("🔴"):
        return "Revenue contraction detected alongside order decline. Immediate intervention recommended."
    elif risk_level.startswith("🟡"):
        return "Early signs of revenue deceleration observed. Close monitoring advised."
    else:
        return "Revenue trajectory remains stable with positive order dynamics. No material performance anomaly detected."

ai_commentary = ai_diagnosis_layer(mom_change, order_change, risk_level)

# -----------------------
# KPI Display
# -----------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Revenue", f"${current_revenue}", delta=f"{mom_change:.2f}%")
col2.metric("Current Orders", current_orders, delta=f"{order_change:.2f}%")
col3.metric("Average Order Value", f"${current_aov:.2f}", delta=f"{aov_change:.2f}%")
col4.metric("Risk Score", risk_score)

# -----------------------
# Risk & Diagnosis Expanders
# -----------------------
with st.expander("Performance Risk Assessment"):
    if risk_level.startswith("🔴"):
        st.markdown(f"<h3 style='color:red'>{risk_level}</h3>", unsafe_allow_html=True)
    elif risk_level.startswith("🟡"):
        st.markdown(f"<h3 style='color:orange'>{risk_level}</h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h3 style='color:green'>{risk_level}</h3>", unsafe_allow_html=True)
    st.write(risk_message)

with st.expander("Performance Diagnosis"):
    st.write(diagnosis)

with st.expander("AI Executive Commentary"):
    st.write(ai_commentary)

# -----------------------
# Revenue Trend + Forecast Plotly
# -----------------------
st.subheader("Revenue Trend & Forecast")
forecast_months = df["Month"].tolist() + ["Forecast"]

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Month"], y=df["Revenue"], mode='lines+markers', name="Actual Revenue"))
fig.add_trace(go.Scatter(x=forecast_months, y=list(trend_line(np.arange(len(forecast_months)))), 
                         mode='lines+markers', name="Trend Forecast", line=dict(dash='dash', color='red')))

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue",
    template="plotly_white",
    legend=dict(y=0.99, x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Revenue Forecast")
st.write(f"Projected Next Month Revenue: ${forecast_revenue}")

# -----------------------
# AI Report Button
# -----------------------
st.subheader("Generate Executive Insight")
if st.button("Generate AI Report"):
    summary = f"""
    Current Revenue: {current_revenue}
    Revenue MoM Change: {mom_change:.2f}%
    Current Orders: {current_orders}
    Order MoM Change: {order_change:.2f}%
    Average Order Value: ${current_aov:.2f} (Δ {aov_change:.2f}%)
    Risk Score: {risk_score}
    Forecasted Revenue: ${forecast_revenue}
    Risk Level: {risk_level}
    Diagnosis: {diagnosis}
    """
    st.write("### Raw KPI Summary")
    st.write(summary)

st.success("AI Revenue Intelligence System is running successfully 🚀")
