import requests
import pandas as pd
from datetime import datetime, timezone

URL = "https://api.coingecko.com/api/v5643/coins/markets"
PARAMS = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1}


def extract():
    """Fetch data from the API. Returns a list of dicts, or None if it fails."""
    try:
        response = requests.get(URL, params=PARAMS, timeout=30)
        response.raise_for_status()  # turns HTTP errors (404, 429, 500) into exceptions
        return response.json()
    except requests.exceptions.Timeout:
        print("ERROR: the API took too long to respond.")
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: the API returned a bad status: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: network problem: {e}")
    return None


def main():
    raw = extract()
    if raw is None:
        print("Stopping the pipeline: no data was extracted.")
        return

    df = pd.DataFrame(raw)
    df["ingested_at"] = datetime.now(timezone.utc)
    df.to_parquet("raw_crypto.parquet", index=False)

    clean = df[["id", "symbol", "current_price", "market_cap", "ingested_at"]].copy()
    clean["market_cap_billions"] = (clean["market_cap"] / 1e9).round(2)
    print(f"Loaded {len(clean)} coins")
    print(clean.head(10))


if __name__ == "__main__":
    main()