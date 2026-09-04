# Architecture

```text
                    USER
                      |
             NSE / BSE + company query
                      |
              COMPANY RESOLVER
                      |
          exact listed security identity
                      |
          +-----------+-----------+
          |                       |
   FINANCIAL AGENT          INDUSTRY AGENT
          |                       |
  statements / reports       competitors / news
  earnings calls             industry reports
  historical movement        macro signals
  capital allocation         sector implications
          |                       |
          +-----------+-----------+
                      |
              SYNTHESIS AGENT
                      |
          prioritized research queue
                      |
              STREAMLIT DASHBOARD
```

All external research is performed through Gemini with Google Search grounding. Calculations and presentation happen locally in Python/Streamlit.

The system does not maintain a predefined company universe. Company identity is resolved dynamically on every research run.
