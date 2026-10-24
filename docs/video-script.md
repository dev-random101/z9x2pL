# Video Script: UK Wind Generation Forecast Analysis

**Total Duration**: < 10 Minutes

---

## Part 1: Client Pitch (Max 5 Mins)
**Goal**: Demonstrate business value and the "Buying Insight".

### Shot List
1. **Intro (30s)**: Speaker on camera, explaining the problem (Day-ahead market risk, forecast error).
2. **Demo - Main Chart (2m)**: 
   - Show the Actual vs Forecast line chart.
   - Change the **Cutoff Time** (e.g., from 09:00 to 15:00) $\rightarrow$ show how the forecast line changes.
   - Explain: "We aren't just looking at the best forecast, but the one you actually had when you made the decision."
3. **Demo - Metrics (1.5m)**:
   - Highlight the **Bias** and **P90 Error**.
   - Read the **Buying Insight** panel: "Forecast over-predicts by X MW on average; covering 90% of cases needs a buffer of Y MW."
   - Explain: "This number tells you exactly how much extra thermal power to secure to avoid imbalance charges."
4. **Closing (30s)**: Summary of value (Reduced risk, quantified buffer).

---

## Part 2: Tech Lead Walkthrough (Max 5 Mins)
**Goal**: Explain the "how" and the technical trade-offs.

### Shot List
1. **Architecture Diagram (1m)**: 
   - Show the flow: Elexon API $\rightarrow$ Processed CSVs $\rightarrow$ FastAPI $\rightarrow$ React.
   - Explain the "Data-in-Repo" choice for Vercel serverless performance.
2. **The Core Logic (2m)**:
   - Open `services/selection.py`.
   - Explain the logic: filtering by \`publishTime <= cutoff\`, then taking the \`max(publishTime)\`.
   - Emphasize: "This prevents data leakage—we never use a forecast that was published after the decision time."
3. **Metrics & Testing (1m)**:
   - Show `services/metrics.py` and the pytest suite.
   - Mention the MAPE guard (using NMAE) to avoid division by zero.
4. **Deployment & Trade-offs (1m)**:
   - Show `vercel.json` and the Docker setup.
   - Discuss the tradeoff between a real DB and CSVs for a project of this scale.
