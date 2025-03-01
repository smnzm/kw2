import requests
import pandas as pd
import time
from datetime import datetime
import schedule
import os

# Replace with your own API key
api_key = "534c298aed22ae97a4a6a76e28d4b537a4fe6049"

# Function to read keywords from Excel file
def read_keywords_from_excel(filename):
    df = pd.read_excel(filename, sheet_name="Sheet1")  # Adjust sheet_name if needed
    keywords = df["keywords"].tolist()
    return keywords

# List of websites to monitor
websites = ["https://www.hamrah-mechanic.com/","https://bama.ir/"]

# Function to get all ranks of a website for a keyword (supports multiple occurrences)
def get_ranks(keyword, website, api_key):
    headers = {
        "X-API-KEY": api_key
    }
    max_pages = 2  # 2 pages = 20 results
    found_ranks = []

    for page in range(max_pages):
        params = {
            "q": keyword,
            "gl": "ir",  # Iran
            "hl": "fa",  # Farsi language
            "num": 20
        }
        response = requests.get("https://google.serper.dev/search", headers=headers, params=params)
        results = response.json()

        print(f"Results for keyword '{keyword}' (page {page + 1}):")
        print(results)

        if "organic" not in results:
            print(f"No organic results found for keyword '{keyword}' on page {page + 1}")
            break

        # Check all results for occurrences of the website
        for rank, result in enumerate(results.get("organic", []), start=1 + page * 10):
            if website in result.get("link"):
                found_ranks.append(rank)

        if len(results.get("organic", [])) < 10:
            break  # Stop if fewer than 10 results (end of results)

    # Ensure at least two rank values
    rank_1 = found_ranks[0] if len(found_ranks) > 0 else None
    rank_2 = found_ranks[1] if len(found_ranks) > 1 else None

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
                "rank_1": rank_1,  # First appearance
                "rank_2": rank_2,  # Second appearance
                "timestamp": datetime.now()
            })
            time.sleep(1)  # To respect API rate limits
    return data

# Save data to CSV
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)

# Job to monitor keywords and save to CSV
def job():
    keywords = read_keywords_from_excel("keywords.xlsx")
    data = monitor_keywords(keywords, websites, api_key)
    save_to_csv(data, "keyword_ranks.csv")

# Run the job instantly
job()
