CHANNEL_COLORS = {
    "Facebook": "#4267B2",
    "Google": "#DB4437",
    "TikTok": "#25F4EE",
}


def color_for_channel(name: str) -> str:
    return CHANNEL_COLORS.get(name, "#888888")


def apply_theme(name: str) -> str:
    """Apply the light theme with transparent Plotly backgrounds and readable UI.

    Dark theme support removed by request. Always returns light CSS to inject via st.markdown.
    """
    import copy
    import plotly.io as pio
    import plotly.express as px

    # Always use light theme
    theme_name = "Light"

    # Build transparent variants so charts blend with app background
    base_light = pio.templates["plotly_white"] if "plotly_white" in pio.templates else None
    _light = None
    if base_light is not None:
        _light = copy.deepcopy(base_light)
        _light.layout.paper_bgcolor = "rgba(0,0,0,0)"
        _light.layout.plot_bgcolor = "rgba(0,0,0,0)"
        try:
            _light.layout.font.family = "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, 'Apple Color Emoji', 'Segoe UI Emoji'"
            _light.layout.font.color = "#0f172a"
        except Exception:
            pass
        pio.templates["custom_light"] = _light
    # Set Plotly defaults for light theme
    if _light is not None:
        pio.templates.default = "custom_light"
        px.defaults.template = "custom_light"
    text = "#0f172a"          # slate-900
    bg = "#ffffff"            # base background
    bg2 = "#f6f8fb"           # soft panel background (Octave-like)
    bg3 = "#ffffff"
    # Use a gentler, slightly desaturated primary/link blue
    link = "#2b59c3"
    # Light-mode chips: soft style (pale bg, colored text)
    tag_bg = "#eaf2ff"        # pale blue background
    chip_bg = tag_bg
    chip_border = "#cdddfc"
    chip_text = "#2b59c3"

    css = f"""
    <style>
    /* Import modern sans-serif font similar to Octave */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {{
      --oct-text: {text};
      --oct-bg: {bg};
      --oct-bg-2: {bg2};
      --oct-bg-3: {bg3};
      --oct-link: {link};
      --oct-primary: {link};
            --oct-chip-bg: {chip_bg};
            --oct-chip-border: {chip_border};
            --oct-chip-text: {chip_text};
      --oct-card-border: #e2e8f0;
      --oct-card-shadow: 0 1px 2px rgba(16, 24, 40, 0.04), 0 1px 3px rgba(16, 24, 40, 0.06);
      --oct-radius: 12px;
      --oct-radius-sm: 10px;
      --oct-radius-lg: 14px;
    }}

    /* App + Sidebar backgrounds & text */
    [data-testid="stAppViewContainer"] {{ background-color: var(--oct-bg); color: var(--oct-text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, 'Apple Color Emoji', 'Segoe UI Emoji'; }}
    [data-testid="stSidebar"] {{ background-color: var(--oct-bg-2); color: var(--oct-text); }}
    section.main .block-container {{
      padding-top: 2.5rem;
      padding-bottom: 3rem;
      max-width: 1200px;
    }}

        /* Sidebar layout tweaks: reduce top padding and style nav header */
        [data-testid="stSidebar"] > div:first-child {{ padding-top: 8px !important; }}
        [data-testid="stSidebarContent"] {{ padding-top: 8px !important; }}
        .oct-nav-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 4px 8px 2px;
        }}
        .oct-nav-title {{
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #6b7280;
        }}

    /* Text elements */
    h1, h2, h3, h4, h5, h6, p, span, label, li, code, small, strong {{ color: var(--oct-text) !important; }}
    a {{ color: var(--oct-link); }}

    h1 {{ font-weight: 800; letter-spacing: -0.02em; margin: 0.5rem 0 1.25rem; font-size: clamp(32px, 3.4vw, 44px); }}
    h2 {{ font-weight: 700; letter-spacing: -0.01em; margin: 1.25rem 0 0.75rem; font-size: 28px; }}
    h3 {{ font-weight: 600; margin: 0.75rem 0 0.5rem; font-size: 20px; }}
    p, li, label, span {{ font-size: 14.5px; line-height: 1.5; }}

    /* Tables and dataframes */
    .stTable, .stDataFrame {{ background-color: var(--oct-bg-2) !important; color: var(--oct-text) !important; }}
    [data-testid="stTable"], [data-testid="stDataFrame"] {{ background-color: var(--oct-bg-2) !important; color: var(--oct-text) !important; border-radius: var(--oct-radius); box-shadow: var(--oct-card-shadow); }}
    .stTable table, .stDataFrame table, [data-testid="stTable"] table, [data-testid="stDataFrame"] table,
    .stDataFrame tbody, .stDataFrame thead, .stDataFrame td, .stDataFrame th {{
        background-color: var(--oct-bg-2) !important; color: var(--oct-text) !important; border-color: #e2e8f0 !important;
    }}
    .stDataFrame thead th {{ font-weight: 600; position: sticky; top: 0; z-index: 2; background-color: rgba(43, 89, 195, 0.06) !important; }}
    .stDataFrame tbody tr:hover td {{ background-color: rgba(43, 89, 195, 0.05) !important; }}
    .stDataFrame td, .stDataFrame th {{ padding: 12px 10px !important; }}

    /* Inputs */
    input, select, textarea {{ background-color: var(--oct-bg-3) !important; color: var(--oct-text) !important; border-color: #e2e8f0 !important; border-radius: var(--oct-radius-sm) !important; }}
    input::placeholder, textarea::placeholder {{ color: var(--oct-text) !important; opacity: 0.55; }}
    /* Streamlit select/multiselect containers */
    [data-baseweb="select"] > div {{ background-color: var(--oct-bg-3) !important; color: var(--oct-text) !important; border-color: #e2e8f0 !important; border-radius: var(--oct-radius-sm) !important; }}
    [data-baseweb="select"] input {{ color: var(--oct-text) !important; }}
    /* Selected tag chips */
    /* Use higher specificity and target all descendants to override BaseWeb defaults */
    .stMultiSelect [data-baseweb="tag"],
    [data-testid="stSidebar"] [data-baseweb="tag"],
    [data-baseweb="tag"] {{
        background-color: var(--oct-chip-bg) !important;
        color: var(--oct-chip-text) !important;
        border-color: var(--oct-chip-border) !important;
        border-radius: 10px !important;
        margin: 2px 4px !important;
    }}
    .stMultiSelect [data-baseweb="tag"] *,
    [data-testid="stSidebar"] [data-baseweb="tag"] *,
    [data-baseweb="tag"] * {{
        color: var(--oct-chip-text) !important;
        fill: var(--oct-chip-text) !important;
        stroke: var(--oct-chip-text) !important;
    }}
    /* Date input */
    [data-testid="stDateInput"] input {{ background-color: var(--oct-bg-3) !important; color: var(--oct-text) !important; border-color: #e2e8f0 !important; }}
    /* Text/Number input wrappers */
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {{ background-color: var(--oct-bg-3) !important; color: var(--oct-text) !important; }}

        /* Expanders & Header */
        [data-testid="stExpander"] {{ background-color: var(--oct-bg-2); color: var(--oct-text); border-radius: var(--oct-radius); box-shadow: var(--oct-card-shadow); }}
    [data-testid="stHeader"] {{ background: transparent; }}

            /* Buttons */
            button[kind] {{
                /* Default filled style in main content */
                background-color: var(--oct-primary) !important;
                color: #ffffff !important;
                border: 1px solid var(--oct-primary) !important;
                border-radius: 10px !important;
                padding: 10px 14px !important;
                font-weight: 600 !important;
                box-shadow: var(--oct-card-shadow) !important;
                transition: filter .15s ease, transform .06s ease;
            }}
            button[kind]:hover {{ filter: brightness(0.97); }}
            button[kind]:active {{ transform: translateY(1px); }}

            .stDownloadButton > button {{
                background-color: #ffffff !important;
                color: var(--oct-primary) !important;
                border: 1px solid var(--oct-primary) !important;
                border-radius: 10px !important;
                padding: 10px 14px !important;
                font-weight: 600 !important;
                box-shadow: var(--oct-card-shadow) !important;
                transition: background-color .15s ease, color .15s ease, transform .06s ease;
            }}
            .stDownloadButton > button:hover {{
                background-color: rgba(43, 89, 195, 0.06) !important;
            }}
            .stDownloadButton > button:active {{ transform: translateY(1px); }}

            /* Sidebar buttons are outline by default (covers quick ranges and reset) */
            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] button[kind] {{
                background-color: var(--oct-bg) !important;
                color: var(--oct-primary) !important;
                border: 1px solid var(--oct-primary) !important;
                border-radius: 10px !important;
                padding: 8px 12px !important;
                font-weight: 600 !important;
                box-shadow: var(--oct-card-shadow) !important;
            }}
            [data-testid="stSidebar"] .stButton > button:hover,
            [data-testid="stSidebar"] button[kind]:hover {{
                background-color: rgba(43, 89, 195, 0.06) !important;
            }}
            [data-testid="stSidebar"] .stButton > button:active,
            [data-testid="stSidebar"] button[kind]:active {{
                transform: translateY(1px);
            }}

                    /* Header Deploy button (Streamlit Cloud) to softer outline */
                    [data-testid="stToolbar"] button {{
                    background-color: #ffffff !important;
                    color: var(--oct-primary) !important;
                    border: 1px solid var(--oct-primary) !important;
                    border-radius: 10px !important;
                    box-shadow: var(--oct-card-shadow) !important;
                }}
                    [data-testid="stToolbar"] button:hover {{ background-color: rgba(43, 89, 195, 0.06) !important; }}

            /* Focus visibility for accessibility */
            input:focus-visible, select:focus-visible, textarea:focus-visible,
            [data-baseweb="select"] > div:focus-within, button:focus-visible {{
                outline: 2px solid rgba(43, 89, 195, 0.45) !important;
                outline-offset: 1px !important;
                box-shadow: 0 0 0 2px rgba(43, 89, 195, 0.08) !important;
            }}

        /* Metric cards */
            [data-testid="stMetric"] {{
                background: var(--oct-bg-2);
                border: 1px solid var(--oct-card-border);
                border-radius: var(--oct-radius);
                padding: 14px 16px;
                box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
            }}
            [data-testid="stMetricLabel"] {{ font-size: 12px; font-weight: 500; opacity: 0.85; }}
            [data-testid="stMetricValue"] {{ font-size: 26px; font-weight: 700; letter-spacing: -0.015em; }}

            /* Sidebar heading style */
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
                text-transform: uppercase;
                font-size: 12px !important;
                letter-spacing: 0.08em;
                color: #6b7280 !important;
                margin-top: 1rem;
                margin-bottom: 0.5rem;
            }}
    </style>
    """
    return css
