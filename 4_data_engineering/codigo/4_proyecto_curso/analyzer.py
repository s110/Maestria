import polars as pl
import os

# -- Configuration --
# Directory where your Parquet files are stored.
# The script will search for any file ending with .parquet
INPUT_DIR = "."
# Path for the output Delta Lake table.
OUTPUT_DELTA_TABLE = "btc_daily_stats.delta"


def analyze_data():
    """
    Reads all Parquet files from the input directory, calculates daily
    statistics, and writes the result to a Delta Lake table.
    """
    parquet_files_path = os.path.join(INPUT_DIR, "*.parquet")
    print(f"Searching for Parquet files in: {parquet_files_path}")

    try:
        # Lazily scan all parquet files to handle large datasets
        lazy_df = pl.scan_parquet(parquet_files_path)
    except Exception as e:
        print(f"An error occurred while reading Parquet files: {e}")
        print("Please ensure there are Parquet files in the specified directory.")
        return

    print("Calculating daily statistics...")

    # Group by day and calculate descriptive statistics
    daily_stats_df = (
        lazy_df.group_by(pl.col("timestamp").dt.date().alias("date"))
        .agg(
            pl.col("price").min().alias("min_price"),
            pl.col("price").max().alias("max_price"),
            pl.col("price").mean().alias("mean_price"),
            pl.col("price").median().alias("median_price"),
            pl.col("price").std().alias("std_dev_price"),
            pl.col("price").var().alias("variance_price"),
            pl.col("price").quantile(0.25).alias("q1_price"),
            pl.col("price").quantile(0.75).alias("q3_price"),
            pl.col("price").first().alias("open_price"),
            pl.col("price").last().alias("close_price"),
            pl.count().alias("record_count"),
        )
        .sort("date")
    )

    # Calculate Interquartile Range (IQR)
    daily_stats_df = daily_stats_df.with_columns(
        (pl.col("q3_price") - pl.col("q1_price")).alias("iqr_price")
    )

    # Collect the results from the lazy evaluation
    final_df = daily_stats_df.collect()

    if final_df.is_empty():
        print("No data found to process. Exiting.")
        return

    print("Daily statistics calculated:")
    print(final_df)

    try:
        print(f"\nWriting data to Delta Lake table: {OUTPUT_DELTA_TABLE}")
        final_df.write_delta(OUTPUT_DELTA_TABLE, mode="overwrite")
        print("Successfully wrote to Delta Lake table.")
    except Exception as e:
        print(f"An error occurred while writing to the Delta Lake table: {e}")


if __name__ == "__main__":
    analyze_data()
