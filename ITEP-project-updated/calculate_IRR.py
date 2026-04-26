import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs('visualizations', exist_ok=True)
os.makedirs('reports', exist_ok=True)

print("Loading coded data...")
nathan_codes = pd.read_csv('metadata/nathan_coded_passages.csv')
paikea_codes = pd.read_csv('metadata/paikea_coded_passages.csv')

# Rename framing_code to category for consistency
nathan_codes = nathan_codes.rename(columns={'framing_code': 'category', 'document_type': 'document'})
paikea_codes = paikea_codes.rename(columns={'framing_code': 'category', 'document_type': 'document'})

# Merge on passage_id
merged = nathan_codes.merge(paikea_codes, on='passage_id', suffixes=('_nathan', '_paikea'))

print(f"Loaded {len(merged)} passages for comparison\n")

# Calculate Cohen's Kappa
kappa = cohen_kappa_score(merged['category_nathan'], merged['category_paikea'])

print("="*60)
print("INTER-RATER RELIABILITY RESULTS")
print("="*60)
print(f"Cohen's Kappa: {kappa:.3f}")
print(f"Interpretation: ", end='')
if kappa < 0.20:
    print("Slight agreement")
elif kappa < 0.40:
    print("Fair agreement")
elif kappa < 0.60:
    print("Moderate agreement")
elif kappa < 0.80:
    print("Substantial agreement")
else:
    print("Almost perfect agreement")

total = len(merged)
agreements = (merged['category_nathan'] == merged['category_paikea']).sum()
percent_agreement = (agreements / total) * 100

print(f"\nPercentage Agreement: {percent_agreement:.1f}%")
print(f"Agreements: {agreements} out of {total}")
print(f"Disagreements: {total - agreements} out of {total}")
print("="*60 + "\n")

categories = sorted(set(merged['category_nathan'].unique()) | set(merged['category_paikea'].unique()))
cm = confusion_matrix(merged['category_nathan'], merged['category_paikea'], labels=categories)

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=categories, yticklabels=categories,
            cbar_kws={'label': 'Count'})
plt.title('Inter-Rater Agreement Confusion Matrix', fontsize=14, fontweight='bold')
plt.xlabel("Paikea's Coding", fontsize=12)
plt.ylabel("Nathan's Coding", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('visualizations/irr_confusion_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Confusion matrix saved to visualizations/irr_confusion_matrix.png")

disagreements = merged[merged['category_nathan'] != merged['category_paikea']].copy()
disagreements = disagreements[['passage_id', 'platform_nathan', 'document_nathan',
                                'category_nathan', 'category_paikea', 'passage_nathan']]
disagreements.columns = ['passage_id', 'platform', 'document',
                         'nathan_category', 'paikea_category', 'passage']
disagreements.to_csv('metadata/disagreements_to_resolve.csv', index=False)
print(f"✓ {len(disagreements)} disagreements saved to metadata/disagreements_to_resolve.csv")

with open('reports/irr_report.txt', 'w', encoding='utf-8') as f:
    f.write("INTER-RATER RELIABILITY REPORT\n")
    f.write("="*60 + "\n\n")
    f.write(f"Total passages coded: {total}\n")
    f.write(f"Agreements: {agreements}\n")
    f.write(f"Disagreements: {total - agreements}\n")
    f.write(f"Percentage Agreement: {percent_agreement:.1f}%\n")
    f.write(f"Cohen's Kappa: {kappa:.3f}\n\n")

    if kappa < 0.20:
        interpretation = "Slight agreement"
    elif kappa < 0.40:
        interpretation = "Fair agreement"
    elif kappa < 0.60:
        interpretation = "Moderate agreement"
    elif kappa < 0.80:
        interpretation = "Substantial agreement"
    else:
        interpretation = "Almost perfect agreement"

    f.write(f"Interpretation: {interpretation}\n\n")

    if len(disagreements) > 0:
        f.write("DISAGREEMENTS TO RESOLVE:\n")
        f.write("-"*60 + "\n\n")
        for idx, row in disagreements.iterrows():
            f.write(f"Passage ID: {row['passage_id']}\n")
            f.write(f"Platform: {row['platform']}\n")
            f.write(f"Document: {row['document']}\n")
            f.write(f"Nathan's code: {row['nathan_category']}\n")
            f.write(f"Paikea's code: {row['paikea_category']}\n")
            f.write(f"Text: {str(row['passage'])[:200]}...\n")
            f.write("-"*60 + "\n\n")

print("✓ Full IRR report saved to reports/irr_report.txt\n")
