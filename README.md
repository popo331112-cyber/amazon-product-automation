# Amazon Product Scraper Automation

This Python script automates the process of finding products on Amazon based on specific criteria and saves the results to a CSV file.

## Features

- **Search by Keywords**: Scrapes products for multiple search terms.
- **Custom Filters**:
  - **BSR (Best Sellers Rank)**: < 100,000 (Adjustable)
  - **Sellers**: 5 to 20 (Adjustable)
  - **Rating**: > 3.5 stars
  - **Price**: > $20
- **Output**: Saves results to `amazon_products.csv`.

## Requirements

- Python 3.x
- Playwright

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/popo331112-cyber/amazon-product-automation.git
   cd amazon-product-automation
   ```

2. Install dependencies:
   ```bash
   pip install playwright
   playwright install chromium
   ```

## Usage

Run the script:
```bash
python amazon_scraper.py
```

The script will search for the configured keywords, visit each product page to check BSR and seller count, and save matching products to `amazon_products.csv`.

## Note

This script is for educational purposes. Please respect Amazon's Terms of Service and use responsibly.
