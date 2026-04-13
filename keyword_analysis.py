import os
import re
import csv
import pandas as pd
from collections import Counter

# Original direct neutrality terms
KEYWORDS_DIRECT = [
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

# Expanded: indirect and euphemistic neutrality language
# These are terms platforms actually use when discussing neutrality-adjacent concepts
# without invoking "neutrality" explicitly. Grouped by conceptual cluster for transparency.
KEYWORDS_INDIRECT = [

    # --- Enforcement / removal framing ---
    # Platforms frame moderation as rule enforcement rather than editorial choice
    'remove',
    'removal',
    'taken down',
    'violates our policies',
    'against our policies',
    'policy violation',
    'enforce',
    'enforcement',
    'suspend',
    'suspension',
    'ban',
    'restrict',
    'restriction',
    'limit',
    'limitation',

    # --- Harm-based justification framing ---
    # Platforms justify interventions through harm/safety language, not viewpoint
    'harmful content',
    'harmful behavior',
    'safety',
    'safe environment',
    'protect',
    'protection',
    'well-being',
    'wellbeing',
    'health',
    'integrity',
    'trust and safety',

    # --- Equal/consistent application framing ---
    # Language signaling uniform, non-preferential application of rules
    'consistent',
    'consistently',
    'apply equally',
    'applied equally',
    'regardless of',
    'irrespective of',
    'without regard to',
    'equally',
    'uniformly',
    'across the board',

    # --- Transparency / accountability framing ---
    # Platforms invoke transparency to signal neutral process rather than neutral outcome
    'transparent',
    'transparency',
    'accountable',
    'accountability',
    'appeal',
    'appeals process',
    'review',
    'oversight',
    'independent oversight',

    # --- Community / shared standards framing ---
    # Neutrality displaced onto "community" rather than platform
    'community standards',
    'community guidelines',
    'community rules',
    'shared values',
    'our community',
    'everyone',
    'all users',
    'all people',

    # --- Voice / expression framing ---
    # Platforms affirm expressive diversity without committing to viewpoint neutrality
    'voice',
    'diverse',
    'diversity',
    'inclusion',
    'inclusive',
    'belonging',
    'pluralism',
    'open conversation',
    'open dialogue',
    'give everyone a voice',

    # --- Platform-as-passive-conduit framing ---
    # Language suggesting the platform is a neutral host, not an editor
    'host',
    'hosting',
    'platform for',
    'we do not endorse',
    'does not represent',
    'user-generated',
    'third-party content',
    'not responsible for',

    # --- Algorithmic / automated framing ---
    # Signals that decisions are procedural/automated rather than ideological
    'algorithm',
    'algorithmic',
    'automated',
    'automated systems',
    'machine learning',
    'classifier',
    'signal',
    'ranking',
    'recommendation',

    # --- Scope / jurisdictional limiting framing ---
    # Limits on what counts as platform's responsibility
    'applicable law',
    'legal',
    'comply',
    'compliance',
    'lawful',
    'unlawful',
    'illegal',
    'jurisdiction',
]

# Combined keyword set
KEYWORDS = KEYWORDS_DIRECT + KEYWORDS_INDIRECT

# Tag each keyword with its category for output
KEYWORD_CATEGORIES = {}
for k in KEYWORDS_DIRECT:
    KEYWORD_CATEGORIES[k] = 'direct'
for k in KEYWORDS_INDIRECT:
    KEYWORD_CATEGORIES[k] = 'indirect'


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

print("Analyzing keyword frequencies (expanded keyword set)\n")
print(f"Direct neutrality terms: {len(KEYWORDS_DIRECT)}")
print(f"Indirect/euphemistic terms: {len(KEYWORDS_INDIRECT)}")
print(f"Total keywords: {len(KEYWORDS)}\n")

for _, row in metadata_df.iterrows():
    filepath = f"data/clean_text/{row['filename']}"

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue

    text = load_document(filepath)
    word_count = len(text.split())
    keyword_counts = count_keywords(text, KEYWORDS)

    # Subtotals by category
    direct_total = sum(keyword_counts[k] for k in KEYWORDS_DIRECT)
    indirect_total = sum(keyword_counts[k] for k in KEYWORDS_INDIRECT)
    total_keyword_count = direct_total + indirect_total

    freq_per_1000_total = calculate_frequency_per_1000(total_keyword_count, word_count)
    freq_per_1000_direct = calculate_frequency_per_1000(direct_total, word_count)
    freq_per_1000_indirect = calculate_frequency_per_1000(indirect_total, word_count)

    result = {
        'platform': row['platform'],
        'document_type': row['document_type'],
        'word_count': word_count,
        'total_neutrality_terms': total_keyword_count,
        'direct_terms_count': direct_total,
        'indirect_terms_count': indirect_total,
        'per_1000_words_total': round(freq_per_1000_total, 2),
        'per_1000_words_direct': round(freq_per_1000_direct, 2),
        'per_1000_words_indirect': round(freq_per_1000_indirect, 2),
    }

    for keyword, count in keyword_counts.items():
        col = f"count_{keyword.replace(' ', '_').replace('/', '_')}"
        result[col] = count

    results.append(result)

    print(f"{row['platform']} - {row['document_type']}")
    print(f"  Words: {word_count:,}")
    print(f"  Direct neutrality terms: {direct_total} ({freq_per_1000_direct:.2f} per 1k)")
    print(f"  Indirect neutrality terms: {indirect_total} ({freq_per_1000_indirect:.2f} per 1k)")
    print(f"  Total: {total_keyword_count} ({freq_per_1000_total:.2f} per 1k)\n")

results_df = pd.DataFrame(results)
results_df.to_csv('metadata/keyword_frequency_analysis.csv', index=False)
print("Results saved to metadata/keyword_frequency_analysis.csv")

print("\nSUMMARY TABLE")
print(results_df[['platform', 'document_type', 'word_count',
                   'direct_terms_count', 'indirect_terms_count',
                   'per_1000_words_direct', 'per_1000_words_indirect',
                   'per_1000_words_total']].to_string(index=False))

# ── ABSENCE ANALYSIS ──────────────────────────────────────────────────────────
# These are terms describing how platforms actually operate that are
# systematically absent from their policy documents. The gap between
# indirect neutrality language (dense) and operational reality terms (absent)
# is the accountability foreclosure this project argues for.

KEYWORDS_OPERATIONAL = [
    'algorithmic curation',
    'shadow ban',
    'shadowbanning',
    'demonetize',
    'demonetization',
    'engagement optimization',
    'behavioral data',
    'ad targeting',
    'content suppression',
    'downrank',
    'downranking',
    'visibility reduction',
    'reach limitation',
    'audience restriction',
    'ad revenue',
    'monetization',
    'click-through',
    'impression',
    'engagement rate',
    'behavioral profiling',
    'data harvesting',
    'surveillance',
]

print("\n── ABSENCE ANALYSIS ──")
print("Operational reality terms vs. neutrality rhetoric\n")

absence_results = []

for _, row in metadata_df.iterrows():
    filepath = f"data/clean_text/{row['filename']}"
    if not os.path.exists(filepath):
        continue

    text = load_document(filepath)
    word_count = len(text.split())
    op_counts = count_keywords(text, KEYWORDS_OPERATIONAL)
    op_total = sum(op_counts.values())
    op_per_1000 = calculate_frequency_per_1000(op_total, word_count)

    # Pull indirect density from results_df for comparison
    indirect_per_1000 = results_df[
        (results_df['platform'] == row['platform']) &
        (results_df['document_type'] == row['document_type'])
    ]['per_1000_words_indirect'].values[0]

    absence_result = {
        'platform': row['platform'],
        'document_type': row['document_type'],
        'word_count': word_count,
        'operational_terms_count': op_total,
        'per_1000_words_operational': round(op_per_1000, 2),
        'per_1000_words_indirect_neutrality': round(indirect_per_1000, 2),
        'gap_ratio': round(indirect_per_1000 / op_per_1000, 1) if op_per_1000 > 0 else float('inf'),
    }
    for kw, count in op_counts.items():
        col = f"absent_{kw.replace(' ', '_')}"
        absence_result[col] = count

    absence_results.append(absence_result)

    print(f"{row['platform']} - {row['document_type']}")
    print(f"  Indirect neutrality terms: {indirect_per_1000:.2f} per 1k")
    print(f"  Operational reality terms: {op_per_1000:.2f} per 1k")
    gap = f"{indirect_per_1000/op_per_1000:.1f}x" if op_per_1000 > 0 else "∞"
    print(f"  Gap ratio: {gap}\n")

absence_df = pd.DataFrame(absence_results)
absence_df.to_csv('metadata/absence_analysis.csv', index=False)
print("Saved to metadata/absence_analysis.csv")