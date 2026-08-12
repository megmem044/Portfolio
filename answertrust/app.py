"""AnswerTrust landing page."""

import streamlit as st


st.set_page_config(
    page_title="AnswerTrust",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        :root {
            --ink: #2c2c34;
            --coral: #ff7d59;
            --pink: #ffbde8;
            --periwinkle: #9980ed;
            --olive: #d1d161;
            --paper: #fffdf8;
            --muted: #62616e;
        }
        .stApp { background: #cddbf9; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stHeader"] { background: transparent; }
        .block-container {
            align-items: center; display: flex; justify-content: center;
            max-width: 1040px; min-height: 94vh; padding: 2rem;
        }
        .main [data-testid="stVerticalBlock"] {
            align-items: center; display: flex; width: 100%;
        }
        .landing-card {
            animation: card-in .55s cubic-bezier(.2,.8,.2,1) both;
            background: var(--paper); border: 2px solid var(--ink);
            border-radius: 28px; box-shadow: 12px 12px 0 var(--periwinkle);
            margin: 0 auto; max-width: 780px; overflow: hidden;
            padding: clamp(3.5rem, 7vw, 6rem) clamp(2rem, 7vw, 6rem) 7rem;
            position: relative; text-align: center;
        }
        .landing-card::before, .landing-card::after {
            border-radius: 50%; content: ""; position: absolute;
        }
        .landing-card::before {
            background: var(--pink); height: 105px; left: -48px; top: -46px;
            width: 105px;
        }
        .landing-card::after {
            background: var(--olive); bottom: -36px; height: 88px;
            right: -32px; width: 88px;
        }
        .landing-card h1 {
            color: var(--ink); font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(3.7rem, 8vw, 6.5rem); font-weight: 700;
            letter-spacing: -.065em; line-height: .95; margin: 0 0 1.8rem;
        }
        .landing-card p {
            color: var(--muted); font-size: clamp(1.05rem, 2vw, 1.3rem);
            line-height: 1.65; margin: 0 auto; max-width: 590px;
        }
        div[data-testid="stButton"] {
            display: flex; justify-content: center; margin: -5.1rem auto 0;
            position: relative; width: 100%; z-index: 5;
        }
        div[data-testid="stButton"] button {
            background: var(--coral); border: 2px solid var(--coral);
            border-radius: 12px; box-shadow: 5px 5px 0 var(--ink);
            color: #fff; font-weight: 750; min-height: 3.2rem;
            min-width: 220px; transition: transform .18s ease,
            box-shadow .18s ease, background .18s ease;
        }
        div[data-testid="stButton"] button:hover {
            background: var(--periwinkle); border-color: var(--periwinkle);
            box-shadow: 2px 2px 0 var(--ink); color: #fff;
            transform: translate(3px, 3px);
        }
        @keyframes card-in {
            from { opacity: 0; transform: translateY(18px) scale(.985); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation: none !important; transition: none !important; }
        }
        @media (max-width: 640px) {
            .block-container { padding: 1.25rem; }
            .landing-card { border-radius: 22px; padding-bottom: 7rem; }
            .landing-card h1 { font-size: 3.7rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <main class="landing-card">
        <h1>AnswerTrust</h1>
        <p>
            AnswerTrust checks a generated answer against the evidence you
            trust, so you know when it is ready.
        </p>
    </main>
    """,
    unsafe_allow_html=True,
)

if st.button("Start an evaluation", type="primary"):
    st.switch_page("pages/1_New_Evaluation.py")
