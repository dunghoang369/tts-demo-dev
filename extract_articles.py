#!/usr/bin/env python3
"""
Extract title and full_text from articles_news.json and format them.
"""

import json


def extract_articles(json_file_path):
    """
    Read JSON file and extract title and full_text from each article.

    Args:
        json_file_path: Path to the JSON file containing articles

    Returns:
        Formatted string with all articles
    """
    # Read the JSON file
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract articles
    articles = data.get("articles", [])

    # Build the formatted string
    result_parts = []
    for article in articles:
        title = article.get("title", "")
        fulltext = article.get("full_text", "")

        # Format: "title: fulltext"
        result_parts.append(f"{title}: {fulltext}")

    # Join with double newline separator
    result = "\n\n".join(result_parts)

    return result


def main():
    # Path to the JSON file
    json_file = "articles_news.json"

    # Extract and format articles
    formatted_text = extract_articles(json_file)

    # Print the result
    print(formatted_text)

    # Optionally, save to a file
    output_file = "extracted_articles.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted_text)

    print(f"\n\n{'='*80}")
    print(f"Extraction complete! Output saved to '{output_file}'")
    print(f"Total articles processed: {formatted_text.count(': ')}")


if __name__ == "__main__":
    main()
