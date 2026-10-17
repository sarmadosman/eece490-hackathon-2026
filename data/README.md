# Supplied transaction data

Local input: `raw/stories_transactions.csv`, copied unchanged from the file supplied by the user.
SHA-256: `f1672e728c28295b2b802d878fd38a158ba039827b429355e8438ee0463237a1`.

The CSV is excluded from Git by default. A fresh checkout needs the supplied file placed at this path, or `--data /path/to/file.csv`. No external dataset is necessary. The local notebook and analysis use the actual provided CSV, not generated replacements.

## Grain and definitions

| Original column | Definition used here |
|---|---|
| Transaction ID | Basket identifier; repeated values across item lines are expected |
| Date, Time | Recorded date and local clock time; timezone is not specified |
| Branch | Recorded branch; no assumed unaffected control branch |
| Customer ID | Optional identifier; missing IDs are retained, never imputed as one customer |
| Order Type | Recorded service mode |
| Product, Category | Recorded menu labels |
| Quantity | Units on an item line |
| Unit Price (USD) | Listed price before the recorded discount |
| Discount Rate | Fraction, e.g. 0.15 means 15% |
| Unit Cost (USD) | Recorded product cost; whether procurement, allocation, or recipe cost is unknown |
| Line Revenue (USD) | Recorded revenue, reconciled to quantity × price × (1 − discount) |
| Line Gross Profit (USD) | Revenue minus recorded product costs; excludes unrecorded labor, rent, and overhead |

Retain exact duplicate lines in the primary analysis because their meaning is unresolved. Export a deduplicated sensitivity analysis. Calendar dates with no records are treated as zero observed sales, which does not establish that a branch was open or stocked.

The brief describes transaction data with replacement IDs. IDs in this file begin with `SYN-`; neither the prefix nor the brief alone establishes how the supplied data were generated. Avoid stronger claims about provenance.
