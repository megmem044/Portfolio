"""Shared presentation helpers for the AnswerTrust Streamlit interface."""
from __future__ import annotations
from html import escape
import streamlit as st

DECISION_TONES = {
    "PUBLISH": ("#3c6484", "#d0d9f5", "Ready to publish"),
    "REVIEW": ("#5b6418", "#e7f1ab", "Human review required"),
    "REJECT": ("#333333", "#dedbd5", "Do not publish"),
}


def apply_theme() -> None:
    """Apply the editorial AnswerTrust design system."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
    :root{--ivory:#fffdf5;--lemon:#e7f1ab;--lavender:#d0d9f5;--sky:#95b1ee;
      --midnight:#3c6484;--charcoal:#333333;--gray700:#444340;--gray500:#85847f;
      --gray300:#dedbd5;--gray100:#f1efe9;--surface:#faf8f1;}
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--charcoal)}
    .stApp{background-color:var(--ivory);background-image:linear-gradient(rgba(51,51,51,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(51,51,51,.035) 1px,transparent 1px);background-size:44px 44px}
    [data-testid="stHeader"]{background:rgba(255,253,245,.92);border-bottom:1px solid var(--gray300)}
    [data-testid="stSidebar"]{background:var(--charcoal);border-right:1px solid #171717}
    [data-testid="stSidebar"] *{color:var(--ivory)!important}
    [data-testid="stSidebarNav"]::before{content:"AnswerTrust";display:block;font-family:'Instrument Serif',serif;font-size:2rem;padding:1.8rem 1.25rem .75rem;color:var(--ivory)}
    [data-testid="stSidebarNav"]{padding-top:0!important}
    [data-testid="stSidebarNav"] ul{gap:.34rem!important;margin-top:.2rem!important;padding-top:0!important}
    [data-testid="stSidebarNav"] li{margin:0!important;padding:0!important}
    [data-testid="stSidebarNav"] a{border:1px solid transparent;border-radius:4px;margin:0 .65rem!important;min-height:2.65rem;padding:.48rem .75rem!important;transition:transform .12s ease,box-shadow .12s ease}
    [data-testid="stSidebarNav"] li a{background:var(--gray100)!important}
    [data-testid="stSidebarNav"] li a *{color:var(--charcoal)!important;font-weight:700!important}
    [data-testid="stSidebarNav"] a:hover{background:var(--ivory)!important;border-color:var(--sky);transform:translate(-2px,-2px);box-shadow:3px 3px 0 #111}
    [data-testid="stSidebarNav"] a[aria-current="page"]{background:var(--midnight)!important;border-color:var(--ivory)!important;box-shadow:3px 3px 0 #111}
    [data-testid="stSidebarNav"] a[aria-current="page"] *{color:var(--ivory)!important}
    .block-container{max-width:1180px;padding-top:2rem;padding-bottom:5rem}
    h1,h2,h3{color:var(--charcoal)!important;letter-spacing:-.025em}
    h1{font-family:'Instrument Serif',serif!important;font-weight:400!important}
    h2,h3{font-family:'DM Sans',sans-serif!important;font-weight:700!important}
    .at-hero{background:rgba(255,253,245,.94);border:1px solid var(--charcoal);border-radius:4px;color:var(--charcoal);padding:2.25rem 2.35rem;margin-bottom:1.5rem;box-shadow:8px 8px 0 var(--gray300);position:relative;overflow:hidden}
    .at-hero:after{content:"";position:absolute;background:var(--gray300);height:100%;width:14px;right:0;top:0;border-left:1px solid var(--charcoal)}
    .at-hero--lemon{background:linear-gradient(110deg,var(--ivory),#f7facf);box-shadow:8px 8px 0 var(--lemon)}
    .at-hero--lemon:after{background:var(--lemon)}
    .at-hero--lavender{background:linear-gradient(110deg,var(--ivory),#e8ecfb);box-shadow:8px 8px 0 var(--lavender)}
    .at-hero--lavender:after{background:var(--lavender)}
    .at-hero--sky{background:linear-gradient(110deg,var(--ivory),#dce6fa);box-shadow:8px 8px 0 var(--sky)}
    .at-hero--sky:after{background:var(--sky)}
    .at-kicker{color:var(--midnight);font-size:.72rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase}
    .at-hero h1{font-size:clamp(2.35rem,4.6vw,4.1rem);line-height:1;margin:.55rem 0 .8rem;max-width:850px}
    .at-hero p{color:var(--gray700);font-size:1rem;line-height:1.7;max-width:740px;margin:0}
    .at-step{display:inline-flex;align-items:center;justify-content:center;width:1.55rem;height:1.55rem;border:1px solid var(--charcoal);border-radius:50%;background:var(--lemon);font-size:.72rem;font-weight:700;margin-right:.45rem}
    .at-section-title{color:var(--charcoal);font-size:.83rem;font-weight:700;letter-spacing:.02em;margin:.1rem 0 .8rem}
    .at-verdict{border:1px solid var(--charcoal);border-radius:4px;padding:1.45rem 1.6rem;margin:1.5rem 0 1rem;background:var(--ivory);box-shadow:6px 6px 0 var(--sky)}
    .at-verdict-row{align-items:center;display:flex;gap:.9rem;flex-wrap:wrap}
    .at-pill{border:1px solid currentColor;border-radius:999px;display:inline-flex;font-size:.7rem;font-weight:700;letter-spacing:.1em;padding:.4rem .7rem;text-transform:uppercase}
    .at-score{color:var(--charcoal);font-family:'Instrument Serif',serif;font-size:2.5rem}
    .at-muted{color:var(--gray500);font-size:.85rem}
    .at-claim{color:var(--charcoal);font-family:'Instrument Serif',serif;font-size:1.55rem;line-height:1.4}
    .at-evidence{background:var(--page-soft,var(--lavender));border:1px solid var(--page-primary,var(--midnight));border-radius:4px;color:var(--charcoal);margin:.6rem 0;padding:.9rem 1rem}
    .at-evidence-meta{color:var(--page-primary,var(--midnight));font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.3rem}
    div[data-testid="stForm"],div[data-testid="stExpander"],div[data-testid="stMetric"]{background:rgba(255,253,245,.96);border:1px solid var(--gray300)!important;border-radius:4px!important;box-shadow:4px 4px 0 rgba(51,51,51,.09)}
    div[data-testid="stForm"]{padding:1.35rem 1.45rem}
    div[data-testid="stMetric"]{padding:1rem 1.1rem}
    .stTextInput input,.stTextArea textarea{background:var(--ivory)!important;border:1px solid var(--gray300)!important;border-radius:4px!important}
    .stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--page-primary,var(--midnight))!important;box-shadow:0 0 0 3px var(--page-focus,rgba(149,177,238,.4))!important}
    .stButton button,.stFormSubmitButton button{border-radius:4px!important;min-height:2.75rem;font-weight:700!important;transition:transform .12s ease,box-shadow .12s ease}
    .stFormSubmitButton button,[data-testid="baseButton-primary"]{background:var(--page-primary,var(--midnight))!important;border:1px solid var(--charcoal)!important;color:var(--page-button-text,var(--ivory))!important}
    [data-testid="baseButton-secondary"]{background:var(--page-soft,var(--lavender))!important;border:1px solid var(--charcoal)!important;color:var(--charcoal)!important}
    [data-testid="baseButton-secondary"]:hover{background:var(--page-accent,var(--lemon))!important;color:var(--charcoal)!important}
    div[data-testid="stMetric"]{border-top:5px solid var(--page-accent,var(--lavender))!important}
    .stButton button:hover,.stFormSubmitButton button:hover{transform:translate(-2px,-2px);box-shadow:3px 3px 0 var(--charcoal)}
    div[data-testid="stAlert"]{border-radius:4px}.stDataFrame{border:1px solid var(--gray300);border-radius:4px;overflow:hidden}
    hr{border-color:var(--charcoal)!important;opacity:.45}
    @media(max-width:700px){.block-container{padding:1rem}.at-hero{padding:1.55rem}.at-hero h1{font-size:2.25rem}.at-score{font-size:2rem}}
    </style>""",unsafe_allow_html=True)


