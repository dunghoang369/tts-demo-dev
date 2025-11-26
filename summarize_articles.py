#!/usr/bin/env python3
"""
Script to summarize news articles using the summarization API.
Reads articles_news.json, calls the summarize API for each article's full_text,
and saves the summaries to summarized_news.json.
"""

import re
import json
import time
import requests
from datetime import datetime
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# API configuration
SUMMARIZE_API_URL = "http://115.79.192.192:19977/summarize"
GET_NEWS_API_URL = "http://115.79.192.192:19977/get_news"
GET_NEWS_CATEGORY_API_URL = "http://115.79.192.192:19977/get_news_type"
API_KEY = "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu"


# Category mapping based on article content
def init_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        cred = credentials.Certificate("firebase-credentials.json")
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None


def upload_to_firestore(db, news_items, fetch_metadata):
    """Upload news items to Firestore collection with metadata"""
    try:
        # Create a collection reference
        collection_ref = db.collection("news_articles")

        # Store metadata document
        metadata_doc = {
            "fetch_date": fetch_metadata.get("fetch_date", datetime.now().isoformat()),
            "total_items": len(news_items),
            "news_type": fetch_metadata.get("news_type", "thoi-su"),
            "timestamp": firestore.SERVER_TIMESTAMP,
        }

        # Add metadata document
        collection_ref.document("_metadata").set(metadata_doc, merge=True)

        # Upload each news item
        for item in news_items:
            # Generate doc ID from timestamp and title hash
            doc_id = f"{item['publish_time']}_{hash(item['title']) % 10000}"
            collection_ref.document(doc_id).set(item)
            print(f"Uploaded: {item['title'][:50]}...")

        print(f"\nSuccessfully uploaded {len(news_items)} items to Firestore")
        return True
    except Exception as e:
        print(f"Error uploading to Firestore: {e}")
        return False


def summarize_text(full_text):
    """Call the summarize API to get a summary of the text"""
    headers = {
        "accept": "application/json",
        "api-key": API_KEY,
        "Content-Type": "application/json",
    }

    data = {"content": full_text}

    try:
        response = requests.post(
            SUMMARIZE_API_URL, headers=headers, json=data, timeout=120
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == 0 and "summary" in result:
            return result["summary"]
        else:
            print(f"API returned non-zero status: {result}")
            return None
    except Exception as e:
        print(f"Error calling summarize API: {e}")
        return None


def main():
    # Read articles from JSON file
    try:
        with open("articles_news.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: articles_news.json not found")
        return

    articles = data.get("articles", [])
    fetch_date = data.get("fetch_date", "")

    print(f"Found {len(articles)} articles to summarize")
    print(f"Fetch date: {fetch_date}\n")

    summarized_articles = []

    for i, article in enumerate(articles, 1):
        title = article.get("title", "")
        full_text = article.get("full_text", "")
        publish_time = article.get("publish_time", 0)

        # Convert timestamp to date string
        if publish_time:
            date_obj = datetime.fromtimestamp(publish_time)
            date_str = date_obj.strftime("%d/%m/%Y")
        else:
            date_str = "17/11/2024"

        print(f"[{i}/{len(articles)}] Summarizing: {title[:50]}...")

        # Call summarize API
        summary = summarize_text(full_text)

        if summary:
            # Determine category
            category = categorize_article(title, full_text)

            summarized_article = {
                "title": title,
                "summary": summary,
                "category": category,
                "date": date_str,
            }
            summarized_articles.append(summarized_article)
            print(f"  ✓ Summary: {summary[:80]}...")
            print(f"  Category: {category}")
        else:
            print(f"  ✗ Failed to summarize")

        print()

    # Save to output file
    output_data = {
        "fetch_date": fetch_date,
        "total_articles": len(summarized_articles),
        "articles": summarized_articles,
    }

    with open("summarized_news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Successfully summarized {len(summarized_articles)} articles")
    print(f"✓ Saved to summarized_news.json")


def get_news(news_type, limit=5):
    """Get news from the API"""
    headers = {
        "accept": "application/json",
        "api-key": API_KEY,
        "Content-Type": "application/json",
    }

    data = {"news_type": news_type, "limit": limit}
    response = requests.post(GET_NEWS_API_URL, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    return response.json()


def get_news_category():
    headers = {
        "accept": "application/json",
        "api-key": API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.get(GET_NEWS_CATEGORY_API_URL, headers=headers, timeout=120)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # Initialize Firebase
    db = init_firebase()
    if not db:
        print("Failed to initialize Firebase. Exiting.")
        exit(1)

    # Get news category
    news_category = get_news_category()

    # Get news from API
    news_type = "thoi-su"
    category = news_category.get(news_type).get("category", "")
    if not category:
        print(f"Error: Category not found for news type: {news_type}")
        exit(1)

    news = get_news(news_type)
    results = news.get("results", [])

    news_items = []
    fetch_date = datetime.now().isoformat()

    for result in results.get("articles", []):
        title = result.get("title", "")
        publish_datetime = result.get("publish_time", "")

        import pdb

        pdb.set_trace()
        # Extract and parse date/time
        date_match = re.search(r"(\d{2})/(\d{2})/(\d{4})", publish_datetime)
        publish_date = (
            f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"
            if date_match
            else ""
        )

        time_match = re.search(r"(\d{2}):(\d{2})", publish_datetime)
        publish_time = (
            f"{time_match.group(1)}:{time_match.group(2)}" if time_match else ""
        )

        full_text = result.get("full_text", "")
        date_time = pd.to_datetime(f"{publish_date} {publish_time}")
        timestamp = int(date_time.timestamp())
        url = result.get("url", "")

        # Summarize the article
        summary = summarize_text(full_text)

        item = {
            "title": title,
            "full_text": full_text,
            "summary": summary,
            "publish_time": timestamp,
            "url": url,
            "category": category,
            "fetch_date": fetch_date,
        }

        news_items.append(item)
        print(f"Processed: {title[:50]}...")
        print(f"  Category: {category}")
        print(f"  Summary: {summary[:80] if summary else 'N/A'}...")
        print("-" * 100)

    # Upload to Firestore
    metadata = {"fetch_date": fetch_date, "news_type": "thoi-su"}
    upload_to_firestore(db, news_items, metadata)
