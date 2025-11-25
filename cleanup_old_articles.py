#!/usr/bin/env python3
"""
Cleanup Script: Remove articles older than 7 days from Firestore
This script deletes articles where publish_time is more than 7 days old
"""

import os
import sys
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("Firebase already initialized")
    except ValueError:
        # Initialize Firebase
        cred_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "firebase-credentials.json"
        )
        
        if not os.path.exists(cred_path):
            print(f"Error: Firebase credentials not found at {cred_path}")
            sys.exit(1)
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully")

def cleanup_old_articles(dry_run=True):
    """
    Delete articles older than 7 days from Firestore
    
    Args:
        dry_run: If True, only print what would be deleted without actually deleting
    """
    db = firestore.client()
    collection_ref = db.collection("news_articles")
    
    # Calculate 7 days ago timestamp
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_timestamp = seven_days_ago.timestamp()
    
    print(f"\n{'='*60}")
    print(f"Cleanup Articles Older Than 7 Days")
    print(f"{'='*60}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"7 days ago: {seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Threshold timestamp: {seven_days_timestamp}")
    print(f"Mode: {'DRY RUN (no actual deletion)' if dry_run else 'LIVE (will delete articles)'}")
    print(f"{'='*60}\n")
    
    # Query articles older than 7 days
    # Note: We need to fetch all and filter because Firestore has query limitations
    query = collection_ref.order_by("publish_time", direction=firestore.Query.ASCENDING)
    
    docs = query.stream()
    
    articles_to_delete = []
    articles_by_category = {}
    
    for doc in docs:
        # Skip metadata document
        if doc.id == "_metadata":
            continue
        
        article_data = doc.to_dict()
        publish_time = article_data.get("publish_time", 0)
        
        # Check if article is older than 7 days
        if publish_time < seven_days_timestamp:
            category = article_data.get("category", "Unknown")
            title = article_data.get("title", "No title")
            
            # Convert timestamp to readable date
            publish_date = datetime.fromtimestamp(publish_time).strftime("%Y-%m-%d %H:%M:%S")
            
            articles_to_delete.append({
                "doc_id": doc.id,
                "category": category,
                "title": title,
                "publish_time": publish_time,
                "publish_date": publish_date,
            })
            
            # Group by category for summary
            if category not in articles_by_category:
                articles_by_category[category] = 0
            articles_by_category[category] += 1
    
    # Print summary
    print(f"\nFound {len(articles_to_delete)} articles to delete:")
    print(f"{'-'*60}")
    for category, count in sorted(articles_by_category.items()):
        print(f"  {category}: {count} articles")
    print(f"{'-'*60}")
    
    if not articles_to_delete:
        print("\n✅ No articles older than 7 days found. Database is clean!")
        return 0
    
    # Show first 10 articles as examples
    print(f"\nFirst 10 articles to delete:")
    print(f"{'-'*60}")
    for i, article in enumerate(articles_to_delete[:10], 1):
        print(f"{i}. [{article['category']}] {article['title'][:50]}...")
        print(f"   Published: {article['publish_date']}")
    
    if len(articles_to_delete) > 10:
        print(f"   ... and {len(articles_to_delete) - 10} more articles")
    print(f"{'-'*60}")
    
    if dry_run:
        print(f"\n⚠️  DRY RUN: No articles were actually deleted.")
        print(f"To perform actual deletion, run with --execute flag")
        return len(articles_to_delete)
    
    # Confirm deletion in live mode
    print(f"\n⚠️  WARNING: This will permanently delete {len(articles_to_delete)} articles!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("❌ Deletion cancelled")
        return 0
    
    # Perform deletion
    print(f"\n🗑️  Deleting {len(articles_to_delete)} articles...")
    deleted_count = 0
    
    # Delete in batches of 500 (Firestore batch limit)
    batch_size = 500
    
    for i in range(0, len(articles_to_delete), batch_size):
        batch = db.batch()
        batch_articles = articles_to_delete[i:i + batch_size]
        
        for article in batch_articles:
            doc_ref = collection_ref.document(article["doc_id"])
            batch.delete(doc_ref)
        
        batch.commit()
        deleted_count += len(batch_articles)
        print(f"  Deleted {deleted_count}/{len(articles_to_delete)} articles...")
    
    print(f"\n✅ Successfully deleted {deleted_count} articles older than 7 days")
    
    # Update metadata
    try:
        metadata_ref = collection_ref.document("_metadata")
        metadata_ref.update({
            "last_cleanup_time": datetime.now().isoformat(),
            "last_cleanup_deleted": deleted_count,
        })
        print(f"✅ Updated _metadata with cleanup information")
    except Exception as e:
        print(f"⚠️  Could not update metadata: {e}")
    
    return deleted_count

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Cleanup articles older than 7 days from Firestore"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete articles (default is dry-run)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Delete articles older than this many days (default: 7)",
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Firebase
        initialize_firebase()
        
        # Run cleanup
        dry_run = not args.execute
        deleted_count = cleanup_old_articles(dry_run=dry_run)
        
        if dry_run and deleted_count > 0:
            print(f"\n💡 To actually delete these articles, run:")
            print(f"   python cleanup_old_articles.py --execute")
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

