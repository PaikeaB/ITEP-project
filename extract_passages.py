import os
import re
import csv
import pandas as pd
from keyword_analysis import KEYWORDS, KEYWORDS_DIRECT, KEYWORDS_INDIRECT, KEYWORD_CATEGORIES

# How many words of context to include on each side of a keyword hit
CONTEXT_WINDOW = 50

# Output directory for passage files
os.makedirs('data/passages', exist_ok=True)


def load_document(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def extract_passages(text, keyword, context_window=CONTEXT_WINDOW):
    """
    Find all occurrences of a keyword in text and return surrounding context.
    Returns a list of dicts with position, keyword, and passage.
    """
    words = text.split()
    text_lower = text.lower()
    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
    passages = []

    for match in re.finditer(pattern, text_lower):
        # Find which word index this character position corresponds to
        char_start = match.start()
        preceding_text = text[:char_start]
        word_index = len(preceding_text.split())

        # Slice context window
        start = max(0, word_index - context_window)
        end = min(len(words), word_index + context_window + 1)
        window_words = words[start:end]

        # Mark the keyword hit with brackets for easy scanning
        hit_offset = word_index - start
        if 0 <= hit_offset < len(window_words):
            window_words[hit_offset] = f"[[ {window_words[hit_offset]} ]]"

        passage = ' '.join(window_words)
        passages.append({
            'word_position': word_index,
            'keyword': keyword,
            'category': KEYWORD_CATEGORIES.get(keyword, 'unknown'),
            'passage': passage
        })

    return passages


def classify_placeholder():
    """
    Returns empty framing classification fields for manual coding.
    Coders should fill these in during manual review.
    """
    return {
        'framing_code': '',        # e.g. harm_justification, procedural_neutrality, community_displacement, conduit_framing, algorithmic_framing, expressive_diversity, legal_compliance
        'framing_notes': '',       # Free text notes from coder
        'coder_initials': '',      # NAH or CPB
        'confidence': '',          # high / medium / low
    }


# Load metadata
metadata_df = pd.read_csv('metadata/documents.csv')
all_passages = []

print("Extracting passages for manual framing classification\n")
print(f"Context window: ±{CONTEXT_WINDOW} words\n")

for _, row in metadata_df.iterrows():
    filepath = f"data/clean_text/{row['filename']}"

    if not os.path.exists(filepath):
        print(f"  Skipping (file not found): {filepath}")
        continue

    text = load_document(filepath)
    doc_passages = []

    for keyword in KEYWORDS:
        hits = extract_passages(text, keyword)
        for hit in hits:
            entry = {
                'platform': row['platform'],
                'document_type': row['document_type'],
                'filename': row['filename'],
                **hit,
                **classify_placeholder()
            }
            doc_passages.append(entry)
            all_passages.append(entry)

    # Also save a per-document passage file for easier manual review
    if doc_passages:
        doc_df = pd.DataFrame(doc_passages)
        safe_name = row['filename'].replace('.txt', '')
        doc_df.to_csv(f"data/passages/{safe_name}_passages.csv", index=False)
        print(f"{row['platform']} - {row['document_type']}: {len(doc_passages)} passages extracted")
    else:
        print(f"{row['platform']} - {row['document_type']}: 0 passages (no keyword hits)")

# Save master passage file
all_df = pd.DataFrame(all_passages)
all_df.to_csv('metadata/all_passages.csv', index=False)

print(f"\nTotal passages extracted: {len(all_passages)}")
print("Saved to: metadata/all_passages.csv")
print("Per-document files saved to: data/passages/\n")

# Print summary by platform and framing category
print("SUMMARY BY PLATFORM")
if not all_df.empty:
    summary = all_df.groupby(['platform', 'category']).size().unstack(fill_value=0)
    print(summary.to_string())

print("\n--- NEXT STEP ---")
print("Open metadata/all_passages.csv and fill in:")
print("  framing_code   — one of: harm_justification | procedural_neutrality |")
print("                           community_displacement | conduit_framing |")
print("                           algorithmic_framing | expressive_diversity |")
print("                           legal_compliance | other")
print("  framing_notes  — brief note on why you chose that code")
print("  coder_initials — NAH or CPB")
print("  confidence     — high / medium / low")
print("\nCode a sample of ~30 passages to start, then compare inter-rater reliability.")
