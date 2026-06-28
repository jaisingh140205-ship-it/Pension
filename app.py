"""
Unified Financial & Retirement Calculator
==========================================
Built for The Actuarial Edge 2026 (IFoA × Marsh) — Pension Track

A behavioral nudge engine that diagnoses retirement gaps, educates on savings
vehicles, quantifies the cost of common financial mistakes, and recommends
an optimized multi-pillar savings mix (EPF + NPS + WeCare DB Plan).

Authors: Pension Track Submission
License: Educational Use Only
"""

# Python Easter Egg — because deploying this app should feel effortless!
# import antigravity  # 🐍 Uncomment if you want to fly! (opens xkcd.com/353)
# We reference it here per competition spec — the real antigravity is in the app itself.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# ---------------------------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Retirement Calculator | Actuarial Edge 2026",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CUSTOM CSS — Premium dark-themed aesthetic
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Root variables */
:root {
    --accent-gradient: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
    --success-green: #10b981;
    --warning-amber: #f59e0b;
    --danger-red: #ef4444;
    --card-bg: rgba(30, 30, 46, 0.6);
    --glass-border: rgba(255, 255, 255, 0.08);
}

/* Global font */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Main container spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Metric cards styling */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.05));
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px;
    padding: 16px 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
}
[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em;
}
[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #e2e8f0;
}

/* Expander styling */
[data-testid="stExpander"] {
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    overflow: hidden;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    font-weight: 600;
}

/* Button styling */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
    border: 1px solid rgba(99, 102, 241, 0.3);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}

/* Download button */
.stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
}

/* Info/Warning/Error boxes */
.stAlert {
    border-radius: 10px;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* Header styling */
h1 {
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}
h2 {
    font-weight: 700 !important;
}
h3 {
    font-weight: 600 !important;
}

/* Caption styling */
.stCaption {
    font-size: 0.8rem !important;
    opacity: 0.7;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #1e1b4b, #312e81, #4c1d95);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(139, 92, 246, 0.2);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
}
.hero-banner h1 {
    color: #f1f5f9;
    margin-bottom: 0.5rem;
}
.hero-banner p {
    color: #cbd5e1;
    font-size: 1.05rem;
    line-height: 1.6;
}

/* Score circle */
.score-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.score-circle {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 2.8rem;
    font-weight: 800;
    border: 6px solid;
    margin: 1rem auto;
    box-shadow: 0 0 30px rgba(0,0,0,0.2);
}

/* Payslip table */
.payslip-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.03));
    border: 1px solid rgba(99, 102, 241, 0.12);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------

def format_inr(amount: float) -> str:
    """
    Format a number in Indian currency format (Lakhs/Crores).

    Examples:
        1500000  → "₹15.00 L"
        25000000 → "₹2.50 Cr"
        50000    → "₹50,000"
    """
    if abs(amount) >= 1e7:
        return f"₹{amount / 1e7:.2f} Cr"
    elif abs(amount) >= 1e5:
        return f"₹{amount / 1e5:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def format_inr_full(amount: float) -> str:
    """Full Indian number format with commas: ₹15,00,000"""
    if amount < 0:
        return "-" + format_inr_full(-amount)
    s = str(int(round(amount)))
    if len(s) <= 3:
        return f"₹{s}"
    last_three = s[-3:]
    remaining = s[:-3]
    result = ""
    for i, digit in enumerate(reversed(remaining)):
        if i > 0 and i % 2 == 0:
            result = "," + result
        result = digit + result
    return f"₹{result},{last_three}"


# ---------------------------------------------------------------------------
# ACTUARIAL CALCULATION FUNCTIONS
# ---------------------------------------------------------------------------

def calculate_sip_fv(monthly_sip: float, annual_rate: float, years: int) -> float:
    """
    Future Value of a monthly SIP (Systematic Investment Plan).

    Formula: FV = PMT × [((1 + r)^n - 1) / r]
    where r = monthly rate, n = total months.

    This is the standard annuity-due future value formula used in actuarial
    mathematics (CT1/CM1 curriculum).

    Args:
        monthly_sip: Monthly investment amount in ₹
        annual_rate: Expected annual return rate (e.g. 10 for 10%)
        years: Number of years to invest

    Returns:
        Future value of the SIP at the end of the period
    """
    r = annual_rate / 12 / 100
    n = years * 12
    if r == 0 or n <= 0:
        return monthly_sip * max(n, 0)
    fv = monthly_sip * (((1 + r) ** n - 1) / r)
    return fv


def calculate_sip_fv_yearly(monthly_sip: float, annual_rate: float, years: int) -> list:
    """
    Year-by-year SIP accumulation for charting.

    Returns a list of cumulative FV at the end of each year.
    """
    values = []
    r = annual_rate / 12 / 100
    for y in range(1, years + 1):
        n = y * 12
        if r == 0:
            values.append(monthly_sip * n)
        else:
            values.append(monthly_sip * (((1 + r) ** n - 1) / r))
    return values


def calculate_epf_corpus(basic_annual: float, epf_rate: float,
                         salary_growth: float, years: int) -> float:
    """
    Year-by-year EPF accumulation.

    Employee contributes 12% of basic, employer contributes 12% of basic
    (of which 8.33% goes to EPS and 3.67% to EPF, but for simplicity
    we model the full 24% going to a single EPF pot).

    EPF compounds at the declared EPFO rate (currently 8.25%).

    Actuarial note: This is a Defined Contribution accumulation with a
    guaranteed interest rate — a unique hybrid that doesn't exist in
    most Western pension systems.
    """
    corpus = 0.0
    for year in range(years):
        annual_basic = basic_annual * (1 + salary_growth / 100) ** year
        annual_contribution = annual_basic * 0.24  # 12% employee + 12% employer
        corpus = (corpus + annual_contribution) * (1 + epf_rate / 100)
    return corpus


def calculate_nps_corpus(basic_annual: float, emp_pct: float, employer_pct: float,
                         return_rate: float, salary_growth: float, years: int) -> float:
    """
    NPS accumulation — market-linked Defined Contribution.

    Unlike EPF, NPS returns are not guaranteed. The assumed return rate
    represents the expected long-term CAGR of the NPS equity-heavy
    allocation (Aggressive Lifecycle Fund).
    """
    corpus = 0.0
    for year in range(years):
        annual_basic = basic_annual * (1 + salary_growth / 100) ** year
        annual_contribution = annual_basic * (emp_pct + employer_pct) / 100
        corpus = (corpus + annual_contribution) * (1 + return_rate / 100)
    return corpus


def calculate_wecare_pension(basic_annual: float, salary_growth: float, years: int) -> dict:
    """
    WeCare Defined Benefit pension calculation.

    Pension = (years_of_service / 60) × final_average_monthly_basic

    Uses the 1/60th accrual rate standard in many DB pension schemes.
    The denominator of 60 means an employee needs 60 years of service to
    earn a 100% pension — since nobody works 60 years, the practical
    maximum is the 2/3rds cap.

    Commutation: up to 1/3 of annual pension can be exchanged for a lump
    sum at a commutation factor of 12 (actuarial annuity factor at 6%
    discount rate, based on Indian Assured Lives Mortality 2012-14 table,
    ~20 years post-retirement life expectancy).
    """
    final_annual_basic = basic_annual * (1 + salary_growth / 100) ** years
    final_monthly_basic = final_annual_basic / 12

    accrual_fraction = min(years / 60, 2 / 3)  # Cap at 2/3rds
    monthly_pension = accrual_fraction * final_monthly_basic
    annual_pension = monthly_pension * 12

    # Commutation
    commutation_lump_sum = (1 / 3) * annual_pension * 12  # Factor of 12
    residual_annual_pension = (2 / 3) * annual_pension
    residual_monthly_pension = residual_annual_pension / 12

    # Pension Wealth (PV of residual pension stream using same annuity factor)
    pension_wealth_pv = residual_annual_pension * 12

    return {
        "monthly_pension": monthly_pension,
        "annual_pension": annual_pension,
        "commutation_lump_sum": commutation_lump_sum,
        "residual_monthly_pension": residual_monthly_pension,
        "residual_annual_pension": residual_annual_pension,
        "pension_wealth_pv": pension_wealth_pv,
        "accrual_fraction": accrual_fraction,
    }


def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> float:
    """
    Standard EMI (Equated Monthly Installment) formula.

    EMI = P × r × (1+r)^n / ((1+r)^n - 1)

    Where:
        P = Loan principal (house price minus down payment)
        r = Monthly interest rate (annual rate / 12 / 100)
        n = Total number of monthly payments (tenure × 12)

    This is the standard present value of annuity formula rearranged
    to solve for the periodic payment. In actuarial notation, this is
    equivalent to P / ä_n (annuity-certain PV factor).
    """
    r = annual_rate / 12 / 100
    n = tenure_years * 12
    if r == 0:
        return principal / n if n > 0 else 0
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return emi


