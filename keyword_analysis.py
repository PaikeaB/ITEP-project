import os
import re
import csv
import pandas as pd
from collections import Counter

KEYWORDS = [
    'neutral',
    'neutrality',
    'viewpoint neutral',
    'content neutral',
    'non-discrimination',
    'nondiscrimination',
    'discrimination',
    'free speech',
    'free expression',
    'freedom of expression',
    'public square',
    'open platform',
    'open discourse',
    'common carrier',
    'network neutrality',
    'open internet',
    'content moderation',
    'editorial discretion'
]


def load_document(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def count_keywords(text, keywords):
    text_lower = text.lower()
    counts = {}
    
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        count = len(re.findall(pattern, text_lower))
        counts[keyword] = count
    
    return counts

def calculate_frequency_per_1000(count, total_words):
    if total_words == 0:
        return 0
    return (count / total_words) * 1000


metadata_df = pd.read_csv('metadata/documents.csv')
results = []

print("Analyzing keyword frequencies\n")

for _, row in metadata_df.iterrows():
    filepath = f"data/clean_text/{row['filename']}"
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    text = load_document(filepath)
    word_count = len(text.split())
    keyword_counts = count_keywords(text, KEYWORDS)
    total_keyword_count = sum(keyword_counts.values())
    freq_per_1000 = calculate_frequency_per_1000(total_keyword_count, word_count)
    result = {
        'platform': row['platform'],
        'document_type': row['document_type'],
        'word_count': word_count,
        'total_neutrality_terms': total_keyword_count,
        'per_1000_words': round(freq_per_1000, 2)
    }

    for keyword, count in keyword_counts.items():
        result[f"count_{keyword.replace(' ', '_')}"] = count
    
    results.append(result)
    
    print(f"{row['platform']} - {row['document_type']}")
    print(f"  Words: {word_count:,}")
    print(f"  Neutrality terms: {total_keyword_count}")
    print(f"  Per 1,000 words: {freq_per_1000:.2f}\n")

results_df = pd.DataFrame(results)
results_df.to_csv('metadata/keyword_frequency_analysis.csv', index=False)
print("Results saved to metadata/keyword_frequency_analysis.csv")

print("SUMMARY TABLE")
print(results_df[['platform', 'document_type', 'word_count', 
                   'total_neutrality_terms', 'per_1000_words']].to_string(index=False))