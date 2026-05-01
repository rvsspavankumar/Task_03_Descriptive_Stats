#!/usr/bin/env python3
"""
Descriptive Statistics — Pandas Implementation

A generalized data summarization system that computes column-level, dataset-level,
and grouped descriptive statistics for any well-formed CSV file using Pandas.

Usage:
    python3 pandas_stats.py <path_to_csv>

Examples:
    python3 pandas_stats.py 2024_fb_ads_president_scored_anon.csv
    python3 pandas_stats.py 2024_fb_posts_president_scored_anon.csv
    python3 pandas_stats.py 2024_tw_posts_president_scored_anon.csv
"""

import sys
from pathlib import Path

import pandas as pd

# ─── Configuration ───────────────────────────────────────────────────
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}
MAX_TOP_VALUES = 5
MAX_GROUPS_PRINTED = 10
WIDTH = 76


# ─── Helpers ─────────────────────────────────────────────────────────

def normalize_missing(df):
    """Replace common missing-value tokens with pd.NA in object columns."""
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(list(MISSING_TOKENS), pd.NA)
    return df


def infer_column_type(series):
    """Classify a column as numeric, date, identifier, boolean, or categorical."""
    non_missing = series.dropna()
    if non_missing.empty:
        return "empty"

    # If Pandas already typed it as numeric, trust it
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    sample = non_missing.astype(str)

    # Check numeric
    numeric_check = pd.to_numeric(sample, errors="coerce")
    if numeric_check.notna().all():
        return "numeric"

    # Check boolean
    if sample.str.lower().isin(["true", "false"]).all():
        return "boolean"

    # Check date (YYYY-MM-DD with optional time, or YYYY-MM)
    date_parts = sample.str.split(" ").str[0]
    date_check = pd.to_datetime(date_parts, errors="coerce", format="%Y-%m-%d")
    if date_check.notna().sum() / len(sample) > 0.9:
        return "date"

    # Check dict-like range text
    if sample.str.startswith("{").all():
        return "range_text"

    # Check list-like text
    if sample.str.startswith("[").all() and sample.str.endswith("]").all():
        return "list_text"

    # High cardinality -> identifier
    unique_ratio = sample.nunique() / len(sample) if len(sample) > 0 else 0
    if unique_ratio > 0.95 and len(sample) > 20:
        return "identifier"

    return "categorical"


def fmt(value, decimals=6):
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def print_header(title):
    print("\n" + "=" * WIDTH)
    print(title)
    print("=" * WIDTH)


# ─── Dataset-Level Analysis ──────────────────────────────────────────

def print_dataset_overview(df, label="DATASET"):
    print_header(f"{label} OVERVIEW")
    print(f"  Total rows   : {df.shape[0]}")
    print(f"  Total columns: {df.shape[1]}")
    print("\n  Column names:")
    for col in df.columns:
        print(f"    - {col}")
    print("\n  Pandas dtypes:")
    for col in df.columns:
        print(f"    {col}: {df[col].dtype}")


def print_missing_summary(df):
    print_header("MISSING VALUES BY COLUMN")
    n = len(df)
    miss_counts = df.isna().sum()
    for col in df.columns:
        miss = int(miss_counts[col])
        pct = (miss / n * 100) if n else 0
        print(f"  {col}: {miss} ({pct:.2f}%)")


def print_describe(df):
    print_header("PANDAS describe() — NUMERIC COLUMNS")
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        print("  (no numeric columns detected by Pandas)")
    else:
        print(numeric_df.describe().to_string())

    print_header("PANDAS describe() — ALL COLUMNS")
    print(df.describe(include="all").to_string())


def print_column_analysis(df, heading="COLUMN-BY-COLUMN DESCRIPTIVE STATISTICS"):
    print_header(heading)

    for col in df.columns:
        series = df[col]
        col_type = infer_column_type(series)
        miss = int(series.isna().sum())
        non_miss = int(series.notna().sum())

        print("\n" + "-" * WIDTH)
        print(f"  Column                 : {col}")
        print(f"  Inferred type          : {col_type}")
        print(f"  Non-missing count      : {non_miss}")
        print(f"  Missing count          : {miss}")

        if col_type == "numeric":
            nums = pd.to_numeric(series, errors="coerce").dropna()
            if nums.empty:
                print("  (no valid numeric values)")
            else:
                print(f"  Count                  : {int(nums.count())}")
                print(f"  Mean                   : {fmt(nums.mean())}")
                print(f"  Min                    : {fmt(nums.min())}")
                print(f"  Max                    : {fmt(nums.max())}")
                print(f"  Median                 : {fmt(nums.median())}")
                print(f"  Std Dev                : {fmt(nums.std())}")
        else:
            clean = series.dropna().astype(str)
            if clean.empty:
                print("  Count                  : 0")
                print("  Unique values          : 0")
                print("  Mode                   : None")
                print("  Mode frequency         : 0")
            else:
                vc = clean.value_counts()
                print(f"  Count                  : {len(clean)}")
                print(f"  Unique values          : {clean.nunique()}")
                print(f"  Mode                   : {vc.index[0]}")
                print(f"  Mode frequency         : {int(vc.iloc[0])}")
                print(f"  Top {MAX_TOP_VALUES} values:")
                for val, freq in vc.head(MAX_TOP_VALUES).items():
                    display = val if len(val) <= 60 else val[:57] + "..."
                    print(f"    - {display}: {freq}")


