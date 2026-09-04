# Architecture

```text
                         GEMINI RESEARCH LAYER
                  + Google Search grounding
                              |
             +----------------+----------------+
             |                                 |
   FINANCIAL INTELLIGENCE              INDUSTRY INTELLIGENCE
             |                                 |
   Statement periods                    Competitor moves
   Margin / FCF / debt                  Sector news
   Working capital                      Macro drivers
   Anomalies                            Company impact
             |                                 |
             +---------------+-----------------+
                             |
                    RESEARCH SYNTHESIS
                             |
                Materiality / novelty / confidence
                             |
                    ANALYST ACTION CENTER
               READ NOW / REVIEW / MONITOR / IGNORE
```

## Separation of responsibilities

### Gemini
- Finds current public web evidence through Google Search grounding.
- Extracts structured reported numbers and events.
- Interprets drivers and evidence.
- Generates the research queue.

### Python
- Validates presence/types where practical.
- Calculates deterministic ratios and movements when the required inputs are present.
- Renders the dashboard.

## Why not call external finance APIs?

The project constraint is zero budget and a deliberately narrow stack. The trade-off is that Gemini Search is used as the public-data retrieval layer. This makes source traceability essential and means the UI should never imply institutional-feed precision.
