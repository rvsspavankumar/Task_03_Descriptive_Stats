#!/usr/bin/env python3
"""
Descriptive Statistics — Polars Implementation

A generalized data summarization system that computes column-level, dataset-level,
and grouped descriptive statistics for any well-formed CSV file using Polars.

Usage:
    python3 polars_stats.py <path_to_csv>

Examples:
    python3 polars_stats.py 2024_fb_ads_president_scored_anon.csv
    python3 polars_stats.py 2024_fb_posts_president_scored_anon.csv
    python3 polars_stats.py 2024_tw_posts_president_scored_anon.csv

Requirements:
    pip install polars
"""

import sys
from pathlib import Path

import polars as pl

# ─── Configuration ───────────────────────────────────────────────────
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-",
                  "NA", "N/A", "None", "NaN"}
MAX_TOP_VALUES = 5
MAX_GROUPS_PRINTED = 10
WIDTH = 76


# ─── Helpers ─────────────────────────────────────────────────────────

def normalize_missing(df):
    """Replace common missing-value tokens with null in string columns."""
    for col in df.columns:
        if df[col].dtype == pl.Utf8 or df[col].dtype == pl.String:
            df = df.with_columns(
                pl.when(
                    pl.col(col).str.strip_chars().str.to_lowercase().is_in(
                        [t.lower() for t in MISSING_TOKENS]
                    )
                )
                .then(None)
                .otherwise(pl.col(col).str.strip_chars())
                .alias(col)
            )
    return df


def infer_column_type(series):
    """Classify a column as numeric, date, identifier, boolean, or categorical."""
    non_null = series.drop_nulls()
    if non_null.is_empty():
        return "empty"

    # If Polars already inferred numeric, trust it
    if series.dtype in (pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                        pl.Float32, pl.Float64):
        return "numeric"

    sample = non_null.cast(pl.Utf8)

    # Try numeric conversion
    numeric_attempt = sample.str.strip_chars().cast(pl.Float64, strict=False)
    if numeric_attempt.null_count() == 0:
        return "numeric"

    # Check boolean
    if sample.str.to_lowercase().is_in(["true", "false"]).all():
        return "boolean"

    # Check date (YYYY-MM-DD, possibly with time after space)
    date_parts = sample.str.split(" ").list.first()
    date_attempt = date_parts.str.to_date("%Y-%m-%d", strict=False)
    non_null_dates = date_attempt.drop_nulls()
    if len(non_null_dates) / len(sample) > 0.9:
        return "date"

    # Dict-like text
    if sample.str.starts_with("{").all():
        return "range_text"

    # List-like text
    if sample.str.starts_with("[").all() and sample.str.ends_with("]").all():
        return "list_text"

    # High cardinality -> identifier
    unique_ratio = sample.n_unique() / len(sample) if len(sample) > 0 else 0
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
    print(f"  Total rows   : {df.height}")
    print(f"  Total columns: {df.width}")
    print("\n  Column names:")
    for col in df.columns:
        print(f"    - {col}")
    print("\n  Polars dtypes:")
    for col in df.columns:
        print(f"    {col}: {df[col].dtype}")


def print_missing_summary(df):
    print_header("MISSING VALUES BY COLUMN")
    n = df.height
    for col in df.columns:
        miss = df[col].null_count()
        pct = (miss / n * 100) if n else 0
        print(f"  {col}: {miss} ({pct:.2f}%)")


def print_describe(df):
    print_header("POLARS describe()")
    print(df.describe())


def print_column_analysis(df, heading="COLUMN-BY-COLUMN DESCRIPTIVE STATISTICS"):
    print_header(heading)

    for col in df.columns:
        series = df[col]
        col_type = infer_column_type(series)
        miss = series.null_count()
        non_miss = df.height - miss

        print("\n" + "-" * WIDTH)
        print(f"  Column                 : {col}")
        print(f"  Inferred type          : {col_type}")
        print(f"  Non-missing count      : {non_miss}")
        print(f"  Missing count          : {miss}")

        if col_type == "numeric":
            if series.dtype in (pl.Float32, pl.Float64, pl.Int8, pl.Int16,
                                pl.Int32, pl.Int64, pl.UInt8, pl.UInt16,
                                pl.UInt32, pl.UInt64):
                nums = series.drop_nulls()
            else:
                nums = (series.cast(pl.Utf8).str.strip_chars()
                        .cast(pl.Float64, strict=False).drop_nulls())

            if nums.is_empty():
                print("  (no valid numeric values)")
            else:
                print(f"  Count                  : {len(nums)}")
                print(f"  Mean                   : {fmt(nums.mean())}")
                print(f"  Min                    : {fmt(nums.min())}")
                print(f"  Max                    : {fmt(nums.max())}")
                print(f"  Median                 : {fmt(nums.median())}")
                print(f"  Std Dev                : {fmt(nums.std())}")
        else:
            clean = series.drop_nulls().cast(pl.Utf8)
            if clean.is_empty():
                print("  Count                  : 0")
                print("  Unique values          : 0")
                print("  Mode                   : None")
                print("  Mode frequency         : 0")
            else:
                vc = clean.value_counts().sort("count", descending=True)
                mode_val = vc[col][0]
                mode_freq = vc["count"][0]
                print(f"  Count                  : {len(clean)}")
                print(f"  Unique values          : {clean.n_unique()}")
                print(f"  Mode                   : {mode_val}")
                print(f"  Mode frequency         : {mode_freq}")
                print(f"  Top {MAX_TOP_VALUES} values:")
                for row in vc.head(MAX_TOP_VALUES).iter_rows():
                    val, freq = row[0], row[1]
                    display = str(val) if len(str(val)) <= 60 else str(val)[:57] + "..."
                    print(f"    - {display}: {freq}")


