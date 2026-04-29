import streamlit as st
import pandas as pd
import plotly.express as px

# 🎨 CONFIG

st.set_page_config(page_title="Finance Intelligence", layout="wide")

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Animations */
.fade-in {
    animation: fadeIn 0.8s ease-in-out;
}
@keyframes fadeIn {
    from {opacity:0;}
    to {opacity:1;}
}

.slide-up {
    animation: slideUp 0.6s ease;
}
@keyframes slideUp {
    from {transform: translateY(30px); opacity:0;}
    to {transform: translateY(0); opacity:1;}
}

/* Cards */
.card {
    background: rgba(255,255,255,0.06);
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
    margin-bottom: 10px;
}
.card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}

/* Divider */
.divider {
    height: 2px;
    background: linear-gradient(to right, #3b82f6, #06b6d4);
    margin: 20px 0;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# FILE UPLOAD

st.sidebar.header("📂 Upload Data")

file1 = st.sidebar.file_uploader("Dataset 1", type=["xlsx","csv"])
file2 = st.sidebar.file_uploader("Dataset 2 (optional)", type=["xlsx","csv"])

if file1 is None:
    st.warning("Upload a dataset to begin")
    st.stop()

def load(file):
    df = pd.read_excel(file) if file.name.endswith(".xlsx") else pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df1 = load(file1)
df2 = load(file2) if file2 else None


# METRICS

def calc(df):
    spent = df["Debit"].sum()
    income = df["Credit"].sum()
    bal = df["Balance"].iloc[-1]
    inv = df["Investment"].sum()
    ret = df["Returns"].sum()
    roi = (ret/inv*100) if inv>0 else 0
    loan = df["Outstanding_Loan"].iloc[-1]
    return spent, income, bal, roi, loan

spent, income, bal, roi, loan = calc(df1)


# TABS

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview","📈 Investments","🏦 Loans","🔄 Comparison","🤖 Insights"]
)


# OVERVIEW

with tab1:

    st.markdown("<div class='fade-in'><h2>💰 Overview</h2></div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)

    c1.markdown(f"<div class='card slide-up'>💸 Spent<br><h2>₹{spent:,.0f}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card slide-up'>💰 Income<br><h2>₹{income:,.0f}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card slide-up'>🏦 Balance<br><h2>₹{bal:,.0f}</h2></div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown("### 📈 Cash Flow")
    with st.spinner("Loading chart..."):
        daily = df1.groupby("Date")[["Debit","Credit"]].sum()
        st.plotly_chart(px.line(daily), use_container_width=True)

    st.markdown("### 🥧 Spending Distribution")
    exp = df1[df1["Debit"]>0]
    cat = exp.groupby("Category")["Debit"].sum()
    st.plotly_chart(px.pie(values=cat.values, names=cat.index), use_container_width=True)


# INVESTMENTS

with tab2:

    st.markdown("<div class='fade-in'><h2>📈 Investments</h2></div>", unsafe_allow_html=True)

    st.metric("ROI", f"{roi:.2f}%")

    with st.spinner("Analyzing investments..."):
        inv = df1.groupby("Date")[["Investment","Returns"]].sum()
        st.plotly_chart(px.line(inv), use_container_width=True)


# LOANS

with tab3:

    st.markdown("<div class='fade-in'><h2>🏦 Loans</h2></div>", unsafe_allow_html=True)

    with st.spinner("Loading loan data..."):
        loan_trend = df1.groupby("Date")["Outstanding_Loan"].max()
        st.plotly_chart(px.line(loan_trend), use_container_width=True)

    emi_ratio = df1["EMI_Paid"].sum()/income if income>0 else 0
    st.metric("EMI Ratio", f"{emi_ratio:.2f}")


# COMPARISON

with tab4:

    if df2 is not None:

        st.markdown("<div class='fade-in'><h2>📊 Comparison</h2></div>", unsafe_allow_html=True)

        spent2, income2, bal2, roi2, loan2 = calc(df2)

        metric_choice = st.multiselect(
            "Select Metrics",
            ["Spent","Income","ROI","Loan"],
            default=["Spent","Income"]
        )

        data_map = {
            "Spent": (spent, spent2),
            "Income": (income, income2),
            "ROI": (roi, roi2),
            "Loan": (loan, loan2)
        }

        comp = pd.DataFrame({
            m: data_map[m] for m in metric_choice
        }, index=["File1","File2"]).T

        st.dataframe(comp)

        st.plotly_chart(px.bar(comp, barmode="group"), use_container_width=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        st.subheader("📊 Correlation Analysis")

        corr_cols = ["Debit","Credit","Investment","Returns","Outstanding_Loan"]
        corr = df1[corr_cols].corr()

        st.plotly_chart(px.imshow(corr, text_auto=True), use_container_width=True)

    else:
        st.info("Upload second dataset to enable comparison")

# INSIGHTS

with tab5:

    st.markdown("<div class='fade-in'><h2>🤖 Insights</h2></div>", unsafe_allow_html=True)

    insights = []

    savings = (income-spent)/income if income>0 else 0

    if savings < 0:
        insights.append("⚠️ Overspending detected")

    if roi < 0:
        insights.append("📉 Investment losses")

    if loan > income:
        insights.append("🚨 High debt level")

    if not insights:
        insights.append("✅ Financial condition is stable")

    for i in insights:
        st.markdown(f"<div class='card fade-in'>{i}</div>", unsafe_allow_html=True)