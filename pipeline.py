import logging
import time
import os
import requests
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()
API_URL = os.getenv("API_URL")
PER_PAGE = int(os.getenv("PER_PAGE", 50))

if not API_URL:
    raise ValueError("API_URL is missing from the .env file")

if not 1 <= PER_PAGE <= 250:
    raise ValueError("PER_PAGE must be between 1 and 250")

class CryptoExtractor:
    def __init__(self, url, per_page):
        self.url = url
        self.per_page = per_page

    def fetch(self):
        params = {"vs_currency": "usd", "order": "market_cap_desc",
                  "per_page": self.per_page, "page": 1}
        response = requests.get(self.url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()



RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def is_retryable(e):

    # Check temporary network errors
    if isinstance(
        e,
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError
        )
    ):
        return True

    # Check retryable HTTP status codes
    if (
        isinstance(e, requests.exceptions.HTTPError)
        and e.response is not None
    ):
        return e.response.status_code in RETRYABLE_STATUS

    # Do not retry other errors
    return False


def with_retries(func, max_attempts=4, base_delay=2):

    for attempt in range(1, max_attempts + 1):

        try:
            return func()

        except Exception as e:

            # Stop if we reached the limit or the error is permanent
            if attempt == max_attempts or not is_retryable(e):

                logger.error(
                    f"Giving up after {attempt} attempt(s): {e}"
                )

                raise

            # Calculate exponential waiting time
            wait = base_delay ** attempt

            logger.warning(
                f"Attempt {attempt} failed: {e}. "
                f"Retrying in {wait}s"
            )

            time.sleep(wait)


# def with_retries(func, max_attempts=4, base_delay=2):
#     for attempt in range(1, max_attempts + 1):
#         try:
#             return func()
#         except Exception as e:
#             if attempt == max_attempts:
#                 logger.error(f"Giving up after {attempt} attempts: {e}")
#                 raise
#             wait = base_delay ** attempt
#             logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {wait}s")
#             time.sleep(wait)


def main():
    logger.info("Pipeline started.")

    extractor = CryptoExtractor(API_URL, PER_PAGE)
    try:
        # STEP 1: EXTRACT
        raw_data = with_retries(extractor.fetch)

        # STEP 2: DATA QUALITY CHECK
        if not raw_data:
            raise ValueError("API returned no data")

        logger.info(f"Successfully fetched {len(raw_data)} coins from the API.")

        # STEP 3: CREATE DATAFRAME
        df = pd.DataFrame(raw_data)
        df["ingested_at"] = datetime.now(timezone.utc)
        # df.to_parquet("raw_crypto.parquet", index = False)

        # logger.info("Raw data saved to raw_crypto.parquet")

       # STEP 4: SAVE RAW DATA WITHOUT OVERWRITING
        out_dir = Path("data/raw")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Generate UTC timestamp
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        # Create a unique filename
        path = out_dir / f"crypto_{ts}.parquet"

        # Save raw data
        df.to_parquet(path, index=False)

        # Log the saved file
        logger.info(f"Raw data saved to {path}")

        logger.info("Pipeline completed successfully")

    except Exception:
        logger.exception("Pipeline failed")
        raise

if __name__ == "__main__":
    main()