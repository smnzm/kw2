import requests
import pandas as pd
import time
from datetime import datetime
import os

# Replace with your own API key
api_key = "534c298aed22ae97a4a6a76e28d4b537a4fe6049"

# Function to read keywords from Excel file
def read_keywords_from_excel(filename):
    df = pd.read_excel(filename, sheet_name="Sheet1")  # Adjust sheet_name if needed
    keywords = df["keywords"].tolist()
    return keywords

# List of websites to monitor
websites = ["https://bama.ir/"]

# Function to get both ranks from a single API request
def get_ranks(keyword, website, api_key):
    headers = {"X-API-KEY": api_key}
    params = {
        "q": keyword,
        "gl": "ir",  # Iran
        "hl": "fa",  # Farsi language
        "num": 20
    }

    response = requests.get("https://google.serper.dev/search", headers=headers, params=params)

    try:
        results = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON for keyword '{keyword}'")
        return None, None  # Return None if API fails

    # Debugging: Print raw response
    print(f"Results for '{keyword}':", results)

    if "organic" not in results:
        return None, None  # No organic results found

    # Extract all rankings where the website appears
    ranks = [rank for rank, result in enumerate(results["organic"], start=1) if website in result.get("link", "")]

    # Return the first and second occurrence (if exists)
    rank_1 = ranks[0] if len(ranks) > 0 else None
    rank_2 = ranks[1] if len(ranks) > 1 else None

    return rank_1, rank_2

# Function to monitor keywords
def monitor_keywords(keywords, websites, api_key):
    data = []
    for keyword in keywords:
        for website in websites:
            rank_1, rank_2 = get_ranks(keyword, website, api_key)
            data.append({
                "keyword": keyword,
                "website": website,
                "rank_1": rank_1,
                "rank_2": rank_2,
                "timestamp": datetime.now()
            })
            time.sleep(0.5)  # Reduce API usage rate
    return data

# Save data to Excel file
def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

# Run the job immediately
def job():
    keywords = read_keywords_from_excel("keywords.xlsx")
    data = monitor_keywords(keywords, websites, api_key)
    save_to_excel(data, "keyword_ranks.xlsx")

# Run the script immediately
job()