# ─── Grouped Analysis ────────────────────────────────────────────────

def print_grouped_analysis(df, group_keys):
    key_label = " + ".join(group_keys)
    print_header(f"GROUPED ANALYSIS BY: {key_label}")

    grouped = df.groupby(group_keys, dropna=False)
    print(f"  Total groups: {grouped.ngroups}")

    # Build a DataFrame of group sizes sorted descending
    size_df = grouped.size().reset_index(name="_count").sort_values(
        "_count", ascending=False
    )

    # Identify numeric columns for aggregation
    agg_cols = [c for c in df.columns if c not in group_keys]
    numeric_agg = [c for c in agg_cols if infer_column_type(df[c]) == "numeric"]

    for idx in range(min(MAX_GROUPS_PRINTED, len(size_df))):
        row = size_df.iloc[idx]
        key_vals = {k: row[k] for k in group_keys}
        count = int(row["_count"])

        key_display = " | ".join(
            f"{k}={str(v)[:40]}" for k, v in key_vals.items()
        )
        print(f"\n{'~' * WIDTH}")
        print(f"  Group: {key_display}")
        print(f"  Rows : {count}")

        # Filter to this group
        mask = pd.Series(True, index=df.index)
        for k, v in key_vals.items():
            if pd.isna(v):
                mask = mask & df[k].isna()
            else:
                mask = mask & (df[k] == v)
        group_df = df.loc[mask]

        for c in numeric_agg:
            nums = pd.to_numeric(group_df[c], errors="coerce").dropna()
            if not nums.empty:
                print(f"    {c}:")
                print(f"      count={int(nums.count())}  mean={fmt(nums.mean(),2)}"
                      f"  min={fmt(nums.min(),2)}  max={fmt(nums.max(),2)}"
                      f"  median={fmt(nums.median(),2)}  std={fmt(nums.std(),2)}")

        for c in agg_cols:
            if c in numeric_agg:
                continue
            col_type = infer_column_type(df[c])
            if col_type == "categorical":
                clean = group_df[c].dropna().astype(str)
                if not clean.empty and clean.nunique() <= 20:
                    vc = clean.value_counts()
                    print(f"    {c}: unique={clean.nunique()}"
                          f"  mode={vc.index[0]} ({int(vc.iloc[0])})")

    if len(size_df) > MAX_GROUPS_PRINTED:
        remaining = len(size_df) - MAX_GROUPS_PRINTED
        print(f"\n  ... and {remaining} more groups (omitted for brevity)")


# ─── Dynamic Group Key Detection ─────────────────────────────────────

def detect_group_keys(columns):
    """
    Automatically detect sensible grouping strategies based on available columns.
    No dataset-specific hardcoding — uses column name patterns to decide.
    """
    strategies = []
    cols = list(columns)

    # Primary grouping: look for an account/page-level identifier
    primary_id = None
    for candidate in ["page_id", "Facebook_Id", "id", "account_id", "user_id"]:
        if candidate in cols:
            primary_id = candidate
            break

    if primary_id:
        strategies.append([primary_id])

    # Secondary grouping: primary + a post/ad-level identifier
    secondary_id = None
    for candidate in ["ad_id", "post_id", "tweet_id"]:
        if candidate in cols:
            secondary_id = candidate
            break

    if primary_id and secondary_id:
        strategies.append([primary_id, secondary_id])

    # Categorical grouping: look for useful non-ID categorical columns
    for candidate in ["Type", "source", "lang", "Page Category",
                       "currency", "Video Share Status"]:
        if candidate in cols:
            strategies.append([candidate])
            break  # Only add one categorical grouping

    return strategies


# ─── Main ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pandas_stats.py <path_to_csv>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print(f"\nLoading: {file_path}")
    df = pd.read_csv(file_path, keep_default_na=True)
    df = normalize_missing(df)

    # ── Dataset-level analysis ──
    print_dataset_overview(df, label=file_path.stem)
    print_missing_summary(df)
    print_describe(df)
    print_column_analysis(df)

    # ── Grouped analysis ──
    group_strategies = detect_group_keys(df.columns)
    if group_strategies:
        for keys in group_strategies:
            print_grouped_analysis(df, keys)
    else:
        print("\n  (No suitable grouping columns detected.)")

    print("\n" + "=" * WIDTH)
    print("Analysis complete.")
    print("=" * WIDTH)


if __name__ == "__main__":
    main()
