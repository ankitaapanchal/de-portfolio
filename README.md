# Data Engineering Portfolio

Building production-style data pipelines for finance data.

## Day 1: Crypto Market Data Pipeline
- Extracts top 50 coins from the CoinGecko API
- Saves raw data to Parquet (ELT approach)
- Handles timeouts, HTTP errors, and network failures

## Technologies
Python, pandas, requests, pyarrow


## Day 2 – Making the Pipeline More Reliable
In Day 2, I improved my cryptocurrency data pipeline by adding production-style Python practices.

### Improvements
- **Logging:** Added INFO, WARNING, and ERROR logs to track pipeline execution and failures.
- **Retry handling:** Added selective retries for temporary network failures and retryable HTTP status codes, using exponential backoff.
- **Configuration management:** Moved the API URL and number of records into a `.env` file.
- **Object-oriented programming:** Created a `CryptoExtractor` class to organize API extraction logic.
- **Append-only raw storage:** Saved each pipeline run as a separate timestamped Parquet file in `data/raw/`.
- **Data quality validation:** Added a check to stop the pipeline if the API returns no records.

### Testing
- Ran the pipeline three times and checked that three separate raw Parquet files were created.
- Tested a 404 response to confirm that permanent errors are not retried.
- Tested a network failure to verify exponential retry delays of 2, 4, and 8 seconds.

### Run it
```bash
pip install -r requirements.txt
cp .env.example .env
python pipeline.py
```

### Technologies
Python, Requests, pandas, PyArrow, python-dotenv, Git, and GitHub.
