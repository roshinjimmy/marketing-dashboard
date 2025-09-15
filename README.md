# Marketing Intelligence Dashboard

## Overview

This comprehensive analytics platform integrates multi-channel marketing data (Facebook, Google, TikTok) with business performance metrics to deliver actionable intelligence through interactive visualizations. The dashboard enables data-driven decision making by connecting marketing activities directly to revenue, customer acquisition, and profitability outcomes.

Key capabilities include:
- Cross-channel performance analysis with unified metrics
- Time-series visualization with attribution lag modeling
- Geographic and tactical effectiveness comparison
- Campaign-level ROI assessment and optimization
- Profit impact analysis for financial alignment
- Data quality monitoring for analytical integrity

Live demo: https://marketing-dashboard-lifesight.streamlit.app/

## Dashboard Overview

The Marketing Analytics Dashboard consists of six integrated views designed to provide comprehensive marketing performance analysis:

### 1. Executive Summary
A high-level overview of key performance indicators with period-over-period comparisons, highlighting trends in spend efficiency, acquisition costs, and revenue metrics.

### 2. Performance Trends
Time-series visualization of critical marketing and business metrics with options for rolling averages and attribution lag analysis. Enables identification of temporal patterns and correlation between marketing efforts and business outcomes.

### 3. Channel & Tactic Analysis
Comparative performance visualization across marketing channels and tactics with geographic breakdown. Provides insight into regional performance variations and channel effectiveness.

### 4. Campaign Drilldown
Detailed campaign-level performance data with sortable metrics and performance indicators. Allows granular analysis of individual campaign performance against targets.

### 5. Profit Analysis
Financial impact assessment showing contribution margin and profit metrics across marketing activities. Visualizes the relationship between marketing spend and bottom-line results.

### 6. Data Quality Monitor
Data integrity dashboard highlighting missing values, outliers, and potential anomalies in the marketing dataset. Ensures analytical reliability and flags potential data collection issues.

## Technical Architecture

### Data Layer
- **Source Data**: Integrated campaign-level marketing data (`Facebook.csv`, `Google.csv`, `TikTok.csv`) with business performance metrics (`business.csv`)
- **Processing**: DuckDB for high-performance analytics and Parquet for optimized data storage
- **Key Derived Metrics**:
  - **Performance**: MER (Total Revenue/Ad Spend), Attributed ROAS (Platform Revenue/Spend)
  - **Efficiency**: Blended CAC (Spend/New Customers), CTR (Clicks/Impressions), CPC (Spend/Clicks)
  - **Financial**: Contribution (Gross Profit-Spend), Profit ROAS (Gross Profit/Spend)

### Interface & Controls

#### Global Filter System
- Unified filter architecture with consistent application across all views
- Shareable URL state management for collaborative analysis
- Preset date ranges with dynamic period-over-period comparison
- Optional target threshold integration for performance evaluation

#### Interactive Visualization Framework
- Cross-filtering capabilities between visualizations
- Dynamic metric selection and comparison
- Visualization-specific controls (rolling averages, lag effects, map/chart toggles)
- Responsive layout optimization for different screen sizes

## Installation & Setup

### Local Development Environment

1. Clone the repository and navigate to the project directory
2. Create a Python virtual environment (3.10+)
3. Install dependencies
4. Launch the Streamlit application

```bash
# Clone repository (if not already done)
git clone https://github.com/yourusername/marketing-dashboard.git
cd marketing-dashboard

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app/main.py
```

### Configuration Options

Data files are automatically loaded from the `data/` directory relative to the repository root. For custom data locations, set the `DATA_DIR` environment variable:

```bash
export DATA_DIR=/absolute/path/to/your/data
streamlit run app/main.py
```

## Deployment

The dashboard is deployed using Streamlit Community Cloud with continuous integration:

1. Connect your Streamlit Cloud account to the GitHub repository
2. Configure deployment settings:
   - Entry point: `app/main.py`
   - Python version: 3.10+
   - Environment variables (optional): Set `DATA_DIR` if using custom data location

For production environments, consider:
- Implementing authentication for sensitive data
- Setting up scheduled data refresh processes
- Configuring resource scaling based on user load

## Architecture & Organization

### Project Structure