def hero(kicker: str,title: str,description: str,tone: str="lemon")->None:
    safe_tone = tone if tone in {"lemon", "lavender", "sky"} else "lemon"
    themes = {
        "lemon": {
            "background": "#fffdf5",
            "wash": "rgba(231,241,171,.72)",
            "primary": "#3c6484",
            "accent": "#e7f1ab",
            "soft": "#f4f8cf",
            "focus": "rgba(231,241,171,.58)",
            "button_text": "#fffdf5",
        },
        "lavender": {
            "background": "#f4f6fc",
            "wash": "rgba(208,217,245,.86)",
            "primary": "#3c6484",
            "accent": "#d0d9f5",
            "soft": "#e7ecfa",
            "focus": "rgba(208,217,245,.72)",
            "button_text": "#fffdf5",
        },
        "sky": {
            "background": "#eef3fc",
            "wash": "rgba(149,177,238,.58)",
            "primary": "#333333",
            "accent": "#95b1ee",
            "soft": "#dce6fa",
            "focus": "rgba(149,177,238,.62)",
            "button_text": "#fffdf5",
        },
    }
    theme = themes[safe_tone]
    st.markdown(
        f"""<style>
        :root{{--page-primary:{theme['primary']};--page-accent:{theme['accent']};
          --page-soft:{theme['soft']};--page-focus:{theme['focus']};
          --page-button-text:{theme['button_text']};}}
        .stApp{{background-color:{theme['background']};background-image:
          radial-gradient(circle at 88% 2%,{theme['wash']} 0,transparent 28rem),
          linear-gradient(rgba(51,51,51,.035) 1px,transparent 1px),
          linear-gradient(90deg,rgba(51,51,51,.035) 1px,transparent 1px);
          background-size:auto,44px 44px,44px 44px;}}
        div[data-testid="stForm"],div[data-testid="stExpander"],div[data-testid="stMetric"]
          {{background:rgba(255,253,245,.88);}}
        </style>""",
        unsafe_allow_html=True,
    )
    st.markdown(f'<section class="at-hero at-hero--{safe_tone}"><div class="at-kicker">{escape(kicker)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></section>',unsafe_allow_html=True)


def verdict(decision: str,score: int,action: str,metadata: str)->None:
    color,background,label=DECISION_TONES[decision]
    st.markdown(f'<section class="at-verdict"><div class="at-verdict-row"><span class="at-pill" style="color:{color};background:{background}">{escape(decision)}</span><span class="at-score">{score}/100</span><span class="at-muted">{escape(label)}</span></div><p>{escape(action)}</p><div class="at-muted">{escape(metadata)}</div></section>',unsafe_allow_html=True)


def evidence_block(section: str,similarity: float,passage: str)->None:
    st.markdown(f'<div class="at-evidence"><div class="at-evidence-meta">{escape(section)} &middot; {similarity:.0%} semantic match</div><div>{escape(passage)}</div></div>',unsafe_allow_html=True)
