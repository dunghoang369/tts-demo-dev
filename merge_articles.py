#!/usr/bin/env python3
"""
Script to merge all article titles and summaries into a single formatted string.
Reads summarized_news.json and creates a merged string following the format:
- Title 1: Summary 1

- Title 2: Summary 2
...
"""

import json
from datetime import datetime

def merge_articles(input_file="summarized_news.json", output_file="merged_articles.json"):
    """Merge all articles into a single formatted string"""
    
    # Read summarized articles
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
        return
    
    articles = data.get("articles", [])
    fetch_date = data.get("fetch_date", "")
    
    print(f"Found {len(articles)} articles to merge")
    print(f"Fetch date: {fetch_date}\n")
    
    # Create merged string
    merged_parts = []
    for i, article in enumerate(articles, 1):
        title = article.get("title", "")
        summary = article.get("summary", "")
        
        # Format: - Title: Summary
        merged_parts.append(f"- {title}: {summary}")
        print(f"[{i}/{len(articles)}] Added: {title[:50]}...")
    
    # Join with double newline
    merged_content = "\n\n".join(merged_parts)
    
    # Get today's date in Vietnamese format
    today = datetime.now().strftime("%d/%m/%Y")
    
    # Create output with single Breaking News entry
    output_data = {
        "fetch_date": fetch_date,
        "merged_article": {
            "title": "Tổng hợp tin tức hôm nay",
            "content": merged_content,
            "category": "Breaking News",
            "date": today
        }
    }
    
    # Save to output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Successfully merged {len(articles)} articles")
    print(f"✓ Saved to {output_file}")
    print(f"\nMerged content preview (first 200 chars):")
    print(merged_content[:200] + "...")

if __name__ == "__main__":
    merge_articles()