def calculate_opportunity_cost(monthly_amount: float, annual_return: float,
                               years: int) -> float:
    """
    What would the EMI amount grow to if invested in equity instead?

    This is the core "opportunity cost" calculation — the wealth you
    DIDN'T build because your money went to loan repayment instead
    of equity compounding.

    Uses the same FV of annuity formula as the Cost of Delay chart.
    """
    return calculate_sip_fv(monthly_amount, annual_return, years)


def calculate_health_score(replacement_ratio: float, savings_rate: float,
                           emi_ratio: float, num_pillars: int) -> float:
    """
    Composite financial health score (0-100).

    Components (weighted):
        - Replacement Ratio Score (40%): Based on distance from 60% target
        - Savings Rate Score (25%): % of gross income saved for retirement
        - EMI Affordability Score (20%): Whether EMI < 30% of net pay
        - Diversification Score (15%): Using multiple pillars vs. EPF-only

    This is a simplified scoring rubric for educational purposes.
    Real financial health assessments would use Monte Carlo simulation
    and stochastic mortality models.
    """
    rr_score = min(replacement_ratio / 60 * 100, 100) * 0.40
    sr_score = min(savings_rate / 20 * 100, 100) * 0.25
    if emi_ratio > 0:
        emi_score = max(0, (30 - emi_ratio) / 30 * 100) * 0.20
    else:
        emi_score = 100 * 0.20
    # Diversification: 1 pillar=33, 2=67, 3=100
    div_map = {0: 0, 1: 33, 2: 67, 3: 100}
    div_score = div_map.get(min(num_pillars, 3), 100) * 0.15
    return rr_score + sr_score + emi_score + div_score


def build_full_context() -> str:
    """Build a comprehensive context string from session state for AI prompts."""
    ss = st.session_state
    return (
        f"Age: {ss.get('age', 28)}, "
        f"Salary: ₹{ss.get('salary', 2000000):,}/year, "
        f"Basic: {ss.get('basic_pct', 40)}% of CTC, "
        f"EPF Corpus at 60: {format_inr(ss.get('epf_corpus', 0))}, "
        f"NPS Corpus at 60: {format_inr(ss.get('nps_corpus', 0))}, "
        f"WeCare Monthly Pension: {format_inr(ss.get('wecare_monthly_pension', 0))}, "
        f"Replacement Ratio: {ss.get('replacement_ratio', 0):.1f}%, "
        f"EMI: {format_inr(ss.get('emi_val', 0))}/month, "
        f"Health Score: {ss.get('health_score', 0):.0f}/100, "
        f"Net Take-Home: {format_inr(ss.get('net_take_home', 0))}/month, "
        f"Years to Retirement: {ss.get('years_to_retire', 32)}, "
        f"Salary Growth: {ss.get('salary_growth', 7)}%, "
        f"Expected Equity Return: {ss.get('equity_return', 10)}%, "
        f"NPS Contribution: {ss.get('nps_pct', 10)}% of basic, "
        f"Employer NPS: {ss.get('employer_nps_pct', 10)}% of basic, "
        f"Inflation: {ss.get('inflation', 6)}%"
    )


# ---------------------------------------------------------------------------
# GEMINI AI INTEGRATION
# ---------------------------------------------------------------------------

def get_gemini_response(api_key: str, prompt: str, context: str = "") -> str:
    """
    Send a prompt to Gemini and return the response.
    Uses gemini-2.0-flash (free tier, fast, good reasoning).

    Args:
        api_key: User's Gemini API key
        prompt: The user's question or the system-generated explanation request
        context: Financial context string with the user's current numbers

    Returns:
        Gemini's response as a string, or an error message
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        system_context = f"""You are a friendly, expert financial advisor embedded 
in a retirement planning calculator app. You explain complex actuarial and 
financial concepts in simple, everyday Hindi-English (Hinglish) or plain 
English — as if explaining to a smart friend who has never studied finance.

RULES:
- Use analogies from daily Indian life (chai, cricket, Bollywood, EMIs, 
  salary day, etc.)
- Always use Indian number formatting (Lakhs, Crores)
- Never use jargon without immediately explaining it
- Be encouraging but honest — don't sugarcoat bad numbers
- Keep responses under 200 words unless asked for detail
- Use emojis sparingly but effectively
- If the user's retirement is severely underfunded, be direct but empathetic

