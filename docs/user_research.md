# User Research Synthesis

**Participants:** 15 professionals: 6 product managers / product development, 5 actuarial (pricing & reserving), 4 compliance / regulatory filing.
**Format:** 30–45 minute semi-structured interviews.

## Key findings
1. **Competitor research is manual and slow.** Most participants described searching SERFF Filing Access state by state, opening PDF filing memoranda, and copying rate change %, effective dates, and coverage changes into Excel. A typical competitor review took several hours per state.
2. **Company names don't join cleanly.** Filings use group names, subsidiary names, and abbreviations that don't match NAIC statement data without manual mapping.
3. **Rates without loss experience lack context.** Actuaries wanted to know whether a competitor's increase was a reaction to their own loss ratio deterioration or a market-wide trend.
4. **Stakeholders want visuals, not tables.** Product and leadership audiences preferred maps and simple comparisons over raw filing lists.

## How findings shaped the product
| Finding | Feature |
|---|---|
| Manual copy/paste of rate fields | `parser.py`: regex extraction of selected/indicated change, effective date, impact range |
| Name mismatches | `normalize.py`: NAIC code first, fuzzy-name fallback |
| Need loss context | `v_rate_vs_loss` view joins prior-year LR to next-year rate action |
| Visual communication | Tableau dashboards + Excel workbook for non-technical peers |

## Outcome
In before/after timing with participants, the pipeline + dashboard cut competitor research time by **~40%**. Findings were presented to **20+ non-technical peers**.
