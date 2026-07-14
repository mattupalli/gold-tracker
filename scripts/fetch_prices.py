#!/usr/bin/env python3
"""
Gold Price Fetcher for Hyderabad, India
Fetches data from goodreturns.in and stores in JSON format
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
PRICES_FILE = DATA_DIR / "prices.json"
HYDERABAD_URL = "https://www.goodreturns.in/gold-rates/hyderabad.html"

# Headers to mimic browser request (keep minimal to avoid Cloudflare issues)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Custom headers for AJAX endpoint
AJAX_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "X-OIGT-Header": "GITPL",
}


def clean_price(price_str):
    """Clean price string and convert to integer"""
    # Remove currency symbols, commas, and whitespace
    cleaned = price_str.replace("₹", "").replace(",", "").replace(" ", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        return None


def fetch_current_prices(session):
    """Fetch current gold prices from Hyderabad page"""
    print("Fetching current prices...")
    response = session.get(HYDERABAD_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    prices = {}

    # Extract current prices using find() with id attribute
    # (CSS selectors don't work well with IDs starting with numbers)
    price_ids = {"24K": "24K-price", "22K": "22K-price", "18K": "18K-price"}
    
    for purity, element_id in price_ids.items():
        element = soup.find(id=element_id)
        if element:
            price_text = element.get_text(strip=True)
            prices[f"{purity}_per_gram"] = clean_price(price_text)

    # Extract change indicators from price cards
    price_cards = soup.select(".gr-price-card")
    for card in price_cards:
        card_text = card.get_text(strip=True)
        if "24K" in card_text:
            change_elem = card.select_one(".gr-change-pill")
            if change_elem:
                prices["24K_change"] = change_elem.get_text(strip=True)
        elif "22K" in card_text:
            change_elem = card.select_one(".gr-change-pill")
            if change_elem:
                prices["22K_change"] = change_elem.get_text(strip=True)

    # Extract per-weight table
    per_weight_table = soup.select_one("section.section-sec4 table")
    if per_weight_table:
        rows = per_weight_table.select("tbody tr")
        per_weight = {}
        for row in rows:
            cells = row.select("td")
            if len(cells) >= 4:
                weight = cells[0].get_text(strip=True)
                # Extract price only (first text node, before the span)
                price_24k = cells[1].find(string=True, recursive=False)
                price_22k = cells[2].find(string=True, recursive=False)
                price_18k = cells[3].find(string=True, recursive=False)
                
                per_weight[weight] = {
                    "24K": clean_price(price_24k) if price_24k else None,
                    "22K": clean_price(price_22k) if price_22k else None,
                    "18K": clean_price(price_18k) if price_18k else None,
                }
        prices["per_weight"] = per_weight

    return prices


def fetch_historical_table(session):
    """Fetch last 10 days historical table"""
    print("Fetching historical table...")
    response = session.get(HYDERABAD_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the historical table (last 10 days)
    historical_section = soup.select_one("section.gold_table_sec5")
    if not historical_section:
        return []

    table = historical_section.select_one("table")
    if not table:
        return []

    history = []
    rows = table.select("tbody tr")

    for row in rows:
        cells = row.select("td")
        if len(cells) >= 3:
            date_text = cells[0].get_text(strip=True)
            price_24k_text = cells[1].get_text(strip=True)
            price_22k_text = cells[2].get_text(strip=True)

            # Extract price before the parenthesis (change indicator)
            # Format: "₹14,280(-11)" or "₹14,280 (0)"
            price_24k_match = price_24k_text.split("(")[0].strip()
            price_22k_match = price_22k_text.split("(")[0].strip()
            
            price_24k = clean_price(price_24k_match)
            price_22k = clean_price(price_22k_match)

            # Only add if we have valid prices
            if price_24k is not None and price_22k is not None:
                history.append({
                    "date": date_text,
                    "24K": price_24k,
                    "22K": price_22k,
                })

    return history


def fetch_historical_price(session, date_str):
    """Fetch historical price for a specific date using AJAX endpoint"""
    print(f"Fetching price for {date_str}...")

    # First, visit the main page to get cookies
    session.get(HYDERABAD_URL, headers=HEADERS, timeout=30)

    # Then fetch the historical data
    params = {
        "gr_db_dynamic_content": "metal_past_price",
        "date": date_str,
    }

    response = session.get(
        HYDERABAD_URL,
        params=params,
        headers={**HEADERS, **AJAX_HEADERS},
        timeout=30,
    )

    if response.status_code == 200:
        try:
            data = response.json()
            return {
                "date": date_str,
                "24K": data.get("gold_price_24K"),
                "22K": data.get("gold_price_22K"),
                "18K": data.get("gold_price_18K"),
            }
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for {date_str}")
            return None
    else:
        print(f"Failed to fetch {date_str}: HTTP {response.status_code}")
        return None


def load_existing_data():
    """Load existing prices from JSON file"""
    if PRICES_FILE.exists():
        with open(PRICES_FILE, "r") as f:
            return json.load(f)
    return {"current": {}, "history": [], "last_updated": None}


def save_data(data):
    """Save prices to JSON file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(PRICES_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Data saved to {PRICES_FILE}")


def merge_history(existing_history, new_history):
    """Merge new history with existing, avoiding duplicates and nulls"""
    # Filter out items with null prices from both sources
    valid_existing = [item for item in existing_history if item.get("24K") is not None]
    valid_new = [item for item in new_history if item.get("24K") is not None]
    
    # Create a set of existing dates
    existing_dates = {item["date"] for item in valid_existing}

    # Add new items that don't exist
    merged = list(valid_existing)
    for item in valid_new:
        if item["date"] not in existing_dates:
            merged.append(item)
            existing_dates.add(item["date"])

    # Sort by date (newest first)
    merged.sort(key=lambda x: x["date"], reverse=True)

    # Keep only last 90 days
    return merged[:90]


def main():
    """Main function to fetch and store gold prices"""
    print("=" * 50)
    print("Gold Price Fetcher - Hyderabad, India")
    print("=" * 50)

    # Create session
    session = requests.Session()

    try:
        # Load existing data
        data = load_existing_data()

        # Fetch current prices
        current_prices = fetch_current_prices(session)

        # Fetch historical table (last 10 days)
        history_table = fetch_historical_table(session)

        # Update data
        data["current"] = current_prices
        data["history"] = merge_history(data.get("history", []), history_table)
        data["last_updated"] = datetime.now().isoformat()

        # Save data
        save_data(data)

        # Print summary
        print("\n" + "=" * 50)
        print("FETCH SUMMARY")
        print("=" * 50)
        print(f"24K Price: ₹{current_prices.get('24K_per_gram', 'N/A')}/gram")
        print(f"22K Price: ₹{current_prices.get('22K_per_gram', 'N/A')}/gram")
        print(f"18K Price: ₹{current_prices.get('18K_per_gram', 'N/A')}/gram")
        print(f"24K Change: {current_prices.get('24K_change', 'N/A')}")
        print(f"22K Change: {current_prices.get('22K_change', 'N/A')}")
        print(f"History records: {len(data['history'])}")
        print(f"Last updated: {data['last_updated']}")
        print("=" * 50)

        return 0

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
