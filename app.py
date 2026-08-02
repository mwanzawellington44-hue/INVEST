import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Import calculations from calculations.py
from calculations import (
    graham_value,
    liquidity_ratio,
    margin_of_safety,
    net_current_assets,
    peg_ratio,
    profit_ratio,
    return_on_equity,
    solvency_ratio,
)

# ---------------------------------------------------------
# 1. PAGE & STATE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Invast Financial AI Dashboard", layout="wide", page_icon="📊"
)

# Default values if no PDF has been scanned yet
DEFAULT_DATA = {
    "company_name": "NANACO",
    "current_price": 100.0,
    "pe_ratio": 15.0,
    "eps": 6.5,
    "bvps": 25.0,
    "growth_rate": 12.0,
    "sales": 500000.0,
    "current_assets": 2000.0,
    "current_liabilities": 900.0,
    "long_term_debt": 800.0,
    "total_debt": 1000.0,
    "shareholders_equity": 1500.0,
    "net_income": 250.0,
    "dividend_years": 12,
}

if "fin_data" not in st.session_state:
    st.session_state.fin_data = DEFAULT_DATA


# ---------------------------------------------------------
# 2. PYDANTIC SCHEMA FOR STRUCTURED AI EXTRACTION
# ---------------------------------------------------------
class FinancialMetricsSchema(BaseModel):
    company_name: str = Field(description="Name of the target company")
    current_price: float = Field(
        description="Current stock price per share (if mentioned, otherwise 100.0)"
    )
    pe_ratio: float = Field(description="Price to Earnings (P/E) ratio")
    eps: float = Field(description="Earnings per Share (EPS)")
    bvps: float = Field(description="Book Value per Share (BVPS)")
    growth_rate: float = Field(
        description="Earnings growth rate percentage e.g. 12.0 for 12%"
    )
    sales: float = Field(description="Total annual net sales or revenue")
    current_assets: float = Field(description="Total current assets")
    current_liabilities: float = Field(description="Total current liabilities")
    long_term_debt: float = Field(description="Total long term debt")
    total_debt: float = Field(
        description="Total debt (short term + long term debt)"
    )
    shareholders_equity: float = Field(description="Total shareholders equity")
    net_income: float = Field(description="Net income or profit after tax")
    dividend_years: int = Field(
        description=(
            "Number of consecutive years with uninterrupted dividend payments"
        )
    )


# ---------------------------------------------------------
# 3. SIDEBAR: PDF UPLOADER & AI SCANNER
# ---------------------------------------------------------
st.sidebar.title("🤖 AI PDF Extraction")

# Safely fetch API key without crashing app on startup if missing
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

uploaded_pdf = st.sidebar.file_uploader(
    "Upload Financial Report (PDF)", type=["pdf"]
)

if uploaded_pdf and st.sidebar.button("⚡ Scan & Parse Report"):
    if not api_key:
        st.sidebar.error(
            "Gemini API Key missing! Please configure secrets.toml or Streamlit Secrets."
        )
    else:
        with st.spinner("AI scanning PDF and extracting financial numbers..."):
            try:
                # Initialize Google GenAI Client safely
                client = genai.Client(api_key=api_key)

                # Read uploaded PDF bytes
                pdf_bytes = uploaded_pdf.read()
                pdf_part = types.Part.from_bytes(
                    data=pdf_bytes, mime_type="application/pdf"
                )

                extraction_prompt = """
                Analyze this financial report carefully. Extract the company's financial values 
                and map them into the requested schema fields. Ensure values represent full numeric amounts.
                """

                # FIXED: Updated model string to "gemini-1.5-flash"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[pdf_part, extraction_prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=FinancialMetricsSchema,
                    ),
                )

                # Parse extracted JSON directly into Python Dictionary
                extracted_dict = json.loads(response.text)
                st.session_state.fin_data = extracted_dict
                st.sidebar.success("Successfully extracted financial data!")

            except Exception as e:
                st.sidebar.error(f"Error parsing PDF: {str(e)}")

st.sidebar.divider()

# ---------------------------------------------------------
# 4. EDITABLE FINANCIAL VALUES (VERIFICATION STEP)
# ---------------------------------------------------------
with st.sidebar.expander("📝 Review / Override Values", expanded=False):
    fd = st.session_state.fin_data
    company_name = st.text_input(
        "Company Name", value=fd.get("company_name", "NANACO")
    )
    current_price = st.number_input(
        "Current Share Price ($)", value=float(fd.get("current_price", 100.0))
    )
    pe_ratio = st.number_input(
        "P/E Ratio", value=float(fd.get("pe_ratio", 15.0))
    )
    eps = st.number_input("EPS ($)", value=float(fd.get("eps", 6.5)))
    bvps = st.number_input("BVPS ($)", value=float(fd.get("bvps", 25.0)))
    growth = st.number_input(
        "Growth Rate (%)", value=float(fd.get("growth_rate", 12.0))
    )
    sales = st.number_input(
        "Annual Sales ($)", value=float(fd.get("sales", 500000.0))
    )
    current_assets = st.number_input(
        "Current Assets ($)", value=float(fd.get("current_assets", 2000.0))
    )
    current_liabilities = st.number_input(
        "Current Liabilities ($)",
        value=float(fd.get("current_liabilities", 900.0)),
    )
    long_term_debt = st.number_input(
        "Long-Term Debt ($)", value=float(fd.get("long_term_debt", 800.0))
    )
    total_debt = st.number_input(
        "Total Debt ($)", value=float(fd.get("total_debt", 1000.0))
    )
    shareholders_equity = st.number_input(
        "Shareholders' Equity ($)",
        value=float(fd.get("shareholders_equity", 1500.0)),
    )
    net_income = st.number_input(
        "Net Income ($)", value=float(fd.get("net_income", 250.0))
    )
    div_years = st.number_input(
        "Dividend Payment Years", value=int(fd.get("dividend_years", 12))
    )

