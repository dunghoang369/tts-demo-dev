#!/usr/bin/env python3
"""
Script to retrieve the first 5 latest articles from Firestore.
Queries the news_articles collection, sorts by publish_time (descending),
and prints all fields to console.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


def init_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        cred = credentials.Certificate("firebase-credentials.json")
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None


def retrieve_latest_articles(db, limit=5):
    """Retrieve the latest articles from Firestore, sorted by publish_time"""
    try:
        # Query the news_articles collection
        collection_ref = db.collection("news_articles")

        # Order by publish_time descending and limit to 5
        query = collection_ref.order_by(
            "publish_time", direction=firestore.Query.DESCENDING
        ).limit(limit)

        # Execute query
        docs = query.stream()

        articles = []
        for doc in docs:
            # Skip metadata document
            if doc.id == "_metadata":
                continue

            article_data = doc.to_dict()
            article_data["doc_id"] = doc.id
            articles.append(article_data)

        return articles
    except Exception as e:
        print(f"Error retrieving articles from Firestore: {e}")
        return []


def format_timestamp(timestamp):
    """Convert timestamp to readable date/time format"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return str(timestamp)


def display_articles(articles):
    """Display articles in a formatted way"""
    if not articles:
        print("No articles found in Firestore.")
        return

    print("=" * 100)
    print(f"Retrieved {len(articles)} Latest Articles from Firestore")
    print("=" * 100)
    print()

    for i, article in enumerate(articles, 1):
        print(f"[{i}] {article.get('title', 'No title')}")
        print(f"    Document ID: {article.get('doc_id', 'N/A')}")
        print(f"    Category: {article.get('category', 'N/A')}")
        print(f"    URL: {article.get('url', 'N/A')}")

        # Format publish_time
        publish_time = article.get("publish_time", 0)
        if publish_time:
            formatted_time = format_timestamp(publish_time)
            print(f"    Published: {formatted_time} (timestamp: {publish_time})")
        else:
            print(f"    Published: N/A")

        print(f"    Fetch Date: {article.get('fetch_date', 'N/A')}")

        # Display summary
        summary = article.get("summary", "")
        if summary:
            print(f"    Summary: {summary}")
        else:
            print(f"    Summary: N/A")

    print(f"✓ Successfully retrieved and displayed {len(articles)} articles")


def main():
    """Main function to retrieve and display articles from Firestore"""
    # Initialize Firebase
    db = init_firebase()
    if not db:
        print(
            "Failed to initialize Firebase. Please ensure firebase-credentials.json exists."
        )
        return

    print("Connecting to Firestore...")
    print()

    # Retrieve latest 5 articles
    articles = retrieve_latest_articles(db, limit=5)

    # Display articles
    display_articles(articles)


if __name__ == "__main__":
    main()