USER'S CURRENT FINANCIAL SNAPSHOT:
{context}
"""
        response = model.generate_content(f"{system_context}\n\nUser's question: {prompt}")
        return response.text
    except Exception as e:
        return (
            f"⚠️ AI Assistant error: {str(e)}. "
            "The calculator still works fully without AI."
        )


def ai_button(label: str, prompt: str, context: str, key: str,
              gemini_api_key: str | None):
    """
    Render an AI explanation button. If no API key, shows an info message.
    """
    if gemini_api_key:
        if st.button(label, key=key):
            with st.spinner("🤖 Thinking..."):
                response = get_gemini_response(gemini_api_key, prompt, context)
            st.markdown(response)
    else:
        st.info(
            "🔑 Add your free Gemini API key in the sidebar to unlock AI explanations."
        )


# ---------------------------------------------------------------------------
# SIDEBAR — Global Inputs
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 0.5rem 0 0.8rem 0;">
            <span style="font-size: 2rem;">🎯</span><br>
            <span style="font-size: 1.1rem; font-weight: 700; 
                   background: linear-gradient(135deg, #818cf8, #c084fc);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Retirement Planner
            </span><br>
            <span style="font-size: 0.7rem; opacity: 0.6;">Actuarial Edge 2026 · IFoA × Marsh</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.header("👤 Your Profile")

    age = st.slider(
        "Your Current Age", 22, 55, 28,
        help="Your age today. The app will project everything from now to age 60.",
    )
    salary = st.number_input(
        "Annual Salary (CTC) in ₹",
        min_value=300000, max_value=50000000, value=2000000, step=100000,
        help="Your total Cost-to-Company. This is the number on your offer letter, "
             "not your take-home pay.",
    )
    basic_pct = st.slider(
        "Basic Salary (% of CTC)", 30, 60, 40,
        help="Basic salary is usually 40-50% of CTC. Check your payslip. "
             "EPF and pension contributions are calculated on this amount.",
    )

    st.markdown("---")
    st.header("📈 Assumptions")

    salary_growth = st.slider(
        "Expected Annual Salary Growth (%)", 4.0, 12.0, 7.0, 0.5,
        help="How much you expect your salary to grow each year. "
             "India average is 7-9% for IT/corporate roles.",
    )
    equity_return = st.slider(
        "Expected Market Return — NPS/Equity (%)", 8.0, 15.0, 10.0, 0.5,
        help="Long-term equity returns in India have been ~12-14% (Nifty 50). "
             "We use a conservative 10% as the default.",
    )
    epf_rate = st.slider(
        "EPF Interest Rate (%)", 7.0, 9.0, 8.25, 0.25,
        help="EPFO declares this rate annually. FY2025-26 rate is 8.25%.",
    )
    inflation = st.slider(
        "Expected Inflation Rate (%)", 4.0, 8.0, 6.0, 0.5,
        help="RBI targets 4% inflation. Actual averages 5-6%. "
             "This affects the real purchasing power of your future money.",
    )

    st.markdown("---")
    st.header("💰 Your Contributions")

    nps_pct = st.slider(
        "Your NPS Contribution (% of Basic)", 0, 20, 10,
        help="Your voluntary NPS contribution. Employer may also contribute separately.",
    )
    employer_nps_pct = st.slider(
        "Employer NPS Contribution (% of Basic)", 0, 14, 10,
        help="Check with HR. Up to 14% is tax-free under Section 80CCD(2).",
    )

    # ELI5 Toggle
    st.markdown("---")
    eli5_mode = st.toggle(
        "🧒 Simple Language Mode", value=False,
        help="Turn this on to get AI-powered super-simple explanations "
             "next to every number. Best for first-time users.",
    )

    # Gemini AI section
    st.markdown("---")
    st.subheader("🤖 AI Financial Assistant")
    st.caption("Powered by Google Gemini (Free Tier)")
    gemini_api_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        help="Get a free API key at https://aistudio.google.com/apikey. "
             "Your key is never stored — it's only used during this session.",
    )
    if gemini_api_key:
        st.success("✅ AI Assistant is active!")
    else:
        st.info(
            "💡 Add your free Gemini API key to unlock the AI assistant. "
            "The app works fully without it — AI just adds conversational explanations."
        )


# ---------------------------------------------------------------------------
# DERIVED VALUES (shared across all tabs)
# ---------------------------------------------------------------------------
years = max(60 - age, 1)  # Years to retirement
basic_annual = salary * basic_pct / 100
basic_monthly = basic_annual / 12

# EPF
epf_monthly_employee = basic_monthly * 0.12
epf_monthly_employer = basic_monthly * 0.12
epf_corpus = calculate_epf_corpus(basic_annual, epf_rate, salary_growth, years)

# NPS
nps_monthly_employee = basic_monthly * nps_pct / 100
nps_monthly_employer = basic_monthly * employer_nps_pct / 100
nps_corpus = calculate_nps_corpus(
    basic_annual, nps_pct, employer_nps_pct, equity_return, salary_growth, years
)

# WeCare
wecare_monthly_contribution = basic_monthly * 0.10
wecare = calculate_wecare_pension(basic_annual, salary_growth, years)

# Take-home (approximate)
gross_monthly = salary / 12
total_deductions = epf_monthly_employee + nps_monthly_employee + wecare_monthly_contribution
net_take_home = gross_monthly - total_deductions

# Total retirement wealth
total_wealth = epf_corpus + nps_corpus + wecare["commutation_lump_sum"] + wecare["pension_wealth_pv"]

# Final salary
final_annual_salary = salary * (1 + salary_growth / 100) ** years
final_monthly_salary = final_annual_salary / 12

# Replacement Ratio
annual_retirement_income = (
    wecare["residual_annual_pension"]
    + (epf_corpus + nps_corpus) * 0.04  # 4% safe withdrawal from DC pots
)
replacement_ratio = (annual_retirement_income / final_annual_salary) * 100 if final_annual_salary > 0 else 0

# Store in session_state for AI context
st.session_state["age"] = age
st.session_state["salary"] = salary
st.session_state["basic_pct"] = basic_pct
st.session_state["salary_growth"] = salary_growth
st.session_state["equity_return"] = equity_return
st.session_state["inflation"] = inflation
st.session_state["nps_pct"] = nps_pct
st.session_state["employer_nps_pct"] = employer_nps_pct
st.session_state["epf_corpus"] = epf_corpus
st.session_state["nps_corpus"] = nps_corpus
st.session_state["wecare_monthly_pension"] = wecare["monthly_pension"]
st.session_state["replacement_ratio"] = replacement_ratio
st.session_state["net_take_home"] = net_take_home
st.session_state["years_to_retire"] = years
st.session_state["total_wealth"] = total_wealth


# ---------------------------------------------------------------------------
# PLOTLY CHART THEME
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(l=40, r=40, t=60, b=40),
    hoverlabel=dict(
        bgcolor="rgba(30,30,46,0.95)",
        font_size=13,
        font_family="Inter, sans-serif",
    ),
)


# ---------------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------------

pages = [
    "🏠 Home",
    "📊 Savings Vehicles",
    "🧮 Retirement Calculator",
    "🏗️ Housing vs. Retirement",
    "🎯 Financial Health Report",
]
if gemini_api_key:
    pages.append("💬 AI Assistant")

with st.sidebar:
    st.markdown("---")
    st.header("🧭 Navigation")
    nav = st.radio("Go to", pages, label_visibility="collapsed")


# ═══════════════════════════════════════════════════════════════════════════
# 🏠 HOME / WELCOME TAB
# ═══════════════════════════════════════════════════════════════════════════

if nav == "🏠 Home":

    # Onboarding
    if not st.session_state.get("onboarded"):
        st.markdown(
            """
            <div class="hero-banner">
                <h1>🎯 Welcome to Your Retirement Planning Dashboard</h1>
                <p>The one tool that shows you the truth about your financial future — 
                in 5 minutes or less.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("""
### In the next 5 minutes, you'll discover:
1. 💡 **Whether your EPF alone is enough** (spoiler: it's probably not)
2. 📉 **How much delaying investments is costing you** every single day
3. 🏠 **The hidden price of buying a house too early**
4. 🎯 **A personalized action plan** to secure your retirement

> *Built for The Actuarial Edge 2026 (IFoA × Marsh) — Pension Track*
        """)

        st.info("👈 Start by filling in your details in the sidebar, then explore each tab.")

        if st.button("Let's Get Started! 🚀", type="primary"):
            st.session_state["onboarded"] = True
            st.rerun()
    else:
        # Post-onboarding home
        st.markdown(
            """
            <div class="hero-banner">
                <h1>🎯 Your Retirement Planning Dashboard</h1>
                <p>Diagnose. Educate. Optimize. Act.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Shock-value statistics
        st.subheader("😱 Why Should You Care?")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Indians with adequate retirement savings", "5%",
                delta="-95% are at risk", delta_color="inverse",
            )
            st.caption("Source: HSBC Future of Retirement Survey")
        with col2:
            st.metric(
                "Cost of 10-year delay on ₹10K/month SIP", "₹1.5+ Cr lost",
                delta="68% of potential corpus", delta_color="inverse",
            )
            st.caption("At 10% CAGR, starting at 25 vs 35")
        with col3:
            st.metric(
                "EPF alone replaces", "~30% of final salary",
                delta="Target is 50-70%", delta_color="inverse",
            )
            st.caption("IFoA/OECD adequacy benchmark")

        st.markdown("---")

        # Quick snapshot
        st.subheader("📸 Your Quick Snapshot")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Current Age", f"{age} yrs")
            st.caption(f"{years} years to retirement at 60")
        with c2:
            st.metric("Annual CTC", format_inr(salary))
            st.caption(f"Basic: {format_inr(basic_annual)}/yr")
        with c3:
            st.metric("Monthly Take-Home (Est.)", format_inr(net_take_home))
            st.caption("After EPF + NPS + WeCare deductions")
        with c4:
            color = "🟢" if replacement_ratio >= 50 else ("🟡" if replacement_ratio >= 40 else "🔴")
            st.metric("Replacement Ratio", f"{color} {replacement_ratio:.1f}%")
            st.caption("Target: 50-70%")

        st.markdown("---")
        st.markdown("""
### 🧭 How to Use This App
| Step | Where | What You'll Learn |
|------|-------|--------------------|
| 1️⃣ | **Sidebar** | Fill in your age, salary & contribution preferences |
| 2️⃣ | **📊 Savings Vehicles** | Compare EPF, NPS, PPF, ELSS side-by-side |
| 3️⃣ | **🧮 Retirement Calculator** | See your multi-pillar retirement projection |
| 4️⃣ | **🏗️ Housing vs. Retirement** | Understand the true cost of buying a home early |
| 5️⃣ | **🎯 Financial Health Report** | Get your score + personalized action plan |
        """)


# ═══════════════════════════════════════════════════════════════════════════
# 📊 TAB 1: SAVINGS VEHICLES COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

elif nav == "📊 Savings Vehicles":

    st.markdown(
        """
        <div class="hero-banner">
            <h1>📊 Savings Vehicles — Know Your Options</h1>
            <p>Not all savings instruments are created equal. Let's break them down.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Feature 1: Comparison Table ──────────────────────────────────────
    st.subheader("🔍 Side-by-Side Comparison")

    comparison_data = {
        "Feature": [
            "What Is It?",
            "Risk Level",
            "Can I Withdraw?",
            "Tax Benefit",
            "Expected Return",
            "Employer Chips In?",
            "Enough for Retirement?",
        ],
        "EPF": [
            "Mandatory retirement fund by your employer",
            "⬜ Zero (Govt. guaranteed)",
            "Partial rules; full at 58",
            "EEE — No tax at any stage",
            "~8.25% (fixed)",
            "✅ Yes — 12% of basic",
            "❌ Alone, only 25-35% replacement",
        ],
        "NPS (Tier-I)": [
            "Voluntary government pension scheme",
            "🟧 Moderate-High (market-linked)",
            "Locked to 60 (25% partial after 3 yrs)",
            "Extra ₹50K u/s 80CCD(1B); 60% taxed at exit",
            "9-12% (market-dependent)",
            "✅ Up to 14% of basic (if offered)",
            "✅ Strong 2nd pillar",
        ],
        "PPF": [
            "Government savings scheme (post office/bank)",
            "⬜ Zero (Govt. guaranteed)",
            "15-yr lock-in (partial from Yr 7)",
            "EEE — No tax at any stage",
            "~7.1% (fixed)",
            "❌ No",
            "❌ Supplementary only",
        ],
        "ELSS Mutual Funds": [
            "Tax-saving equity mutual funds",
            "🟥 High (market-linked)",
            "3-yr lock-in, then anytime",
            "₹1.5L u/s 80C; LTCG >₹1.25L taxed at 12.5%",
            "12-15% (long-term equity)",
            "❌ No",
            "✅ Best for aggressive growth",
        ],
    }
    df_compare = pd.DataFrame(comparison_data)
    st.dataframe(
        df_compare.set_index("Feature"),
        use_container_width=True,
        height=320,
    )

    st.info("""
**🔑 Key Takeaway:** EPF is your safety net, not your retirement plan.

Think of it like this: EPF is the *dal-chawal* (basic meal) of retirement planning. 
It keeps you alive, but for a comfortable life, you need NPS (the *sabzi*), 
mutual funds (the dessert), and ideally an employer pension (the *full thali*). 🍽️
    """)

    ai_button(
        "🤖 Explain these vehicles in simple terms",
        "Explain the difference between EPF, NPS, PPF, and ELSS to someone who "
        "has never heard of any of them. Use a food menu analogy.",
        build_full_context(), "ai_vehicles", gemini_api_key,
    )

    st.markdown("---")

    # ── Feature 2: Cost of Delay Visualization ───────────────────────────
    st.subheader("⏰ The Exponential Cost of Waiting")
    st.caption(
        "See how much you lose by delaying your investments even by a few years."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        delay_age = st.slider(
            "Your starting age for this analysis", 22, 40, min(age, 35),
            key="delay_age",
            help="We'll compare starting now vs. starting 5 and 10 years later.",
        )
    with col_b:
        monthly_sip = st.number_input(
            "Monthly SIP Amount (₹)", min_value=1000, max_value=500000,
            value=10000, step=1000,
            help="How much you plan to invest each month.",
        )

    years_now = max(60 - delay_age, 1)
    years_5 = max(60 - delay_age - 5, 1)
    years_10 = max(60 - delay_age - 10, 1)

    fv_now = calculate_sip_fv(monthly_sip, equity_return, years_now)
    fv_5 = calculate_sip_fv(monthly_sip, equity_return, years_5)
    fv_10 = calculate_sip_fv(monthly_sip, equity_return, years_10)

    # Year-by-year for chart
    vals_now = calculate_sip_fv_yearly(monthly_sip, equity_return, years_now)
    vals_5 = [0] * 5 + calculate_sip_fv_yearly(monthly_sip, equity_return, years_5)
    vals_10 = [0] * 10 + calculate_sip_fv_yearly(monthly_sip, equity_return, years_10)

    # Pad shorter lists
    max_len = years_now
    vals_5 += [vals_5[-1]] * (max_len - len(vals_5)) if len(vals_5) < max_len else []
    vals_10 += [vals_10[-1]] * (max_len - len(vals_10)) if len(vals_10) < max_len else []
    vals_5 = vals_5[:max_len]
    vals_10 = vals_10[:max_len]

    ages_list = list(range(delay_age + 1, delay_age + 1 + max_len))

    fig_delay = go.Figure()
    fig_delay.add_trace(go.Scatter(
        x=ages_list, y=vals_now, name=f"Start at {delay_age}",
        mode="lines", fill="tozeroy",
        line=dict(color="#10b981", width=3),
        fillcolor="rgba(16,185,129,0.1)",
        hovertemplate="Age %{x}<br>Corpus: ₹%{y:,.0f}<extra></extra>",
    ))
    fig_delay.add_trace(go.Scatter(
        x=ages_list, y=vals_5, name=f"Start at {delay_age + 5}",
        mode="lines", fill="tozeroy",
        line=dict(color="#f59e0b", width=3),
        fillcolor="rgba(245,158,11,0.1)",
        hovertemplate="Age %{x}<br>Corpus: ₹%{y:,.0f}<extra></extra>",
    ))
    fig_delay.add_trace(go.Scatter(
        x=ages_list, y=vals_10, name=f"Start at {delay_age + 10}",
        mode="lines", fill="tozeroy",
        line=dict(color="#ef4444", width=3),
        fillcolor="rgba(239,68,68,0.1)",
        hovertemplate="Age %{x}<br>Corpus: ₹%{y:,.0f}<extra></extra>",
    ))

    # Endpoint annotations
    fig_delay.add_annotation(
        x=ages_list[-1], y=vals_now[-1],
        text=f"<b>{format_inr(fv_now)}</b>",
        showarrow=True, arrowhead=2, ax=40, ay=-30,
        font=dict(color="#10b981", size=13),
    )
    fig_delay.add_annotation(
        x=ages_list[-1], y=vals_5[-1],
        text=f"<b>{format_inr(fv_5)}</b>",
        showarrow=True, arrowhead=2, ax=40, ay=-30,
        font=dict(color="#f59e0b", size=13),
    )
    fig_delay.add_annotation(
        x=ages_list[-1], y=vals_10[-1],
        text=f"<b>{format_inr(fv_10)}</b>",
        showarrow=True, arrowhead=2, ax=40, ay=-30,
        font=dict(color="#ef4444", size=13),
    )

    fig_delay.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="The Exponential Cost of Waiting", font=dict(size=18)),
        xaxis_title="Age",
        yaxis_title="Corpus Value (₹)",
        yaxis=dict(tickformat=","),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        height=480,
    )
    st.plotly_chart(fig_delay, use_container_width=True)

    # Layer 1 — Glance
    loss_5 = fv_now - fv_5
    loss_10 = fv_now - fv_10
    loss_pct_5 = (loss_5 / fv_now * 100) if fv_now > 0 else 0
    loss_pct_10 = (loss_10 / fv_now * 100) if fv_now > 0 else 0

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.metric(f"🟢 Start at {delay_age}", format_inr(fv_now))
        st.caption("Full compounding benefit")
    with mc2:
        st.metric(f"🟡 Start at {delay_age + 5}", format_inr(fv_5),
                  delta=f"-{format_inr(loss_5)}", delta_color="inverse")
        st.caption(f"{loss_pct_5:.0f}% permanent loss")
    with mc3:
        st.metric(f"🔴 Start at {delay_age + 10}", format_inr(fv_10),
                  delta=f"-{format_inr(loss_10)}", delta_color="inverse")
        st.caption(f"{loss_pct_10:.0f}% permanent loss")

    # Layer 2 — Read
    st.warning(f"""
⏰ **The Math of Waiting:**
- Start at age {delay_age}: Your ₹{monthly_sip:,}/month becomes **{format_inr(fv_now)}**
- Start at age {delay_age + 5}: Same ₹{monthly_sip:,}/month becomes only **{format_inr(fv_5)}** \
— you permanently lose **{format_inr(loss_5)}** ({loss_pct_5:.0f}% of your potential)
- Start at age {delay_age + 10}: Only **{format_inr(fv_10)}** \
— you lose **{format_inr(loss_10)}** ({loss_pct_10:.0f}%)

The money you lose isn't just your contributions — it's the GROWTH on those \
contributions. Time is the only financial asset you can never get back.
    """)

    # Layer 3 — Deep Dive
    with st.expander("📐 Show Me The Math — Step by Step"):
        r_monthly = equity_return / 1200
        n_months = years_now * 12
        multiplier = ((1 + r_monthly) ** n_months - 1) / r_monthly if r_monthly > 0 else n_months
        st.markdown(f"""
**Formula Used:** Future Value of Annuity (Monthly SIP)

`FV = PMT × [((1 + r)^n - 1) / r]`

Where:
- PMT = ₹{monthly_sip:,} (your monthly investment)
- r = {equity_return}% ÷ 12 = {equity_return / 12:.4f}% per month = {r_monthly:.6f}
- n = {years_now} years × 12 = {n_months} months

**Plugging in your numbers:**

FV = {monthly_sip:,} × [((1 + {r_monthly:.6f})^{n_months} - 1) / {r_monthly:.6f}]

FV = {monthly_sip:,} × [{multiplier:,.2f}]

FV = **{format_inr(fv_now)}**

*This is the same formula taught in IFoA's CM1 (Actuarial Mathematics) — \
the future value of an annuity-certain payable monthly.*
        """)

    # AI Layer
    ai_button(
        "🤖 Explain this in simple terms",
        f"Explain the cost of delay to a {delay_age}-year-old who invests "
        f"₹{monthly_sip:,}/month. Starting now gives {format_inr(fv_now)}, but "
        f"waiting 10 years gives only {format_inr(fv_10)}. "
        f"Use a relatable Indian analogy.",
        build_full_context(), "ai_cost_of_delay", gemini_api_key,
    )

    st.markdown("---")

    # ── Feature 3: Quick Self-Assessment ─────────────────────────────────
    st.subheader("🚦 Are You on Track? — Quick Self-Assessment")

    savings_pct = st.slider(
        "What % of your monthly salary do you save/invest for retirement (excluding EPF)?",
        0, 30, 5,
        help="Include NPS, PPF, SIPs, any voluntary retirement savings.",
    )

    if savings_pct < 5:
        st.error(
            "🔴 **Your retirement is severely underfunded.** Every month you wait "
            "costs you real money. Please explore the Retirement Calculator tab "
            "to see the exact gap."
        )
    elif savings_pct <= 15:
        st.warning(
            "🟡 **You're saving, but probably not enough.** Let's check with the "
            "calculator whether this hits the 50-70% replacement ratio target."
        )
    else:
        st.success(
            "🟢 **Strong start!** You're ahead of most Indians your age. Let's "
            "verify if this is enough to hit the 50-70% target."
        )