# ---------------------------------------------------------
# 5. METRIC CALCULATIONS
# ---------------------------------------------------------
gm_val = graham_value(eps, bvps)
ms_val = margin_of_safety(gm_val, current_price) if gm_val else None
peg_val = peg_ratio(pe_ratio, growth)
roe_val = return_on_equity(net_income, shareholders_equity)
net_curr_assets = net_current_assets(current_assets, current_liabilities)
liq_val = liquidity_ratio(current_assets, current_liabilities)
solv_val = solvency_ratio(total_debt, shareholders_equity)
prof_val = profit_ratio(net_income, sales)

# ---------------------------------------------------------
# 6. DASHBOARD DISPLAY
# ---------------------------------------------------------
top_col1, top_col2, top_col3 = st.columns([2, 1, 1])

with top_col1:
    st.title(f"📊 {company_name}")
    st.caption("Automated Investment Valuation & Strategy Dashboard")

with top_col2:
    st.metric(label="Market Price", value=f"${current_price:,.2f}")

with top_col3:
    gm_str = f"${gm_val:,.2f}" if gm_val else "N/A"
    st.metric(label="Graham Intrinsic Value (GM)", value=gm_str)

st.divider()

# Strategy Scorecard
st.subheader("🎯 Strategy Scorecard")
sc1, sc2, sc3, sc4 = st.columns(4)

with sc1:
    is_liq_ok = current_assets >= (2 * current_liabilities)
    st.metric("Liquidity Rule (2x)", "PASS ✅" if is_liq_ok else "FAIL ❌")

with sc2:
    is_debt_ok = long_term_debt <= net_curr_assets
    st.metric("Debt vs Net Assets", "PASS ✅" if is_debt_ok else "FAIL ❌")

with sc3:
    is_div_ok = div_years >= 10
    st.metric(
        "Dividend History",
        f"{div_years} Yrs",
        delta="Pass" if is_div_ok else "Low",
    )

with sc4:
    if ms_val and 0.30 <= ms_val <= 0.50:
        buy_status = "BUY ZONE 🎯"
    elif ms_val and ms_val > 0.50:
        buy_status = "DEEP VALUE 💎"
    else:
        buy_status = "OVERVALUED ⚠️"
    ms_disp = f"{ms_val*100:.1f}%" if ms_val else "N/A"
    st.metric("Margin of Safety", ms_disp, delta=buy_status)

st.divider()

# Charts & Ratio Section
left_col, right_col = st.columns([1.1, 1])

with left_col:
    st.subheader("📈 5-Year Debt-to-Equity Trajectory")
    years = ["2022", "2023", "2024", "2025", "2026"]
    de_history = [0.95, 0.82, 0.75, 0.68, solv_val if solv_val else 0.60]

    df_de = pd.DataFrame({"Year": years, "D/E Ratio": de_history})
    fig_de = px.bar(
        df_de,
        x="Year",
        y="D/E Ratio",
        text_auto=".2f",
        color="D/E Ratio",
        color_continuous_scale="Blues_r",
    )
    fig_de.update_layout(height=230, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_de, use_container_width=True)

    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.metric(
            "PEG Ratio", f"{peg_val:.2f}" if peg_val else "N/A", delta="Valuation"
        )
    with v_col2:
        st.metric(
            "Return on Equity (ROE)",
            f"{roe_val:.1f}%" if roe_val else "N/A",
            delta="Efficiency",
        )

with right_col:
    with st.container(border=True):
        st.subheader("📊 Financial Benchmarks")

        # Current Ratio Chart
        st.markdown("**Current Ratio** (Target: ≥ 2.0)")
        df_liq = pd.DataFrame(
            {"Metric": ["Company", "Target"], "Ratio": [liq_val if liq_val else 0, 2.0]}
        )
        fig_liq = px.bar(
            df_liq,
            x="Ratio",
            y="Metric",
            orientation="h",
            color="Metric",
            color_discrete_map={"Company": "#1D3557", "Target": "#E63946"},
        )
        fig_liq.update_layout(
            height=120, margin=dict(l=0, r=0, t=10, b=0), showlegend=False
        )
        st.plotly_chart(fig_liq, use_container_width=True)

        # Debt-to-Equity Chart
        st.markdown("**Debt to Equity Ratio** (Target: ≤ 0.8)")
        df_solv = pd.DataFrame({
            "Metric": ["Company", "Target"],
            "Ratio": [solv_val if solv_val else 0, 0.8],
        })
        fig_solv = px.bar(
            df_solv,
            x="Ratio",
            y="Metric",
            orientation="h",
            color="Metric",
            color_discrete_map={"Company": "#1D3557", "Target": "#E63946"},
        )
        fig_solv.update_layout(
            height=120, margin=dict(l=0, r=0, t=10, b=0), showlegend=False
        )
        st.plotly_chart(fig_solv, use_container_width=True)
