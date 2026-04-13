import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs('visualizations', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Load consensus-coded passages
coded = pd.read_csv('metadata/final_coded_passages.csv')

print("="*60)
print("FRAMING CATEGORY DISTRIBUTION")
print("="*60)

# Count by category
category_counts = coded['category'].value_counts()
print(category_counts)
print()

# Count by platform
platform_category = coded.groupby(['platform', 'category']).size().unstack(fill_value=0)

print("DISTRIBUTION BY PLATFORM")
print("="*60)
print(platform_category)
print("\n")

# Visualization 1: Overall distribution
fig, ax = plt.subplots(figsize=(10, 6))
category_counts.sort_values().plot(kind='barh', color='steelblue', ax=ax)
ax.set_title('Distribution of Framing Categories Across All Passages', 
             fontsize=14, fontweight='bold')
ax.set_xlabel('Number of Passages', fontsize=12)
ax.set_ylabel('Framing Category', fontsize=12)
plt.tight_layout()
plt.savefig('visualizations/framing_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/framing_distribution.png")

# Visualization 2: Stacked bar by platform
fig, ax = plt.subplots(figsize=(12, 6))
platform_category.plot(kind='bar', stacked=True, ax=ax, 
                        colormap='tab10', width=0.7)
ax.set_title('Framing Categories by Platform', fontsize=14, fontweight='bold')
ax.set_xlabel('Platform', fontsize=12)
ax.set_ylabel('Number of Passages', fontsize=12)
ax.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('visualizations/framing_by_platform.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/framing_by_platform.png")

# Visualization 3: Percentage breakdown
fig, ax = plt.subplots(figsize=(10, 8))
colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
wedges, texts, autotexts = ax.pie(category_counts.values, 
                                    labels=category_counts.index,
                                    autopct='%1.1f%%',
                                    colors=colors,
                                    startangle=90)
ax.set_title('Framing Category Distribution (Percentage)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('visualizations/framing_pie_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/framing_pie_chart.png")

# Export summary statistics
summary = {
    'total_passages': len(coded),
    'platforms': coded['platform'].nunique(),
    'categories': coded['category'].nunique(),
    'most_common_category': category_counts.index[0],
    'most_common_count': int(category_counts.iloc[0]),
    'most_common_percentage': f"{(category_counts.iloc[0] / len(coded) * 100):.1f}%"
}

with open('reports/framing_summary.txt', 'w', encoding='utf-8') as f:
    f.write("QUALITATIVE FRAMING ANALYSIS SUMMARY\n")
    f.write("="*60 + "\n\n")
    for key, value in summary.items():
        f.write(f"{key.replace('_', ' ').title()}: {value}\n")
    f.write("\n")
    f.write("CATEGORY COUNTS:\n")
    f.write("-"*60 + "\n")
    for category, count in category_counts.items():
        percentage = (count / len(coded)) * 100
        f.write(f"{category}: {count} ({percentage:.1f}%)\n")
    f.write("\n")
    f.write("PLATFORM BREAKDOWN:\n")
    f.write("-"*60 + "\n")
    f.write(platform_category.to_string())

print("✓ Saved: reports/framing_summary.txt\n")
