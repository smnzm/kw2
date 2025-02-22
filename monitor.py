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
    df = pd.read_excel(filename, sheet_name="Sheet1")  # Adjust sheet_name as needed
    keywords = df["keywords"].tolist()
    return keywords



# List of websites to monitor
websites = ["bama.ir"]

# Function to get the rank of a website for a keyword
def get_rank(keyword, website, api_key):
    headers = {
        "X-API-KEY": api_key
    }
    params = {
        "q": keyword,
        "gl": "ir",  # Iran
        "hl": "fa",  # Farsi language
    }
    response = requests.get("https://google.serper.dev/search", headers=headers, params=params)
    results = response.json()

    # Print the results for debugging
    #print(f"Results for keyword '{keyword}':")
    #print(results)

    # Check if organic results exist in the response
    if "organic" not in results:
        print(f"No organic results found for keyword '{keyword}'")
        return None

    for rank, result in enumerate(results.get("organic", []), start=1):
        if website in result.get("link"):
            print(f"Found {website} at rank {rank} for keyword '{keyword}'")
            return rank
    print(f"{website} not found in top results for keyword '{keyword}'")
    return None

# Function to monitor keywords
def monitor_keywords(keywords, websites, api_key):
    data = []
    for keyword in keywords:
        for website in websites:
            rank = get_rank(keyword, website, api_key)
            data.append({
                "keyword": keyword,
                "website": website,
                "rank": rank,
                "timestamp": datetime.now()
            })
            time.sleep(2)  # To respect API rate limits
    return data

# Save data to CSV
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)

# Job to monitor keywords and save to CSV
def job():
    keywords = read_keywords_from_excel("keywords.xlsx")
    data = monitor_keywords(keywords, websites, api_key)
    save_to_csv(data, "keyword_ranks.csv")

# Schedule the job to run daily at 9 AM
#schedule.every().day.at("17:30").do(job)

#while True:
#    schedule.run_pending()
#    time.sleep(1)

job()
