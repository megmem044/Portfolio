"""Shared Streamlit styling for AnswerTrust workspace pages."""

import streamlit as st


def apply_workspace_theme() -> None:
    """Apply the common AnswerTrust workspace and sidebar theme."""
    st.markdown(
        """
        <style>
            :root { --ink:#2c2c34; --coral:#ff7d59; --pink:#ffbde8;
                --periwinkle:#9980ed; --olive:#d1d161; --sky:#cddbf9;
                --paper:#fffdf8; --muted:#62616e; }
            .stApp { background:var(--sky)!important; background-image:none!important; }
            [data-testid="stHeader"] { background:rgba(205,219,249,.94)!important; }
            [data-testid="stHeader"]::before { background:var(--coral)!important;
                content:""; height:4px; left:0; position:fixed; right:0; top:0; z-index:999; }
            [data-testid="stSidebar"] { background:var(--ink)!important; border-right:0!important; }
            [data-testid="stSidebar"] > div, [data-testid="stSidebarNav"] {
                background:var(--ink)!important; box-shadow:none!important; }
            [data-testid="stSidebarNav"]::before { background:transparent!important;
                color:var(--paper)!important; content:"AnswerTrust"!important;
                display:block!important; font-family:Georgia,"Times New Roman",serif!important;
                font-size:2rem!important; font-weight:700!important;
                letter-spacing:-.04em!important; line-height:1!important;
                padding:2.1rem 1.5rem .55rem!important; }
            [data-testid="stSidebarNav"]::after { display:none!important; }
            [data-testid="stSidebarNav"] ul { margin-top:0!important; padding-top:0!important; }
            [data-testid="stSidebar"] * { color:var(--paper)!important;
                filter:none!important; text-shadow:none!important; }
            [data-testid="stSidebarNav"] a { border-radius:9px!important; }
            [data-testid="stSidebarNav"] a[aria-current="page"] {
                background:var(--coral)!important; }
            [data-testid="stSidebarNav"] a:hover { background:#44434d!important; }
            .block-container { max-width:1120px; padding-top:2.25rem; padding-bottom:4rem; }
            h1,h2,h3 { color:var(--ink)!important; }
            h1 { font-family:Georgia,"Times New Roman",serif!important;
                letter-spacing:-.045em!important; }
            .main p,.main label { color:var(--muted); }
            div[data-testid="stExpander"], div[data-testid="stMetric"] {
                background:var(--paper)!important; border:1px solid #b9bfd0!important;
                border-radius:12px!important; box-shadow:none!important; }
            div[data-testid="stAlert"] { border-radius:10px!important; }
            div[data-testid="stDataFrame"] { background:var(--paper);
                border:1px solid #b9bfd0; border-radius:12px; overflow:hidden; }
            .stButton button { border-radius:10px; font-weight:700; }
        </style>
        """,
        unsafe_allow_html=True,
    )
