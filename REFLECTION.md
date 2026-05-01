# REFLECTION: Building a Generalized Data Summarization System

## Code Reuse from Milestone A

The Milestone A scripts were already designed to accept a CSV filename as a
command-line argument and to detect column types dynamically. This meant the core
statistical functions (numeric_stats, categorical_stats, type inference) transferred
to Milestone B without modification.

What did require changes:

- **Missing value tokens**: The FB Posts dataset uses "-" as a missing indicator
  (in the "Is Video Owner?" column), which was not in the original token set.
  Adding it to the shared MISSING_TOKENS set was a one-line fix that improved
  handling across all datasets.

- **Date format detection**: FB Posts uses datetime strings like
  "2023-09-04 19:31:22 EDT" while FB Ads uses clean "YYYY-MM-DD" dates and
  Twitter uses "2023-09-30 14:11:00". The type inference needed to handle the
  date portion before the space, not the full string.

- **Grouping keys**: The biggest change was making group key detection dynamic.
  Milestone A hardcoded "page_id" and "ad_id". For Milestone B, the script scans
  available columns for known identifier patterns (page_id, Facebook_Id, id,
  post_id, ad_id) and categorical grouping candidates (Type, source, lang).
  This is not truly schema-agnostic — it relies on a priority list of candidate
  column names — but it works across all three datasets without modification.

- **Boolean columns**: Twitter has columns like "isReply" and "isRetweet" with
  text values "True"/"False" that needed a new type category.

Overall, approximately 85% of the Milestone A code carried forward unchanged.

---

## Strategies for Generalization

The primary strategy was **dynamic type inference** — every column is classified
based on its values rather than hardcoded expectations. The type inference function
checks for numeric convertibility, date patterns, dict-like structures, list-like
structures, booleans, and high-cardinality identifiers, in that order. This
approach works on any well-formed CSV without requiring schema configuration.

For grouping, the approach was a **priority-ordered candidate list**. The script
looks for known identifier columns and selects the first match. This is a pragmatic
compromise: it handles the three known datasets and would work for many common
schemas, but a truly unknown dataset might have identifier columns with unexpected
names. A more robust approach would be to analyze cardinality and uniqueness ratios
to identify candidate grouping columns automatically.

**No dataset-specific conditionals** were added. The same script processes all three
files without any if-statements checking filenames or column sets.

---

## Did the Three Platforms Tell the Same Story?

For the 27 shared illuminating indicators, the platforms tell related but distinct
stories:

- **Advocacy is universal**: roughly 55% across all three platforms, suggesting
  that advocacy is a baseline strategy regardless of medium.
- **CTA is a paid-ads strategy**: 57% in FB Ads vs 11-13% in organic posts.
  This is the single largest difference and reflects the fundamental purpose
  of paid advertising versus organic content.
- **Twitter is more confrontational**: highest rates of attack messaging and
  economic policy discussion.
- **Health and women's issues are ad-driven topics**: their prevalence drops
  significantly in organic content, suggesting these are targeted campaign
  advertising themes rather than grassroots conversation topics.

These differences likely reflect both platform mechanics (Twitter's conversational
format encourages debate; Facebook ads are designed for action) and campaign
strategy (using paid ads for targeted issue messaging while organic content drives
broader engagement).

---

## Handing the System to a Colleague

If a colleague needed to analyze a completely different dataset (e.g., a public
health survey or financial transaction log), the following would just work:

- CSV loading and basic structure reporting
- Missing value detection and counting
- Column type inference (numeric, categorical, date, identifier)
- Column-level descriptive statistics
- Dataset overview and missing value summary

What they might need to change:

- **Grouping key detection**: If their dataset uses column names not in the
  candidate list, the script would skip grouped analysis rather than fail.
  They would need to add their identifier columns to the priority list.
- **Missing value tokens**: Some datasets use domain-specific missing indicators
  (e.g., "999", "UNKNOWN", "N/A") that would need to be added to MISSING_TOKENS.
- **Encoding**: The scripts assume UTF-8. A file with Latin-1 or Windows-1252
  encoding would need the encoding parameter adjusted.

The core statistical logic is fully general and requires no changes.

---

## Evolution of Tool Opinions

After working with all three approaches across three tasks:

**Pure Python** is most valuable as a learning tool and for understanding edge
cases. Writing the grouped analysis by hand (partitioning rows into dictionaries,
running stats on each partition) made it very clear what groupby() does behind the
scenes. However, the code volume makes it impractical for regular analytical work.

**Pandas** remains the most productive for daily analysis. The API is familiar,
the ecosystem is vast, and the documentation covers virtually any use case.
The main frustrations have been API changes across versions (Pandas 3.0 broke
some patterns from 2.x) and the implicit type coercion that can silently alter
data during loading.

**Polars** has grown on me. The strict typing caught errors earlier, and the
expression-based syntax forced clearer thinking about what each operation does.
For larger datasets, the performance advantage would be significant. The main
barrier is ecosystem maturity — fewer tutorials, fewer Stack Overflow answers,
and some library interactions that Pandas handles seamlessly.

If starting a new data analysis project today, I would choose Pandas for
exploratory work and Polars for production pipelines or large-scale processing.

---

## AI Code Generation for Generalization

AI tools (Claude, ChatGPT) tend to produce dataset-specific solutions by default.
When asked "write a script to compute descriptive statistics for a CSV", they
typically generate code with hardcoded column names or assumptions about data
types. Getting them to produce genuinely schema-agnostic code required explicit
prompting: "the script must work on any CSV without knowing the column names
in advance."

The AI-generated code was most useful for:
- Boilerplate (argument parsing, output formatting, CSV loading)
- Standard library patterns (Counter usage, statistics module functions)
- Polars syntax (which has less online documentation than Pandas)

The AI was least useful for:
- Edge case handling (mixed types, unusual missing value tokens)
- Grouping key selection logic (required domain knowledge)
- Cross-dataset comparison analysis (required understanding of the data)

Overall, AI tools accelerated the implementation but required significant manual
review and correction, particularly for the generalization requirements.
