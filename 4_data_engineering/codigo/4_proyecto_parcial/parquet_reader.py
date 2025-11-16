import polars as pl

if __name__ == "__main__":
    a = pl.read_parquet("btc_prices_2025-11-07T22:44:39.489548.parquet")
    print("output")
    print(a)
