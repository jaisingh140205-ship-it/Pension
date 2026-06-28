# Pension Track Retirement Calculator

A production-style Streamlit application built for the Pension Track of **The Actuarial Edge 2026** (IFoA × Marsh).

## Overview

This app is a behavioral retirement planning tool designed to help young Indian corporate employees (ages 22–35) understand:

- Why EPF alone is usually not enough for a comfortable retirement
- The cost of delaying investment by 5 or 10 years
- How a multi-pillar strategy (EPF + NPS + employer pension) works
- The housing vs. retirement trade-off for early homebuyers
- Their personal retirement gap and financial health score

The app also includes an optional AI assistant powered by Google Gemini for conversational explanation and personalized guidance.

## Features

### Global Inputs

The sidebar contains all global inputs, including:

- Age
- Annual CTC
- Basic salary percentage
- Salary growth
- Expected equity return
- EPF interest rate
- Inflation rate
- NPS contribution (self and employer)
- Gemini API key input
- Simple language (ELI5) toggle

### App Sections

1. **Home / Welcome**
   - Onboarding wizard for first-time users
   - Shock-value retirement statistics
   - Quick snapshot of estimate and replacement ratio

2. **Savings Vehicles**
   - Side-by-side comparison of EPF, NPS, PPF, and ELSS
   - Cost-of-delay SIP visualization: start now vs. 5 years later vs. 10 years later
   - Quick self-assessment of retirement savings rate

3. **Retirement Calculator**
   - EPF, NPS, and "WeCare" DB pension projection
   - Monthly payslip impact and donut chart
   - Replacement ratio gauge and inflation-adjusted reality check

4. **Housing vs. Retirement**
   - Home loan calculator with EMI, interest shock, and affordability check
   - Opportunity cost comparison: house appreciation vs. investing EMI
   - Scenario analysis for buy now vs. invest first

5. **Financial Health Report**
   - Composite 0-100 health score
   - Peer comparison and recommendations
   - Downloadable detailed retirement report

6. **AI Assistant** (optional)
   - Chat interface for free-form financial questions
   - Suggested prompts for common retirement decisions

## Technical Details

### Libraries Used

- `streamlit`
- `pandas`
- `numpy`
- `plotly`
- `google-generativeai`

### Key App Design Points

- Uses `st.session_state` for persistent state across tabs
- Uses `st.cache_data` for repeated actuarial calculations to improve performance
- Includes graceful AI degradation: the app works fully without a Gemini API key
- Uses Indian rupee formatting with lakhs and crores notation
- Includes step-by-step explainers in expandable panels

## Report Generation

The app generates a detailed retirement report with:

- Personal profile and assumptions
- Monthly contribution breakdown
- Retirement corpus projections
- Replacement ratio analysis
- Inflation-adjusted purchasing power
- A financial health score
- Personalized recommendations

The report downloads as a `.txt` file.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown in the terminal.

## Customization

The app is designed to be easily extended for:

- additional charts and visuals
- custom employer pension formulas
- retirement income replacement targets beyond 60
- tax treatment changes and net-of-tax projections

## Disclaimer

This tool is for educational purposes only. It is not financial advice. Users should consult a qualified financial advisor before making personal retirement decisions.