# ─── Grouped Analysis ────────────────────────────────────────────────

def print_grouped_analysis(df, group_keys):
    key_label = " + ".join(group_keys)
    print_header(f"GROUPED ANALYSIS BY: {key_label}")

    group_sizes = (
        df.group_by(group_keys)
        .agg(pl.len().alias("_count"))
        .sort("_count", descending=True)
    )
    print(f"  Total groups: {group_sizes.height}")

    agg_cols = [c for c in df.columns if c not in group_keys]
    numeric_agg = [c for c in agg_cols if infer_column_type(df[c]) == "numeric"]

    for idx in range(min(MAX_GROUPS_PRINTED, group_sizes.height)):
        row = group_sizes.row(idx, named=True)
        key_vals = {k: row[k] for k in group_keys}
        count = row["_count"]

        key_display = " | ".join(
            f"{k}={str(v)[:40]}" for k, v in key_vals.items()
        )
        print(f"\n{'~' * WIDTH}")
        print(f"  Group: {key_display}")
        print(f"  Rows : {count}")

        # Filter to this group
        expr = pl.lit(True)
        for k, v in key_vals.items():
            if v is None:
                expr = expr & pl.col(k).is_null()
            else:
                expr = expr & (pl.col(k) == v)
        group_df = df.filter(expr)

        for c in numeric_agg:
            if group_df[c].dtype in (pl.Float32, pl.Float64, pl.Int8, pl.Int16,
                                      pl.Int32, pl.Int64, pl.UInt8, pl.UInt16,
                                      pl.UInt32, pl.UInt64):
                nums = group_df[c].drop_nulls()
            else:
                nums = (group_df[c].cast(pl.Utf8).str.strip_chars()
                        .cast(pl.Float64, strict=False).drop_nulls())

            if not nums.is_empty():
                print(f"    {c}:")
                print(f"      count={len(nums)}  mean={fmt(nums.mean(),2)}"
                      f"  min={fmt(nums.min(),2)}  max={fmt(nums.max(),2)}"
                      f"  median={fmt(nums.median(),2)}  std={fmt(nums.std(),2)}")

        for c in agg_cols:
            if c in numeric_agg:
                continue
            col_type = infer_column_type(df[c])
            if col_type == "categorical":
                clean = group_df[c].drop_nulls().cast(pl.Utf8)
                if not clean.is_empty() and clean.n_unique() <= 20:
                    vc = clean.value_counts().sort("count", descending=True)
                    mode_v = vc[c][0]
                    mode_f = vc["count"][0]
                    print(f"    {c}: unique={clean.n_unique()}"
                          f"  mode={mode_v} ({mode_f})")

    if group_sizes.height > MAX_GROUPS_PRINTED:
        remaining = group_sizes.height - MAX_GROUPS_PRINTED
        print(f"\n  ... and {remaining} more groups (omitted for brevity)")


# ─── Dynamic Group Key Detection ─────────────────────────────────────

def detect_group_keys(columns):
    """
    Automatically detect sensible grouping strategies based on available columns.
    No dataset-specific hardcoding — uses column name patterns to decide.
    """
    strategies = []
    cols = list(columns)

    primary_id = None
    for candidate in ["page_id", "Facebook_Id", "id", "account_id", "user_id"]:
        if candidate in cols:
            primary_id = candidate
            break

    if primary_id:
        strategies.append([primary_id])

    secondary_id = None
    for candidate in ["ad_id", "post_id", "tweet_id"]:
        if candidate in cols:
            secondary_id = candidate
            break

    if primary_id and secondary_id:
        strategies.append([primary_id, secondary_id])

    for candidate in ["Type", "source", "lang", "Page Category",
                       "currency", "Video Share Status"]:
        if candidate in cols:
            strategies.append([candidate])
            break

    return strategies


# ─── Main ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 polars_stats.py <path_to_csv>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print(f"\nLoading: {file_path}")
    df = pl.read_csv(file_path, infer_schema_length=10000)
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
