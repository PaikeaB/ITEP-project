import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
df = pd.read_csv('metadata/keyword_frequency_analysis.csv')
import os
os.makedirs('visualizations', exist_ok=True)
plt.figure(figsize=(10, 6))
platform_avg = df.groupby('platform')['per_1000_words'].mean().sort_values(ascending=False)
platform_avg.plot(kind='bar', color='steelblue')
plt.title('Average Neutrality Term Frequency by Platform', fontsize=14, fontweight='bold')
plt.xlabel('Platform', fontsize=12)
plt.ylabel('Frequency per 1,000 Words', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('visualizations/frequency_by_platform.png', dpi=300)
plt.close()


plt.figure(figsize=(12, 6))
doc_avg = df.groupby('document_type')['per_1000_words'].mean().sort_values(ascending=False)
doc_avg.plot(kind='bar', color='coral')
plt.title('Average Neutrality Term Frequency by Document Type', fontsize=14, fontweight='bold')
plt.xlabel('Document Type', fontsize=12)
plt.ylabel('Frequency per 1,000 Words', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('visualizations/frequency_by_document_type.png', dpi=300)
plt.close()


fig, ax = plt.subplots(figsize=(14, 7))
platforms = df['platform'].unique()
doc_types = df['document_type'].unique()
x = np.arange(len(platforms))
width = 0.35


for i, platform in enumerate(platforms):
    platform_data = df[df['platform'] == platform]
    for j, (_, row) in enumerate(platform_data.iterrows()):
        if j < 2: 
            ax.bar(i + (j * width) - width/2, row['per_1000_words'], 
                   width, label=row['document_type'] if i == 0 else '')

ax.set_xlabel('Platform', fontsize=12)
ax.set_ylabel('Frequency per 1,000 Words', fontsize=12)
ax.set_title('Neutrality Term Frequency Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(platforms)
ax.legend()
plt.tight_layout()
plt.savefig('visualizations/platform_comparison.png', dpi=300)
plt.close()

print("Visualizations saved to visualizations/ folder")