# ═══════════════════════════════════════════════════════════════════════════
# 🧮 TAB 2: RETIREMENT CALCULATOR & WeCare DB PLAN
# ═══════════════════════════════════════════════════════════════════════════

elif nav == "🧮 Retirement Calculator":

    st.markdown(
        """
        <div class="hero-banner">
            <h1>🧮 Multi-Pillar Retirement Projection</h1>
            <p>EPF + NPS + WeCare DB Plan — your complete retirement picture at age 60.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── WeCare Explanation ───────────────────────────────────────────────
    with st.expander("🏢 What is the "WeCare" Pension Plan? (Click to learn)", expanded=False):
        st.markdown("""
### 🏢 What is the "WeCare" Pension Plan?

Imagine your company makes you a **promise**: *"Work here until you retire, and 
we'll pay you a guaranteed monthly income for life after that."*

That's a **Defined Benefit (DB) pension plan**. Unlike EPF or NPS where YOUR 
retirement depends on how markets perform, a DB plan puts that risk on the 
EMPLOYER. They promise the outcome, not just the contribution.

**How WeCare works:**
- 📥 **You contribute:** 10% of your basic salary every month
- 🏢 **Your employer guarantees:** A monthly pension based on your final salary 
  and years of service
- 🧮 **The formula:** For every year you work, you earn **1/60th** of your final 
  salary as annual pension

> **Example:** If you work for 30 years and your final basic salary is ₹3,00,000/month:
> - Pension = (30 ÷ 60) × ₹3,00,000 = **₹1,50,000/month for life** ✅
> - That's 50% of your final salary — exactly the target!

💡 **Commutation** is like a trade: you give up some of your monthly pension 
forever, and in exchange, you get a big one-time lump sum at retirement. For 
every ₹1 of annual pension you sacrifice, you get ₹12 as a lump sum. It's 
useful if you need money for a big expense at 60 (medical, house renovation, 
child's wedding).
        """)

    st.markdown("---")

    # ── Section A: Monthly Payslip Impact ────────────────────────────────
    st.subheader("💳 Your Monthly Payslip Impact — What Changes Today?")

    ps1, ps2, ps3, ps4, ps5 = st.columns(5)
    with ps1:
        st.metric("Gross Monthly", format_inr(gross_monthly))
        st.caption("CTC ÷ 12")
    with ps2:
        st.metric("- EPF (12%)", format_inr(epf_monthly_employee))
        st.caption("Your mandatory EPF share")
    with ps3:
        st.metric(f"- NPS ({nps_pct}%)", format_inr(nps_monthly_employee))
        st.caption("Your voluntary NPS contribution")
    with ps4:
        st.metric("- WeCare (10%)", format_inr(wecare_monthly_contribution))
        st.caption("DB pension contribution")
    with ps5:
        st.metric("= Take-Home (Est.)", format_inr(net_take_home))
        st.caption("What hits your bank account")

    # Donut chart
    deduction_labels = ["Take-Home", "EPF (Employee)", "NPS (Employee)", "WeCare"]
    deduction_values = [
        net_take_home,
        epf_monthly_employee,
        nps_monthly_employee,
        wecare_monthly_contribution,
    ]
    deduction_colors = ["#10b981", "#6366f1", "#f59e0b", "#ec4899"]

    fig_donut = go.Figure(go.Pie(
        labels=deduction_labels,
        values=deduction_values,
        hole=0.55,
        marker=dict(colors=deduction_colors),
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="%{label}: ₹%{value:,.0f}<br>(%{percent})<extra></extra>",
    ))
    fig_donut.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Monthly Salary Breakdown", font=dict(size=16)),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    # Context box
    total_monthly_deduction = epf_monthly_employee + nps_monthly_employee + wecare_monthly_contribution
    total_contributions_lifetime = total_monthly_deduction * 12 * years
    roi_multiple = total_wealth / total_contributions_lifetime if total_contributions_lifetime > 0 else 0

    st.success(f"""
💰 **The Trade-Off:**

You're setting aside **{format_inr(total_monthly_deduction)}/month** today 
(that's {format_inr(total_monthly_deduction)} less in your bank account).

But this buys you a projected **{format_inr(total_wealth)}** at age 60.

That's a return of **{roi_multiple:.0f}x** on your total contributions. 
Where else do you get that kind of deal? 📈
    """)

    ai_button(
        "🤖 Explain my payslip impact",
        f"My monthly take-home is {format_inr(net_take_home)} after {format_inr(total_monthly_deduction)} "
        f"in retirement deductions. Explain whether this trade-off is worth it in simple terms.",
        build_full_context(), "ai_payslip", gemini_api_key,
    )

    st.markdown("---")

    # ── Section B: Retirement Projection at 60 ───────────────────────────
    st.subheader(f"📊 Your Retirement Projection at Age 60 ({years} years away)")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏦 EPF Corpus at 60", format_inr(epf_corpus))
        st.caption("Defined Contribution + guaranteed interest at "
                   f"{epf_rate}% p.a.")
    with col2:
        st.metric("📈 NPS Corpus at 60", format_inr(nps_corpus))
        st.caption(f"Market-linked returns assumed at {equity_return}% p.a.")
    with col3:
        st.metric("🏢 WeCare Pension (Monthly)", format_inr(wecare["monthly_pension"]))
        st.caption(f"Based on {years} years of service, "
                   f"{wecare['accrual_fraction'] * 100:.1f}% accrual")

    wcol1, wcol2, wcol3 = st.columns(3)
    with wcol1:
        st.metric("🔄 WeCare Commutation Lump Sum",
                  format_inr(wecare["commutation_lump_sum"]))
        st.caption("1/3 of annual pension × commutation factor 12")
    with wcol2:
        st.metric("📅 Residual Monthly Pension",
                  format_inr(wecare["residual_monthly_pension"]))
        st.caption("After commutation (2/3 of original)")
    with wcol3:
        st.metric("💰 Total Retirement Wealth", format_inr(total_wealth))
        st.caption("EPF + NPS + WeCare (Commutation + Pension Wealth)")

    with st.expander("📐 Show Me The Math — EPF & NPS Accumulation"):
        st.markdown(f"""
**EPF Accumulation (Year-by-year):**
- Contribution rate: 24% of basic salary (12% employee + 12% employer)
- Starting basic: {format_inr(basic_annual)}/year
- Growth rate: {salary_growth}% p.a.
- Interest rate: {epf_rate}% p.a. (compounded annually)
- For each year: Corpus = (Previous Corpus + Annual Contribution) × (1 + {epf_rate}%)

**NPS Accumulation:**
- Your contribution: {nps_pct}% of basic
- Employer contribution: {employer_nps_pct}% of basic
- Total: {nps_pct + employer_nps_pct}% of basic salary
- Assumed market return: {equity_return}% CAGR

**WeCare DB Pension:**
- Accrual rate: 1/60th per year of service
- Your service: {years} years → Accrual = {min(years, 40)}/60 = {wecare['accrual_fraction'] * 100:.2f}%
- Final monthly basic (projected): {format_inr(basic_annual * (1 + salary_growth / 100) ** years / 12)}
- Monthly pension = {wecare['accrual_fraction'] * 100:.2f}% × Final Basic = {format_inr(wecare['monthly_pension'])}
        """)

    ai_button(
        "🤖 Explain my retirement projection",
        f"My EPF corpus will be {format_inr(epf_corpus)}, NPS will be {format_inr(nps_corpus)}, "
        f"and WeCare pension is {format_inr(wecare['monthly_pension'])}/month. "
        f"Is my total of {format_inr(total_wealth)} enough? Break it down for me.",
        build_full_context(), "ai_projection", gemini_api_key,
    )

    st.markdown("---")

    # ── Section C: Replacement Ratio Gauge ───────────────────────────────
    st.subheader("📏 The Replacement Ratio Verdict")
    st.caption(
        "Replacement Ratio = What % of your final salary your retirement income replaces"
    )

    # Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=replacement_ratio,
        number=dict(suffix="%", font=dict(size=48, weight="bold")),
        delta=dict(reference=60, suffix="%",
                   increasing=dict(color="#10b981"),
                   decreasing=dict(color="#ef4444")),
        title=dict(text="Your Replacement Ratio", font=dict(size=18)),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=2, tickcolor="#475569"),
            bar=dict(color="#8b5cf6", thickness=0.3),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=2,
            bordercolor="rgba(255,255,255,0.1)",
            steps=[
                dict(range=[0, 40], color="rgba(239,68,68,0.2)"),
                dict(range=[40, 50], color="rgba(245,158,11,0.2)"),
                dict(range=[50, 70], color="rgba(16,185,129,0.2)"),
                dict(range=[70, 100], color="rgba(59,130,246,0.2)"),
            ],
            threshold=dict(
                line=dict(color="#f1f5f9", width=4),
                thickness=0.8,
                value=replacement_ratio,
            ),
        ),
    ))
    fig_gauge.update_layout(
        **PLOTLY_LAYOUT,
        height=350,
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Verdict text
    if replacement_ratio >= 70:
        st.success(
            f"🔵 **Excellent ({replacement_ratio:.1f}%)** — Above the IFoA/OECD benchmark! "
            "Your multi-pillar strategy is working beautifully."
        )
    elif replacement_ratio >= 50:
        st.success(
            f"🟢 **On Track ({replacement_ratio:.1f}%)** — Meets the IFoA/OECD benchmark "
            "of 50-70%. Keep going!"
        )
    elif replacement_ratio >= 40:
        st.warning(
            f"🟡 **Below Target ({replacement_ratio:.1f}%)** — You're close but not there yet. "
            "Consider increasing your NPS contribution or adding equity SIPs."
        )
    else:
        st.error(
            f"🔴 **Danger — Severe Shortfall ({replacement_ratio:.1f}%)** — "
            "At this rate, you'll face a significant retirement gap. "
            "Immediate action is needed. Check the Financial Health Report tab."
        )

    # Inflation reality check
    real_corpus = total_wealth / ((1 + inflation / 100) ** years)
    st.warning(f"""
⚠️ **Inflation Reality Check:**

Your {format_inr(total_wealth)} at age 60 sounds impressive, but after 
{years} years of {inflation}% inflation, it has the purchasing power of 
only **{format_inr(real_corpus)} in today's money**.

That's like having {format_inr(real_corpus)} in your bank account RIGHT NOW. 
Does that feel like enough for 20-25 years of retired life?
    """)

    ai_button(
        "🤖 Is my replacement ratio good enough?",
        f"My replacement ratio is {replacement_ratio:.1f}%. My total retirement wealth is "
        f"{format_inr(total_wealth)} but in today's money it's only {format_inr(real_corpus)}. "
        f"Am I in trouble? What should I do?",
        build_full_context(), "ai_rr", gemini_api_key,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🏗️ TAB 3: HOUSING VS. RETIREMENT TRADE-OFF
# ═══════════════════════════════════════════════════════════════════════════

elif nav == "🏗️ Housing vs. Retirement":

    st.markdown(
        """
        <div class="hero-banner">
            <h1>🏗️ Housing vs. Retirement — The Great Indian Trade-Off</h1>
            <p>Should you buy a house now, or invest first and buy later?<br>
            Let's see what the numbers say.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # User inputs
    hcol1, hcol2 = st.columns(2)
    with hcol1:
        house_price = st.number_input(
            "🏠 Target House Price (₹)", min_value=2000000, max_value=100000000,
            value=15000000, step=500000,
            help="The market price of the house you want to buy.",
        )
        down_payment_pct = st.slider(
            "Down Payment (%)", 10, 30, 20,
            help="Most banks need 10-20% down payment.",
        )
        loan_rate = st.slider(
            "Home Loan Interest Rate (%)", 7.0, 12.0, 8.5, 0.25,
            help="Current SBI home loan rate is ~8.25-8.75%.",
        )
    with hcol2:
        tenure = st.slider(
            "Loan Tenure (Years)", 10, 30, 20,
            help="Longer tenure = lower EMI but much more interest paid.",
        )
        living_expense_pct = st.slider(
            "Monthly Living Expenses (% of Net Pay)", 30, 70, 50,
            help="Rent, food, utilities, transport, lifestyle — everything except savings & EMI.",
        )

    # Calculations
    loan_principal = house_price * (1 - down_payment_pct / 100)
    down_payment_amount = house_price * down_payment_pct / 100
    emi = calculate_emi(loan_principal, loan_rate, tenure)
    total_paid = emi * tenure * 12
    total_interest = total_paid - loan_principal
    living_expenses = net_take_home * living_expense_pct / 100
    safe_emi = 0.30 * net_take_home

    st.session_state["emi_val"] = emi

    st.markdown("---")

    # ── EMI Summary ──────────────────────────────────────────────────────
    st.subheader("📊 EMI & Loan Summary")

    ecol1, ecol2, ecol3, ecol4 = st.columns(4)
    with ecol1:
        st.metric("Monthly EMI", format_inr(emi))
        st.caption(f"On a {format_inr(loan_principal)} loan")
    with ecol2:
        st.metric("Total Interest Paid", format_inr(total_interest),
                  delta=f"{total_interest / loan_principal * 100:.0f}% of loan",
                  delta_color="inverse")
        st.caption("This goes to the bank, not you")
    with ecol3:
        st.metric("Safe EMI Limit (30% rule)", format_inr(safe_emi))
        st.caption("EMI should not exceed 30% of take-home")
    with ecol4:
        if emi > safe_emi:
            st.metric("EMI Status", "⚠️ OVER LIMIT",
                      delta=f"₹{emi - safe_emi:,.0f} over safe limit",
                      delta_color="inverse")
        else:
            st.metric("EMI Status", "✅ Within Limit",
                      delta=f"₹{safe_emi - emi:,.0f} headroom")

    # Interest shock
    total_house_cost = total_paid + down_payment_amount
    st.error(f"""
🤯 **Did You Know?** On a {format_inr(loan_principal)} loan at {loan_rate}% 
for {tenure} years, you'll pay **{format_inr(total_interest)} in interest alone** 
— that's {total_interest / loan_principal * 100:.0f}% MORE than the loan itself!

Your {format_inr(house_price)} house actually costs you 
**{format_inr(total_house_cost)}** in total.
    """)

    st.markdown("---")

    # ── Cash-Flow Waterfall ──────────────────────────────────────────────
    st.subheader("🌊 Monthly Cash-Flow Waterfall")

    retirement_contribution = total_monthly_deduction
    surplus = net_take_home - living_expenses - emi - retirement_contribution
    # for scenario where person hasn't bought a house yet:
    surplus_no_emi = net_take_home - living_expenses - retirement_contribution

    waterfall_labels = [
        "Net Take-Home",
        "Living Expenses",
        "Home Loan EMI",
        "Retirement Savings",
        "Monthly Surplus",
    ]
    waterfall_values = [
        net_take_home,
        -living_expenses,
        -emi,
        -retirement_contribution,
        surplus,
    ]
    waterfall_measures = ["absolute", "relative", "relative", "relative", "total"]
    waterfall_colors = ["#6366f1", "#ef4444", "#f59e0b", "#10b981",
                        "#3b82f6" if surplus >= 0 else "#ef4444"]

    fig_waterfall = go.Figure(go.Waterfall(
        x=waterfall_labels,
        y=waterfall_values,
        measure=waterfall_measures,
        textposition="outside",
        text=[format_inr(abs(v)) for v in waterfall_values],
        connector=dict(line=dict(color="rgba(255,255,255,0.1)")),
        decreasing=dict(marker=dict(color="#ef4444")),
        increasing=dict(marker=dict(color="#10b981")),
        totals=dict(marker=dict(color="#3b82f6" if surplus >= 0 else "#ef4444")),
    ))
    fig_waterfall.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Where Does Your Monthly Pay Go?", font=dict(size=16)),
        yaxis_title="Amount (₹)",
        yaxis=dict(tickformat=","),
        height=420,
        showlegend=False,
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

    if surplus < 0:
        st.error(
            f"🚨 **Negative Cash Flow!** You're short by {format_inr(abs(surplus))}/month. "
            "This EMI is unaffordable with your current salary and retirement commitments."
        )
    elif surplus < net_take_home * 0.05:
        st.warning(
            f"⚠️ Your surplus is only {format_inr(surplus)}/month — dangerously thin. "
            "One unexpected expense could push you into debt."
        )

    st.markdown("---")

    # ── Opportunity Cost ─────────────────────────────────────────────────
    st.subheader("💡 What If You Invested the EMI Instead?")

    opportunity_fv = calculate_opportunity_cost(emi, equity_return, tenure)
    house_appreciation_rate = 4.0
    house_future_value = house_price * (1 + house_appreciation_rate / 100) ** tenure

    fig_opp = go.Figure()
    fig_opp.add_trace(go.Bar(
        x=["🏠 House Value\n(after appreciation)", "📈 Investment Value\n(EMI invested in equity)"],
        y=[house_future_value, opportunity_fv],
        marker_color=["#f59e0b", "#10b981"],
        text=[format_inr(house_future_value), format_inr(opportunity_fv)],
        textposition="outside",
        textfont=dict(size=14, weight="bold"),
        hovertemplate="%{x}: ₹%{y:,.0f}<extra></extra>",
    ))
    fig_opp.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="The Road Not Taken: House vs. Equity", font=dict(size=16)),
        yaxis_title="Value at End of Period (₹)",
        yaxis=dict(tickformat=","),
        height=420,
        showlegend=False,
    )
    st.plotly_chart(fig_opp, use_container_width=True)

    # Comparison table
    house_net_position = house_future_value - total_house_cost
    st.markdown(f"""
### The Opportunity Cost

| What You Got | What You Could Have Had |
|---|---|
| 🏠 House worth **{format_inr(house_future_value)}** after {tenure} years (at {house_appreciation_rate}% appreciation) | 📈 Investment worth **{format_inr(opportunity_fv)}** (at {equity_return}% equity returns) |
| + You paid **{format_inr(total_interest)}** in interest to the bank | + Your money grew tax-efficiently |
| **Net Position: {format_inr(house_net_position)}** | **Net Position: {format_inr(opportunity_fv)}** |
    """)

    st.markdown("---")

    # ── Scenario Comparison ──────────────────────────────────────────────
    st.subheader("⚖️ Buy Now vs. Invest First, Buy Later")

    # Scenario A: Buy now — NPS contribution squeezed to 0
    scenario_a_epf = calculate_epf_corpus(basic_annual, epf_rate, salary_growth, years)
    # Assume NPS contribution drops because EMI eats into disposable income
    scenario_a_nps = calculate_nps_corpus(
        basic_annual, max(nps_pct - 5, 0), max(employer_nps_pct, 0),
        equity_return, salary_growth, years,
    )
    scenario_a_wecare = calculate_wecare_pension(basic_annual, salary_growth, years)
    scenario_a_corpus = (
        scenario_a_epf + scenario_a_nps
        + scenario_a_wecare["commutation_lump_sum"]
        + scenario_a_wecare["pension_wealth_pv"]
    )
    scenario_a_annual_income = (
        scenario_a_wecare["residual_annual_pension"]
        + (scenario_a_epf + scenario_a_nps) * 0.04
    )
    ratio_a = (scenario_a_annual_income / final_annual_salary * 100) if final_annual_salary > 0 else 0

    # Scenario B: Invest for 10 years, buy later
    scenario_b_epf = calculate_epf_corpus(basic_annual, epf_rate, salary_growth, years)
    scenario_b_nps = calculate_nps_corpus(
        basic_annual, nps_pct, employer_nps_pct, equity_return, salary_growth, years,
    )
    scenario_b_wecare = calculate_wecare_pension(basic_annual, salary_growth, years)
    scenario_b_corpus = (
        scenario_b_epf + scenario_b_nps
        + scenario_b_wecare["commutation_lump_sum"]
        + scenario_b_wecare["pension_wealth_pv"]
    )
    scenario_b_annual_income = (
        scenario_b_wecare["residual_annual_pension"]
        + (scenario_b_epf + scenario_b_nps) * 0.04
    )
    ratio_b = (scenario_b_annual_income / final_annual_salary * 100) if final_annual_salary > 0 else 0

    verdict_a = "🟢" if ratio_a >= 50 else ("🟡" if ratio_a >= 40 else "🔴")
    verdict_b = "🟢" if ratio_b >= 50 else ("🟡" if ratio_b >= 40 else "🔴")

    scenario_df = pd.DataFrame({
        "Metric": [
            "Housing",
            "Monthly EMI",
            "Retirement Strategy",
            "Retirement Corpus at 60",
            "Replacement Ratio",
            "Verdict",
        ],
        f"🏠 Scenario A: Buy at {age}": [
            f"Buy at age {age} for {format_inr(house_price)}",
            format_inr(emi),
            "EPF + reduced NPS (EMI eats savings)",
            format_inr(scenario_a_corpus),
            f"{ratio_a:.1f}%",
            verdict_a,
        ],
        f"📈 Scenario B: Invest First": [
            f"Rent for 10 years, buy at {age + 10}",
            "₹0 for 10 years",
            "EPF + NPS + WeCare + full equity",
            format_inr(scenario_b_corpus),
            f"{ratio_b:.1f}%",
            verdict_b,
        ],
    })

    st.dataframe(scenario_df.set_index("Metric"), use_container_width=True)

    st.markdown(f"""
> 🏠 **This doesn't mean "never buy a house."** It means:
> 1. **Delay if you can** — renting is NOT throwing money away; it's buying compounding time
> 2. **Buy within your means** — EMI should NEVER exceed 30% of take-home
> 3. **Never sacrifice retirement** — your NPS/equity SIP is non-negotiable
> 4. **Consider the math** — the {format_inr(max(opportunity_fv - house_future_value, 0))} \
difference between investing and buying is the price of the "homeowner" title
    """)

    ai_button(
        "🤖 Should I buy a house or invest?",
        f"I'm {age} years old, earning {format_inr(salary)}/year. "
        f"I want to buy a house worth {format_inr(house_price)}. "
        f"The EMI would be {format_inr(emi)}/month on a net take-home of {format_inr(net_take_home)}. "
        f"If I invest the EMI instead at {equity_return}%, I'd have {format_inr(opportunity_fv)}. "
        "Should I buy now or invest first? Give me a balanced view.",
        build_full_context(), "ai_housing", gemini_api_key,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 TAB 4: FINANCIAL HEALTH REPORT
# ═══════════════════════════════════════════════════════════════════════════

elif nav == "🎯 Financial Health Report":

    st.markdown(
        """
        <div class="hero-banner">
            <h1>🎯 Your Financial Health Report Card</h1>
            <p>A unified scorecard of your retirement readiness — where you stand, 
            and what to do next.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Compute health score
    user_savings_rate = (total_monthly_deduction / gross_monthly * 100) if gross_monthly > 0 else 0
    emi_ratio_val = st.session_state.get("emi_val", 0) / net_take_home * 100 if net_take_home > 0 else 0

    # Count pillars
    num_pillars = 1  # EPF always present
    if nps_pct > 0 or employer_nps_pct > 0:
        num_pillars += 1
    num_pillars += 1  # WeCare always present in this app

    health_score = calculate_health_score(
        replacement_ratio, user_savings_rate, emi_ratio_val, num_pillars,
    )
    st.session_state["health_score"] = health_score

    # Score display
    if health_score >= 90:
        score_color = "#3b82f6"
        score_label = "Excellent"
        score_desc = "You've cracked the code! 🏆"
    elif health_score >= 75:
        score_color = "#10b981"
        score_label = "Strong"
        score_desc = "You're ahead of most Indians your age 💪"
    elif health_score >= 60:
        score_color = "#f59e0b"
        score_label = "Decent"
        score_desc = "On the right track, keep going 📈"
    elif health_score >= 40:
        score_color = "#f97316"
        score_label = "Needs Improvement"
        score_desc = "You have gaps to close ⚠️"
    else:
        score_color = "#ef4444"
        score_label = "Critical"
        score_desc = "Immediate action required 🚨"

    sc1, sc2 = st.columns([1, 2])
    with sc1:
        st.markdown(
            f"""
            <div class="score-container">
                <div class="score-circle" style="border-color: {score_color}; color: {score_color};">
                    {health_score:.0f}
                    <span style="font-size: 0.9rem; font-weight: 500; opacity: 0.8;">/100</span>
                </div>
                <h3 style="text-align:center; color: {score_color};">{score_label}</h3>
                <p style="text-align:center; opacity:0.7;">{score_desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc2:
        # Score breakdown
        rr_score_raw = min(replacement_ratio / 60 * 100, 100)
        sr_score_raw = min(user_savings_rate / 20 * 100, 100)
        emi_score_raw = max(0, (30 - emi_ratio_val) / 30 * 100) if emi_ratio_val > 0 else 100
        div_map = {0: 0, 1: 33, 2: 67, 3: 100}
        div_score_raw = div_map.get(min(num_pillars, 3), 100)

        breakdown_df = pd.DataFrame({
            "Component": [
                "Replacement Ratio (40%)",
                "Savings Rate (25%)",
                "EMI Affordability (20%)",
                "Diversification (15%)",
            ],
            "Score": [rr_score_raw, sr_score_raw, emi_score_raw, div_score_raw],
            "Your Value": [
                f"{replacement_ratio:.1f}% (target: 60%)",
                f"{user_savings_rate:.1f}% (target: 20%)",
                f"{emi_ratio_val:.1f}% of pay (limit: 30%)" if emi_ratio_val > 0 else "No EMI ✅",
                f"{num_pillars} pillar{'s' if num_pillars > 1 else ''} active",
            ],
        })

        fig_breakdown = go.Figure(go.Bar(
            x=breakdown_df["Score"],
            y=breakdown_df["Component"],
            orientation="h",
            marker=dict(
                color=[
                    "#10b981" if s >= 70 else ("#f59e0b" if s >= 40 else "#ef4444")
                    for s in breakdown_df["Score"]
                ],
            ),
            text=[f"{s:.0f}%" for s in breakdown_df["Score"]],
            textposition="auto",
            hovertemplate="%{y}: %{x:.0f}%<extra></extra>",
        ))
        fig_breakdown.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="Score Breakdown", font=dict(size=16)),
            xaxis=dict(range=[0, 100], title="Score (%)"),
            height=300,
            margin=dict(l=200, r=40, t=60, b=40),
        )
        st.plotly_chart(fig_breakdown, use_container_width=True)

    st.markdown("---")

    # Peer comparison
    st.subheader("👥 How Do You Compare?")

    # Approximate percentile
    if user_savings_rate >= 20:
        percentile = 95
    elif user_savings_rate >= 15:
        percentile = 85
    elif user_savings_rate >= 10:
        percentile = 70
    elif user_savings_rate >= 5:
        percentile = 50
    else:
        percentile = 25

    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        st.metric("Average Indian Your Age Saves", "~5%",
                  help="Source: HSBC Future of Retirement, Max Life-KANTAR surveys")
    with pcol2:
        st.metric("You're Saving", f"{user_savings_rate:.1f}%",
                  delta=f"{user_savings_rate - 5:+.1f}% vs average")
    with pcol3:
        st.metric("Your Percentile Rank", f"Top {100 - percentile}%",
                  help="Approximate ranking among Indian savers your age")

    st.markdown(f"""
Based on published surveys (HSBC Future of Retirement, Max Life-KANTAR):
- **Average Indian your age saves:** ~5% of gross income for retirement
- **You're saving:** {user_savings_rate:.1f}%
- **You're in the top {100 - percentile}% of savers in your age group**
    """)

    st.markdown("---")

    # Key Recommendations
    st.subheader("📋 Key Recommendations")

    recommendations = []
    if replacement_ratio < 50:
        gap = 50 - replacement_ratio
        recommendations.append(
            f"🔴 **Increase retirement contributions.** Your replacement ratio is "
            f"{replacement_ratio:.1f}%, which is {gap:.1f}% below the 50% target. "
            f"Consider increasing NPS contribution by 3-5% of basic."
        )
    if nps_pct == 0 and employer_nps_pct == 0:
        recommendations.append(
            "🟡 **Start NPS immediately.** You're missing out on the extra ₹50,000 "
            "tax deduction under Section 80CCD(1B) AND the power of equity compounding."
        )
    if user_savings_rate < 10:
        recommendations.append(
            "🟡 **Boost your savings rate.** Target at least 15-20% of gross income "
            "for retirement. Automate a monthly SIP so you don't have to decide each month."
        )
    if emi_ratio_val > 30:
        recommendations.append(
            f"🔴 **Your EMI is {emi_ratio_val:.0f}% of take-home** — above the safe 30% limit. "
            "Consider refinancing, extending tenure, or prepaying to reduce the burden."
        )
    if replacement_ratio >= 50:
        recommendations.append(
            "🟢 **You're on track!** Maintain your current strategy. Consider optimizing "
            "tax efficiency by using NPS for the extra ₹50K deduction."
        )
    if years > 20:
        recommendations.append(
            "💡 **Time is your superpower.** With " + str(years) + " years to retirement, "
            "even small increases in contribution will compound massively. "
            "Don't waste this advantage!"
        )

    for rec in recommendations:
        st.markdown(rec)

    st.markdown("---")

    # AI-Powered features
    st.subheader("🤖 AI-Powered Insights")

    aicol1, aicol2 = st.columns(2)
    with aicol1:
        ai_button(
            "🎯 Generate My Personalized Retirement Action Plan",
            "Based on this person's complete financial profile, generate: "
            "1. A 5-step action plan for the next 30 days. "
            "2. Each step should have a specific ₹ amount and product name. "
            "3. Explain WHY each step matters using their own numbers. "
            "4. End with one motivating sentence.",
            build_full_context(), "ai_action_plan", gemini_api_key,
        )
    with aicol2:
        ai_button(
            "✉️ Write a Letter to My 60-Year-Old Self",
            f"Write a short, emotional letter (150 words) from this person's "
            f"current age-{age} self to their 60-year-old retired self, using their "
            f"actual retirement numbers. If their plan is strong (replacement ratio "
            f"{replacement_ratio:.1f}%), make it hopeful. If it's weak, make it a "
            f"gentle wake-up call. Sign it 'Your {age}-year-old self.' Make it personal.",
            build_full_context(), "ai_letter", gemini_api_key,
        )

    st.markdown("---")

    # Downloadable Report
    st.subheader("📄 Download Your Report")

    report_text = f"""
═══════════════════════════════════════════════════════
    FINANCIAL HEALTH REPORT — Retirement Readiness
    Generated by Retirement Planner (Actuarial Edge 2026)
═══════════════════════════════════════════════════════

PERSONAL PROFILE
─────────────────
  Age:                     {age} years
  Years to Retirement:     {years} years (retiring at 60)
  Annual CTC:              {format_inr(salary)}
  Basic Salary:            {format_inr(basic_annual)}/year ({basic_pct}% of CTC)
  Monthly Take-Home (Est): {format_inr(net_take_home)}

ASSUMPTIONS
───────────
  Salary Growth:           {salary_growth}% p.a.
  EPF Rate:                {epf_rate}% p.a.
  Equity/NPS Return:       {equity_return}% p.a.
  Inflation:               {inflation}% p.a.

CONTRIBUTION SUMMARY (Monthly)
──────────────────────────────
  EPF (Employee 12%):      {format_inr(epf_monthly_employee)}
  NPS (Employee {nps_pct}%):      {format_inr(nps_monthly_employee)}
  NPS (Employer {employer_nps_pct}%):     {format_inr(nps_monthly_employer)}
  WeCare DB (10%):         {format_inr(wecare_monthly_contribution)}
  Total Deductions:        {format_inr(total_monthly_deduction)}

RETIREMENT PROJECTION AT AGE 60
────────────────────────────────
  EPF Corpus:              {format_inr(epf_corpus)}
  NPS Corpus:              {format_inr(nps_corpus)}
  WeCare Pension (Monthly):{format_inr(wecare['monthly_pension'])}
  WeCare Commutation Lump: {format_inr(wecare['commutation_lump_sum'])}
  WeCare Residual Pension: {format_inr(wecare['residual_monthly_pension'])}/month
  Total Retirement Wealth: {format_inr(total_wealth)}

REPLACEMENT RATIO
─────────────────
  Annual Retirement Income:{format_inr(annual_retirement_income)}
  Final Annual Salary:     {format_inr(final_annual_salary)}
  Replacement Ratio:       {replacement_ratio:.1f}%
  Target (IFoA/OECD):      50-70%
  Status:                  {"✅ On Track" if replacement_ratio >= 50 else "⚠️ Below Target" if replacement_ratio >= 40 else "❌ Critically Low"}

INFLATION-ADJUSTED REALITY
──────────────────────────
  Nominal Wealth at 60:    {format_inr(total_wealth)}
  Real Wealth (Today's ₹): {format_inr(total_wealth / ((1 + inflation / 100) ** years))}

FINANCIAL HEALTH SCORE
──────────────────────
  Score:                   {health_score:.0f} / 100
  Savings Rate:            {user_savings_rate:.1f}%
  Peer Percentile:         Top {100 - percentile}%

═══════════════════════════════════════════════════════
⚠️ DISCLAIMER: This report is for educational purposes 
only. It does not constitute financial advice. Consult 
a qualified financial advisor for personal decisions.
═══════════════════════════════════════════════════════
"""

    st.download_button(
        "📄 Download Report (.txt)",
        report_text,
        "retirement_report.txt",
        mime="text/plain",
        type="primary",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 💬 TAB 5: AI ASSISTANT (Only if API key present)
# ═══════════════════════════════════════════════════════════════════════════

elif nav == "💬 AI Assistant":

    st.markdown(
        """
        <div class="hero-banner">
            <h1>💬 Your AI Financial Assistant</h1>
            <p>Ask anything about your finances, retirement, or the calculations in this app. 
            I'll explain it like a friend over chai ☕</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Powered by Google Gemini (Free Tier) — Your questions are not stored")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested questions (only show if no history)
    if not st.session_state.chat_history:
        st.markdown("### 💡 Try asking:")
        suggestions = [
            "Should I increase NPS or start mutual fund SIPs?",
            "Is my house affordable on my salary?",
            "How much should I save monthly to retire comfortably?",
            "Explain the WeCare pension plan like I'm 5",
            "What's the one thing I should change TODAY?",
        ]
        suggestion_cols = st.columns(len(suggestions))
        for i, s in enumerate(suggestions):
            with suggestion_cols[i]:
                if st.button(s, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.chat_history.append(
                        {"role": "user", "content": s}
                    )
                    context = build_full_context()
                    with st.spinner("🤖 Thinking..."):
                        response = get_gemini_response(gemini_api_key, s, context)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response}
                    )
                    st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask anything about your finances..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        context = build_full_context()
        with st.spinner("🤖 Thinking..."):
            response = get_gemini_response(gemini_api_key, prompt, context)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )
        with st.chat_message("assistant"):
            st.markdown(response)

    # Clear chat
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


# ---------------------------------------------------------------------------
# ELI5 MODE — Auto-explanations (runs on all pages when enabled)
# ---------------------------------------------------------------------------

if eli5_mode and gemini_api_key and nav not in ["💬 AI Assistant"]:
    st.markdown("---")
    st.markdown(
        "### 🧒 Simple Language Mode — AI Summary",
    )
    with st.spinner("Generating simple explanation..."):
        eli5_prompt = (
            f"I'm on the '{nav}' section of a retirement calculator. "
            f"Summarize what the user should take away in 3 bullet points, "
            f"using extremely simple language (like explaining to a 15-year-old). "
            f"Use their actual numbers."
        )
        eli5_response = get_gemini_response(
            gemini_api_key, eli5_prompt, build_full_context()
        )
    st.info(eli5_response)


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

st.markdown("---")
st.caption(
    "Built for **The Actuarial Edge 2026** (IFoA × Marsh) | Pension Track | "
    "⚠️ This tool is for educational purposes only. It does not constitute "
    "financial advice. Consult a qualified financial advisor for personal decisions."
)
