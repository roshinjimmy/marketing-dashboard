CHANNEL_COLORS = {
    "Facebook": "#4267B2",
    "Google": "#DB4437",
    "TikTok": "#25F4EE",
}


def color_for_channel(name: str) -> str:
    return CHANNEL_COLORS.get(name, "#888888")


def apply_theme(name: str) -> str:
    # Add a flex row class for horizontal layout
    flex_row_css = """
.oct-flex-row {
    display: flex;
    flex-direction: row;
    gap: 2.5rem;
    align-items: flex-start;
    margin-bottom: 2.5rem;
}
@media (max-width: 900px) {
    .oct-flex-row {
        flex-direction: column;
        gap: 1.5rem;
    }
}
"""
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
    text = "#1D1D1F"          # Apple's dark text - nearly black but not quite
    bg = "#FFFFFF"            # Apple's clean white background
    bg2 = "#F5F5F7"           # Apple's subtle light gray for secondary backgrounds
    bg3 = "#FFFFFF"           # Input background (white)
    link = "#0066CC"          # Apple's blue accent color
    tag_bg = "#E8F0FE"
    chip_bg = tag_bg
    chip_border = "#D2E3FC"
    chip_text = "#0066CC"     # Apple's blue accent color
    css = f"""
<style>
/* No need for external fonts, using Apple system fonts */
:root {{
    --oct-text: {text};
    --oct-bg: {bg};
    --oct-bg-2: {bg2};
    --oct-bg-3: {bg3};
    --oct-link: {link};
    --oct-primary: {link};
    --oct-chip-bg: {chip_bg};
    --oct-chip-border: {chip_border};
    --oct-card-border: rgba(0, 0, 0, 0.1);
    --oct-card-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    --oct-radius: 12px;
    --oct-radius-sm: 8px;
    --oct-radius-lg: 20px;
}}

/* App backgrounds & text - Apple style */
[data-testid="stAppViewContainer"] {{ background-color: var(--oct-bg); color: var(--oct-text); font-family: -apple-system, SF Pro Text, SF Pro Icons, Helvetica Neue, Helvetica, Arial, sans-serif; }}
[data-testid="stSidebar"] {{ background-color: var(--oct-bg-2); color: var(--oct-text); }}
/* Reduce spacing in sidebar */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
/* Remove extra padding from elements */
[data-testid="stSidebar"] > div > div:first-child {{ padding-top: 1.5rem !important; }}
section.main .block-container {{
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}}
    h1, h2, h3, h4, h5, h6, p, span, label, li, code, small, strong {{ color: var(--oct-text) !important; }}
    a {{ color: var(--oct-link); text-decoration: none; font-weight: 400; }}
    a:hover {{ text-decoration: none; opacity: 0.8; }}
    h1 {{ font-weight: 600; letter-spacing: -0.02em; margin: 0.5rem 0 1rem; font-size: clamp(40px, 5vw, 56px); }}
    h2 {{ font-weight: 500; letter-spacing: -0.01em; margin: 1.5rem 0 1rem; font-size: 32px; }}
    h3 {{ font-weight: 500; margin: 1rem 0 0.75rem; font-size: 24px; }}
    p, li, label, span {{ font-size: 17px; line-height: 1.5; }}
    code, small, strong {{ font-size: 15px; }}
/* Tables and dataframes */
.stTable, .stDataFrame {{ background-color: var(--oct-bg-2) !important; color: var(--oct-text) !important; }}
[data-testid="stTable"], [data-testid="stDataFrame"] {{ background-color: var(--oct-bg-2) !important; color: var(--oct-text) !important; border-radius: var(--oct-radius); box-shadow: var(--oct-card-shadow); }}
.stTable table, .stDataFrame table, [data-testid="stTable"] table, [data-testid="stDataFrame"] table,
.stDataFrame tbody, .stDataFrame thead, .stDataFrame td, .stDataFrame th {{
    background-color: var(--oct-bg-2) !important; color: var(--oct-text) !important; border-color: #e2e8f0 !important;
}}
.stDataFrame thead th {{ font-weight: 600; position: sticky; top: 0; z-index: 2; background-color: rgba(43, 89, 195, 0.06) !important; }}
.stDataFrame tbody tr:hover td {{ background-color: rgba(43, 89, 195, 0.05) !important; }}
    .stDataFrame td, .stDataFrame th {{ padding: 14px 14px !important; font-size: 15px !important; }}
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
[data-testid="stExpander"] {{ 
    background-color: var(--oct-bg-2); 
    color: var(--oct-text); 
    border-radius: var(--oct-radius); 
    box-shadow: var(--oct-card-shadow);
}}

/* Style expander buttons to match Apple design */
[data-testid="stExpander"] > div:first-child {{
    border-radius: var(--oct-radius);
}}

[data-testid="stExpander"] > div > div > div[role="button"] {{
    transition: all 0.2s ease-in-out !important;
}}

[data-testid="stExpander"] > div > div > div[role="button"]:hover {{
    background-color: rgba(0, 102, 204, 0.05) !important;
}}

[data-testid="stExpander"] > div > div > div[role="button"] svg {{
    color: var(--oct-primary) !important;
    height: 20px !important;
    width: 20px !important;
}}

/* Increase font size for expander headings */
[data-testid="stExpander"] > div > div > div[role="button"] p {{
    font-size: 18px !important;
    font-weight: 500 !important;
    letter-spacing: -0.01em !important;
}}
[data-testid="stHeader"] {{ background: transparent; }}
    /* Buttons - Apple style */
    button[kind],
    .stButton > button {{
        background-color: var(--oct-primary) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 980px !important; /* Apple's pill-shaped buttons */
        padding: 8px 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        transition: background-color .15s ease, opacity .15s ease;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        line-height: 1.5 !important;
    }}
    button[kind]:hover,
    .stButton > button:hover {{
        filter: none;
        background-color: #004DA6 !important;
        opacity: 0.9;
    }}
    button[kind]:active,
    .stButton > button:active {{ opacity: 0.8; transform: translateY(1px); }}
    
    /* Fix for any child elements within buttons to ensure proper text color */
    button[kind] *,
    .stButton > button * {{
        color: #fff !important;
    }}
    .stDownloadButton > button {{
        background-color: var(--oct-primary) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 980px !important; /* Apple's pill-shaped buttons */
        padding: 8px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        transition: background-color .15s ease, opacity .15s ease, transform .06s ease;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: #004DA6 !important;
        opacity: 0.9;
    }}
    .stDownloadButton > button:active {{ opacity: 0.8; transform: translateY(1px); }}
    
    /* Fix for any child elements within download buttons */
    .stDownloadButton > button * {{
        color: #fff !important;
    }}
    /* Sidebar buttons use filled style by default (covers quick ranges) */
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] button[kind] {{
        background-color: var(--oct-primary) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 980px !important; /* Apple's pill-shaped buttons */
        padding: 6px 12px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        transition: all 0.2s ease-in-out !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 60px !important;
        max-height: 30px !important; /* Keep buttons compact */
        line-height: 1.2 !important;
        margin: 2px !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] button[kind]:hover {{
        background-color: #004DA6 !important;
        opacity: 0.9;
        transform: translateY(-1px) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button:active,
    [data-testid="stSidebar"] button[kind]:active {{ 
        transform: translateY(0px) !important;
        box-shadow: none !important;
        opacity: 0.8 !important;
    }}
    
    /* Make sure text within sidebar buttons has correct color */
    [data-testid="stSidebar"] .stButton > button *,
    [data-testid="stSidebar"] button[kind] * {{
        color: #fff !important;
        font-size: 13px !important;
    }}
    /* Make Reset filters button larger than other buttons */
    #reset-filters .stButton > button,
    [data-testid="stSidebar"] #reset-filters .stButton > button {{
        padding: 8px 16px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        max-height: none !important;
        width: 75% !important; /* Keep the width consistent with previous styling */
        min-height: 36px !important; /* Ensure button height is sufficient for larger text */
    }}
    
    #reset-filters .stButton > button *,
    [data-testid="stSidebar"] #reset-filters .stButton > button * {{
        font-size: 16px !important;
        font-weight: 600 !important;
    }}
/* Header Deploy button (Streamlit Cloud) - Apple style */
[data-testid="stToolbar"] button,
div[data-testid="stDecoration"] button {{
    background-color: var(--oct-primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 980px !important; /* Apple's pill-shaped buttons */
    padding: 8px 20px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transition: background-color .15s ease, opacity .15s ease;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: 80px !important;
}}

[data-testid="stToolbar"] button:hover,
div[data-testid="stDecoration"] button:hover {{
    filter: none;
    background-color: #004DA6 !important;
    opacity: 0.9;
}}

[data-testid="stToolbar"] button:active,
div[data-testid="stDecoration"] button:active {{ opacity: 0.8; }}

/* Fix for any child elements within buttons to ensure proper text color */
[data-testid="stToolbar"] button *,
div[data-testid="stDecoration"] button * {{
    color: #fff !important;
}}
/* Consistent styling for all baseButton elements */
[data-testid="baseButton-primary"],
[data-testid="baseButton-secondary"] {{
    background-color: var(--oct-primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 980px !important; /* Apple's pill-shaped buttons */
    padding: 8px 20px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transition: background-color .15s ease, opacity .15s ease, transform .06s ease;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: 80px !important;
    line-height: 1.5 !important;
}}

[data-testid="baseButton-primary"]:hover,
[data-testid="baseButton-secondary"]:hover {{
    background-color: #004DA6 !important;
    opacity: 0.9;
}}

[data-testid="baseButton-primary"]:active,
[data-testid="baseButton-secondary"]:active {{
    opacity: 0.8;
    transform: translateY(1px);
}}

/* Make sure text within buttons has correct color */
[data-testid="baseButton-primary"] div,
[data-testid="baseButton-secondary"] div,
[data-testid="baseButton-primary"] span,
[data-testid="baseButton-secondary"] span {{
    color: #fff !important;
}}

/* Additional button overrides for special cases */
button[data-testid^="InputButton"],
button[data-testid^="StyledFullScreenButton"] {{
    background-color: var(--oct-primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 980px !important;
    font-weight: 500 !important;
    transition: background-color .15s ease, opacity .15s ease;
}}

/* Style for any standard buttons not caught by other selectors */
button:not([class*="st"]):not([data-testid]):not([kind]) {{
    background-color: var(--oct-primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 980px !important;
    padding: 8px 16px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: background-color .15s ease, opacity .15s ease;
}}

/* Focus visibility for accessibility */
input:focus-visible, select:focus-visible, textarea:focus-visible,
[data-baseweb="select"] > div:focus-within, button:focus-visible {{
    outline: 2px solid rgba(43, 89, 195, 0.45) !important;
    outline-offset: 1px !important;
    box-shadow: 0 0 0 2px rgba(43, 89, 195, 0.08) !important;
}}
/* Metric cards - Apple style */
[data-testid="stMetric"] {{
    background: var(--oct-bg);
    border: none;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    margin-bottom: 1rem;
}}
    [data-testid="stMetricLabel"] {{ font-size: 14px; font-weight: 400; opacity: 0.8; }}
    [data-testid="stMetricValue"] {{ font-size: 32px; font-weight: 600; letter-spacing: -0.02em; }}
/* Sidebar heading style - Apple style */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        text-transform: none;
        font-size: 17px !important;
        letter-spacing: -0.01em;
        font-weight: 500 !important;
        color: #1d1d1f !important;
        margin-top: 1.2rem;
        margin-bottom: 0.7rem;
    }}
    
/* Section headers with Apple-inspired styling */
.oct-section-header {{
    background: transparent;
    padding: 6px 0 4px;
    margin-bottom: 5px;
}}

.oct-section-title {{
    font-size: 17px !important;
    font-weight: 600 !important;
    color: #1d1d1f !important;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}}

/* Navigation section styling */
.oct-nav-section {{
    margin-top: 5px;
}}

/* Filter section styling */
.oct-filter-section {{
    margin-top: 4px;
    margin-bottom: 0;
    padding-bottom: 4px;
}}

/* Section divider styling - Apple-inspired subtle separator */
.oct-section-divider {{
    height: 1px;
    background: rgba(0,0,0,0.1);
    margin: 10px 0;
    width: 100%;
}}

/* Filter group divider - more subtle than section divider */
.oct-filter-divider {{
    height: 1px;
    background: rgba(0,0,0,0.05);
    margin: 6px 0;
    width: 100%;
}}

/* Date range group styling */
.oct-date-range-group {{
    margin: 0;
    padding: 0 0 4px 0;
}}

.date-range-title h4 {{
    margin: 4px 0 2px !important;
    font-size: 13px !important;
    letter-spacing: 0.02em;
    color: #86868b !important;
    font-weight: 500 !important;
    text-transform: none;
}}

/* Quick ranges and date input styling */
#quick-ranges {{
    margin-top: 8px;
    margin-bottom: 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: flex-start;
}}

/* Custom styling for the quick range buttons to make them more Apple-like */
#quick-ranges .stButton > button {{
    min-width: calc(33% - 8px) !important;
    flex-grow: 1;
    margin: 0 !important;
    padding: 5px 8px !important;
    text-align: center !important;
    white-space: nowrap !important;
}}

/* Ensure the quick range buttons use the primary color and white text */
#quick-ranges .stButton > button {{
    background-color: var(--oct-primary) !important;
    color: #fff !important;
}}

#quick-ranges .stButton > button:hover {{
    background-color: #004DA6 !important;
}}

/* Make date input more compact */
[data-testid="stDateInput"] {{
    margin-top: 2px !important;
    margin-bottom: 8px !important;
}}
/* Ultra-dense checkbox groups in sidebar - Apple style */
.oct-filter-group {{ margin-bottom: 4px; margin-top: 0; }}
.oct-filter-group h4 {{ margin: 4px 0 2px !important; font-size: 13px !important; letter-spacing: 0.02em; color: #86868b !important; font-weight: 500 !important; text-transform: none; }}
/* Streamlit checkbox rows */
[data-testid="stSidebar"] .oct-filter-group [data-testid="stCheckbox"] {{ margin: 0 0 0 0 !important; padding-top: 1px !important; padding-bottom: 1px !important; }}
[data-testid="stSidebar"] .oct-filter-group label p {{ margin: 0 !important; font-size: 14px !important; line-height: 1.0 !important; }}
/* Reduce gap between checkbox icon and label */
[data-testid="stSidebar"] .oct-filter-group [data-testid="stCheckbox"] label {{ gap: 4px !important; align-items: center; padding: 0 !important; }}
/* Slightly smaller checkbox control */
[data-testid="stSidebar"] .oct-filter-group input[type="checkbox"] {{ width: 14px; height: 14px; }}
/* Remove extra padding from checkboxes */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div > [data-testid="stCheckbox"] {{ padding-top: 1px !important; padding-bottom: 1px !important; }}

/* Reset filters button styling - Apple blue pill button */
#reset-filters {{
    display: flex;
    justify-content: center;
    margin-top: 18px;
    margin-bottom: 20px;
    padding-top: 5px;
    width: 100%;
}}

/* Target any text elements within the Reset Filters button */
#reset-filters button div,
#reset-filters button span,
#reset-filters button p,
[data-testid="stSidebar"] #reset-filters button div,
[data-testid="stSidebar"] #reset-filters button span,
[data-testid="stSidebar"] #reset-filters button p {{
    font-size: 16px !important;
    font-weight: 600 !important;
}}

/* Custom button styling that won't be overridden by Streamlit */
#custom-reset-btn {{
    background-color: #0066CC !important;
    color: white !important;
    border: none !important;
    border-radius: 980px !important; /* Apple's pill-shaped buttons */
    padding: 8px 18px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    box-shadow: none !important;
    transition: all 0.2s ease-in-out !important;
    width: 75% !important;
    text-align: center !important;
    cursor: pointer !important;
    display: inline-block !important;
}}

#custom-reset-btn:hover {{
    background-color: #004DA6 !important;
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
}}

#custom-reset-btn:active {{
    transform: translateY(1px);
    box-shadow: none !important;
}}

/* Extremely specific selector to override Streamlit's default button styling */
[data-testid="stSidebar"] #reset-filters button,
[data-testid="stSidebar"] #reset-filters [data-testid="baseButton-secondary"],
#reset-filters button {{
    background-color: var(--oct-primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 980px !important; /* Apple's pill-shaped buttons */
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    box-shadow: none !important;
    transition: all 0.2s ease-in-out !important;
    width: 75% !important;
    text-align: center !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 36px !important;
}}

[data-testid="stSidebar"] #reset-filters button:hover,
[data-testid="stSidebar"] #reset-filters [data-testid="baseButton-secondary"]:hover,
[data-testid="stSidebar"] #reset-filters .stButton > button:hover,
#reset-filters button:hover,
#reset-filters .stButton > button:hover {{
    background-color: #004DA6 !important;
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}}

[data-testid="stSidebar"] #reset-filters button:active,
[data-testid="stSidebar"] #reset-filters [data-testid="baseButton-secondary"]:active,
[data-testid="stSidebar"] #reset-filters .stButton > button:active,
#reset-filters button:active,
#reset-filters .stButton > button:active {{
    transform: translateY(1px);
    box-shadow: none !important;
}}

{flex_row_css}
</style>
"""
    return css
