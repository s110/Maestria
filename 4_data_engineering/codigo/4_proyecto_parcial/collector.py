import asyncio
import aiohttp
import polars as pl
from datetime import datetime, timedelta

# -- Configuration --
# You can change these values
COLLECTION_INTERVAL_SECONDS = 10  # X: Interval to fetch data
TOTAL_DURATION_MINUTES = 1  # Y: Total time to run the script

# -- Script --
API_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
OUTPUT_FILE = f"btc_prices_{datetime.now().isoformat()}.parquet"


async def collect_data():
    """
    Collects data from the Binance API asynchronously for a specified duration
    and saves it to a Parquet file using polars.
    """
    print(f"Starting data collection for {TOTAL_DURATION_MINUTES} minute(s).")
    print(f"Data will be fetched every {COLLECTION_INTERVAL_SECONDS} second(s).")

    collected_data = []
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=TOTAL_DURATION_MINUTES)

    async with aiohttp.ClientSession() as session:
        while datetime.now() < end_time:
            loop_start_time = asyncio.get_event_loop().time()

            try:
                async with session.get(API_URL) as response:
                    response.raise_for_status()  # Raise an exception for bad status codes
                    data = await response.json()

                    # Add a timestamp to the collected data
                    data["timestamp"] = datetime.now()
                    collected_data.append(data)

                    print(
                        f"Collected: {data['symbol']} - {data['price']} at {data['timestamp'].isoformat()}"
                    )

            except aiohttp.ClientError as e:
                print(f"An error occurred while requesting data: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            # Wait for the next interval
            elapsed_time = asyncio.get_event_loop().time() - loop_start_time
            sleep_time = max(0, COLLECTION_INTERVAL_SECONDS - elapsed_time)
            await asyncio.sleep(sleep_time)

    if not collected_data:
        print("No data was collected. Exiting.")
        return

    # Convert to polars DataFrame and save as Parquet
    df = pl.DataFrame(collected_data)
    # Cast columns to appropriate types for better storage
    df = df.with_columns(
        pl.col("timestamp").cast(pl.Datetime), pl.col("price").cast(pl.Float64)
    )

    try:
        df.write_parquet(OUTPUT_FILE)
        print(
            f"\nData collection finished. Saved {len(df)} records to '{OUTPUT_FILE}'."
        )
    except Exception as e:
        print(f"An error occurred while saving the Parquet file: {e}")


if __name__ == "__main__":
    asyncio.run(collect_data())