```
marketing-dashboard/
├── app/                  # Application source code
│   ├── main.py           # Entry point, routing, and global filter system
│   ├── data.py           # Data processing, normalization, and storage optimization
│   ├── metrics.py        # Performance metric calculation and standardization
│   ├── theme.py          # Visual styling and UI configuration
│   └── views/            # Dashboard view modules
│       ├── summary.py    # Executive Summary with KPIs and channel breakdown
│       ├── trends.py     # Time series analysis with attribution modeling
│       ├── drilldown.py  # Campaign-level performance analysis
│       ├── geo_tactic.py # Geographic and tactical performance visualization
│       ├── profit.py     # Profit contribution and financial alignment
│       └── data_quality.py # Data integrity monitoring and validation
├── data/                 # Input data sources (CSV format)
│   ├── Facebook.csv      # Facebook marketing campaign data
│   ├── Google.csv        # Google Ads campaign data
│   ├── TikTok.csv        # TikTok marketing campaign data
│   └── business.csv      # Business performance metrics
├── docs/                 # Documentation
│   ├── plan.md           # Implementation strategy and technical approach
│   └── screenshots/      # Dashboard visualization examples
└── requirements.txt      # Dependency specification
```

### Technology Stack

- **Frontend Framework**: Streamlit for rapid application development
- **Data Processing**: DuckDB for high-performance analytical queries
- **Storage Optimization**: Parquet for compressed columnar data storage
- **Visualization**: Plotly and Altair for interactive data visualization
- **State Management**: Streamlit URL parameter system for shareable states

## Roadmap & Future Development

Planned enhancements to expand the platform's capabilities:

### Analytics Extensions
- **Predictive Modeling**: Budget forecasting and scenario planning
- **Attribution Enhancement**: Multi-touch attribution modeling with customizable weighting
- **Cohort Analysis**: Customer retention and lifetime value tracking

### Technical Improvements
- **API Integration**: Direct connections to advertising platforms for automated data refresh
- **Performance Optimization**: Data pre-aggregation for faster dashboard loading
- **Notification System**: Automated alerts for performance anomalies and goal achievements

### User Experience
- **Customizable Reporting**: User-defined report templates and dashboard configurations
- **Advanced Visualizations**: Enhanced chart types and interactive data exploration
- **Mobile Optimization**: Responsive design improvements for on-the-go analytics

## Deployment

The dashboard is deployed on Streamlit Community Cloud:

1) Create a Streamlit Cloud account
2) Connect to this GitHub repository
3) Configure the app to use `app/main.py` as the entry point
4) Set Python 3.10+ as the runtime environment

## Visual Interface

The following screenshots demonstrate key dashboard components:

![Executive Summary](docs/screenshots/executive-summary.png)
*Executive Summary: Comprehensive KPI visualization with channel performance breakdown*

![Trends Analysis 1](docs/screenshots/trend-analysis-1.png)
*Performance Trends: Marketing spend vs. revenue correlation analysis with time-series visualization*

![Trends Analysis 2](docs/screenshots/trend-analysis-2.png)
*Performance Metrics: Marketing efficiency ratio and customer acquisition cost trend analysis*

![Profit Analysis](docs/screenshots/profit-contribution.png)
*Financial Impact: Contribution margin and profit ROAS assessment with period-over-period comparison*

## Technical Methodology

### Analytical Approach

- **Source of Truth**: Business data serves as the authoritative source for revenue, profit, and order metrics
- **Attribution Model**: Platform-specific attribution is isolated to channel/campaign ROAS calculations
- **Data Handling**: 
  - Zero-division protection in all ratio calculations
  - Null values converted to zeros for consistent aggregation
  - Optional lag factors for modeling delayed conversion effects
  - 7-day rolling averages for trend smoothing and volatility reduction
- **Metric Standardization**: Consistent calculation methodology across all channels for fair comparison

### Effective Usage Guide

1. **Hierarchical Analysis**: Begin with the Executive Summary to identify performance trends, then navigate to specific views for deeper investigation

2. **Comparative Analysis**: Utilize the date comparison feature to evaluate current performance against historical benchmarks with automatic percentage change calculation

3. **Anomaly Investigation**: When identifying unusual patterns in trend visualizations, leverage the Campaign Drilldown view to isolate contributing factors

4. **Attribution Optimization**: Experiment with lag settings (0-3 days) to accurately model the relationship between marketing activities and business outcomes

5. **Data Validation**: Consult the Data Quality Monitor when encountering unexpected metrics to verify underlying data integrity

6. **Performance Benchmarking**: Set KPI targets through the global controls to visualize actual performance against objectives

7. **Insight Sharing**: Generate shareable links with preserved filter states to facilitate collaborative analysis

8. **Geographic Intelligence**: Utilize regional visualizations to identify market-specific optimization opportunities

9. **Financial Alignment**: Focus on the Profit Analysis view to evaluate marketing's direct contribution to bottom-line results

## Next Steps & Future Enhancements

- Budget pacing and forecasting module
- A/B test analysis integration
- Cohort retention analysis
- Integration with API data sources for automatic updates
- Enhanced cross-channel attribution modeling