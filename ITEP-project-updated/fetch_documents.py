import os
import csv
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Create directories
os.makedirs('data/raw_html', exist_ok=True)
os.makedirs('data/clean_text', exist_ok=True)
os.makedirs('metadata', exist_ok=True)

documents = [
    {'platform': 'Meta', 'document_type': 'Terms_of_Service', 'url': 'https://www.facebook.com/terms.php', 'filename': 'meta_terms_of_service.txt'},
    {'platform': 'Meta', 'document_type': 'Community_Standards', 'url': 'https://www.facebook.com/communitystandards/', 'filename': 'meta_community_standards.txt'},
    {'platform': 'X', 'document_type': 'Terms_of_Service', 'url': 'https://legal.x.com/en/tos', 'filename': 'x_terms_of_service.txt'},
    {'platform': 'X', 'document_type': 'Rules_and_Policies', 'url': 'https://help.x.com/en/rules-and-policies/x-rules', 'filename': 'x_rules_and_policies.txt'},
    {'platform': 'YouTube', 'document_type': 'Terms_of_Service', 'url': 'https://www.youtube.com/t/terms', 'filename': 'youtube_terms_of_service.txt'},
    {'platform': 'YouTube', 'document_type': 'Community_Guidelines', 'url': 'https://support.google.com/youtube/answer/9288567', 'filename': 'youtube_community_guidelines.txt'},
    {'platform': 'Reddit', 'document_type': 'User_Agreement', 'url': 'https://www.redditinc.com/policies/user-agreement', 'filename': 'reddit_user_agreement.txt'},
    {'platform': 'Reddit', 'document_type': 'Content_Policy', 'url': 'https://www.redditinc.com/policies/content-policy', 'filename': 'reddit_content_policy.txt'}
]

def fetch_with_playwright():
    metadata_rows = []

    with sync_playwright() as p:
        # Launch browser - headless=True means no window pops up
        browser = p.chromium.launch(headless=True)
        # Use a realistic User-Agent and Viewport
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )

        for doc in documents:
            print(f"Fetching {doc['platform']} - {doc['document_type']}...")
            page = context.new_page()
            
            try:
                # Navigate and wait for the page to be "idle" (fully loaded)
                page.goto(doc['url'], wait_until="networkidle", timeout=60000)
                
                # Small extra buffer for JavaScript to finish rendering
                time.sleep(3) 
                
                html_content = page.content()
                
                # Save raw HTML
                html_path = f"data/raw_html/{doc['filename'].replace('.txt', '.html')}"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Parse and Clean
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove non-text elements
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 'button', 'input']):
                    element.decompose()
                
                # Focus on main content if possible to reduce noise
                main = soup.find('main') or soup.find('article') or soup.body
                text = main.get_text(separator=' ', strip=True)
                
                # Clean whitespace logic from your original pipeline
                text = ' '.join(text.split())
                
                # Save clean text
                clean_path = f"data/clean_text/{doc['filename']}"
                with open(clean_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                word_count = len(text.split())
                
                metadata_rows.append({
                    'platform': doc['platform'],
                    'document_type': doc['document_type'],
                    'date': '2025/2026', # Placeholders for your metadata
                    'source_url': doc['url'],
                    'filename': doc['filename'],
                    'word_count': word_count,
                    'fetch_date': datetime.now().strftime('%Y-%m-%d'),
                    'error': 'None'
                })
                print(f"  ✓ Saved. Word count: {word_count}")

            except Exception as e:
                print(f"  ✗ Error fetching {doc['platform']}: {str(e)[:100]}")
                metadata_rows.append({
                    'platform': doc['platform'],
                    'document_type': doc['document_type'],
                    'date': 'N/A',
                    'source_url': doc['url'],
                    'filename': doc['filename'],
                    'word_count': 0,
                    'fetch_date': datetime.now().strftime('%Y-%m-%d'),
                    'error': str(e)
                })
            
            finally:
                page.close()

        browser.close()

    # Save to CSV
    with open('metadata/documents.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['platform', 'document_type', 'date', 
                                               'source_url', 'filename', 'word_count', 
                                               'fetch_date', 'error'])
        writer.writeheader()
        writer.writerows(metadata_rows)

if __name__ == "__main__":
    fetch_with_playwright()
    print("\nAll documents processed. Proceed to keyword_analysis.py")