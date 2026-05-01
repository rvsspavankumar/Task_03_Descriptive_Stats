# Task_03_Descriptive_Stats

## A Generalized Data Summarization System for Multi-Dataset Analysis

## Project Overview

This project builds a generalized data summarization system capable of processing
any well-formed CSV file and producing descriptive statistical analysis without
dataset-specific hardcoding. The system is implemented in three independent
approaches — Pure Python, Pandas, and Polars — and is tested against three
datasets related to political social media activity during the 2024 U.S.
Presidential election.

The system demonstrates:

- **Schema-agnostic design**: dynamic type inference, automatic grouping key
  detection, and no hardcoded column names
- **Cross-platform analysis**: comparing messaging strategies and topic emphasis
  across Facebook Ads, Facebook Posts, and Twitter/X Posts
- **Three analytical approaches**: reinforcing fluency in pure Python, Pandas,
  and Polars through repeated application to different data

---

## Datasets

All three datasets relate to political social media activity during the 2024
U.S. Presidential election:

| Dataset       | File                                          | Rows    | Columns |
|---------------|-----------------------------------------------|---------|---------|
| Facebook Ads  | `2024_fb_ads_president_scored_anon.csv`        | 246,745 | 41      |
| Facebook Posts| `2024_fb_posts_president_scored_anon.csv`      | 19,009  | 56      |
| Twitter Posts | `2024_tw_posts_president_scored_anon.csv`      | 27,304  | 47      |

### Dataset Source

Google Drive link:
https://drive.google.com/file/d/1Jq0fPb-tq76Ee_RtM58fT0_M3o-JDBwe/view?usp=sharing

### Important

The dataset files **are not included in this repository**. Download them from the
link above and place all three CSV files in the project directory.

---

## Project Structure

```
Task_03_Descriptive_Stats/
├── pure_python_stats.py       # Standard library only — works on all three datasets
├── pandas_stats.py            # Pandas implementation — works on all three datasets
├── polars_stats.py            # Polars implementation — works on all three datasets
├── README.md                  # This file
├── CROSS_DATASET.md           # Cross-dataset comparison of shared columns
├── REFLECTION.md              # Comparison of approaches and research question responses
├── requirements.txt           # Python dependencies
└── .gitignore                 # Excludes CSV, .env, __pycache__, etc.
```

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Place the datasets

Download the three CSV files from the link above and place them in the project
directory.

### 3. Run against any dataset

Each script accepts a CSV file path as its first argument. The same script works
on all three files without modification:

**Pure Python:**
```bash
python3 pure_python_stats.py 2024_fb_ads_president_scored_anon.csv
python3 pure_python_stats.py 2024_fb_posts_president_scored_anon.csv
python3 pure_python_stats.py 2024_tw_posts_president_scored_anon.csv
```

**Pandas:**
```bash
python3 pandas_stats.py 2024_fb_ads_president_scored_anon.csv
python3 pandas_stats.py 2024_fb_posts_president_scored_anon.csv
python3 pandas_stats.py 2024_tw_posts_president_scored_anon.csv
```

**Polars:**
```bash
python3 polars_stats.py 2024_fb_ads_president_scored_anon.csv
python3 polars_stats.py 2024_fb_posts_president_scored_anon.csv
python3 polars_stats.py 2024_tw_posts_president_scored_anon.csv
```

To save output for review:
```bash
python3 pandas_stats.py 2024_fb_ads_president_scored_anon.csv > output_fb_ads.txt
```

---

## Summary of Findings

### Facebook Ads (246,745 records)

- **Highly concentrated activity**: Top 5 pages account for ~46% of all ads.
  The largest single page produced 55,503 ads.
- **Right-skewed spending**: Mean spend $1,061 vs. median $49. Most ads are
  low-budget and targeted; a few are very expensive.
- **Mobilization-focused**: CTA messaging appears in 57% of ads — the highest
  of any platform. Advocacy at 55%.
- **Health and women's issues are over-represented** relative to organic
  platforms, suggesting targeted paid messaging strategies.

### Facebook Posts (19,009 records)

- **Small number of pages**: Only 21 unique Facebook pages, with the top page
  producing 9,013 posts (47% of dataset).
- **High engagement variance**: Mean likes per post = 2,378 but with very high
  standard deviation, indicating viral posts alongside low-engagement content.
- **More issue-focused**: 46% of posts contain issue messaging vs. 38% in ads.
- **Lower CTA**: Only 13% of posts are call-to-action, compared to 57% in ads.
- **Notable missing data**: Page Category (13%), Page Admin Top Country (14%),
  and Type (13%) have significant missingness.

### Twitter/X Posts (27,304 records)

- **High engagement per post**: Mean 6,914 likes and 507,085 views per post.
- **Most confrontational**: Attack messaging at 31% is the highest across platforms.
- **Most issue-focused**: 51% issue messaging, highest of all three.
- **Economy dominates**: 16% of tweets address economic topics, highest share
  across platforms.
- **Overwhelmingly English**: 99.9% of posts in English.
- **Twitter Web App dominates**: 55% of posts from web client, 31% from iPhone.

---

## Cross-Dataset Comparison

All three datasets share 27 binary classification columns (the "illuminating"
indicators). Key findings from comparing these shared columns:

- **Advocacy is universal** (~55% across all platforms)
- **CTA is a paid-ads strategy** (57% in ads vs. 11-13% in organic posts)
- **Twitter is more attack-oriented** (31%) and issue-focused (51%)
- **Health and women's issues are ad-driven topics**, dropping significantly
  in organic content
- **Incivility is highest in ads and Twitter** (~18-19%), lowest in FB Posts (13%)

A detailed comparison is in [CROSS_DATASET.md](CROSS_DATASET.md).

---

## Reflection on Three Approaches

All three implementations produce identical numerical results when missing value
handling and standard deviation semantics are aligned. The generalization from
Milestone A to Milestone B required changes primarily in grouping key detection
and missing value token handling — the core statistical logic was fully reusable.

Key takeaways after three tasks:
- **Pure Python**: best for learning, impractical for daily work
- **Pandas**: most productive, largest ecosystem, some version-stability concerns
- **Polars**: strictest typing, best performance, growing but smaller ecosystem

A detailed reflection is in [REFLECTION.md](REFLECTION.md).

---

## Requirements

```
pandas
polars
matplotlib
seaborn
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Author

Pavan Kumar Revanth
Master's in Information Systems
Syracuse University
