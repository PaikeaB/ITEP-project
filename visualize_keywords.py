import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os

os.makedirs('visualizations', exist_ok=True)

df = pd.read_csv('metadata/keyword_frequency_analysis.csv')

# Color palette
COLOR_DIRECT   = '#2C6E91'   # dark blue  — explicit neutrality language
COLOR_INDIRECT = '#E07B39'   # burnt orange — indirect/euphemistic language
COLOR_TOTAL    = '#5B8C5A'   # muted green  — combined

TITLE_SIZE  = 14
LABEL_SIZE  = 12
TICK_SIZE   = 10

# ── Helper ────────────────────────────────────────────────────────────────────

def save(fig, name):
    path = f'visualizations/{name}.png'
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved: {path}')


# ── 1. Direct vs Indirect by Platform (grouped bar) ───────────────────────────

fig, ax = plt.subplots(figsize=(11, 6))

platforms  = df['platform'].unique()
x          = np.arange(len(platforms))
width      = 0.25

direct_avgs   = [df[df['platform'] == p]['per_1000_words_direct'].mean()   for p in platforms]
indirect_avgs = [df[df['platform'] == p]['per_1000_words_indirect'].mean() for p in platforms]
total_avgs    = [df[df['platform'] == p]['per_1000_words_total'].mean()    for p in platforms]

b1 = ax.bar(x - width, direct_avgs,   width, label='Direct terms',   color=COLOR_DIRECT,   alpha=0.9)
b2 = ax.bar(x,         indirect_avgs, width, label='Indirect terms',  color=COLOR_INDIRECT, alpha=0.9)
b3 = ax.bar(x + width, total_avgs,    width, label='Total',           color=COLOR_TOTAL,    alpha=0.9)

ax.set_title('Neutrality Term Frequency by Platform\n(Direct vs. Indirect Language)', fontsize=TITLE_SIZE, fontweight='bold')
ax.set_xlabel('Platform', fontsize=LABEL_SIZE)
ax.set_ylabel('Avg. Frequency per 1,000 Words', fontsize=LABEL_SIZE)
ax.set_xticks(x)
ax.set_xticklabels(platforms, fontsize=TICK_SIZE)
ax.legend(fontsize=TICK_SIZE)
ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
ax.grid(axis='y', linestyle='--', alpha=0.4)
fig.tight_layout()
save(fig, '1_direct_vs_indirect_by_platform')


# ── 2. Stacked bar: Direct vs Indirect proportion per document ────────────────

fig, ax = plt.subplots(figsize=(13, 6))

labels = [f"{r['platform']}\n{r['document_type'].replace('_', ' ')}" for _, r in df.iterrows()]
direct_vals   = df['per_1000_words_direct'].values
indirect_vals = df['per_1000_words_indirect'].values
x = np.arange(len(labels))

ax.bar(x, direct_vals,   label='Direct terms',  color=COLOR_DIRECT,   alpha=0.9)
ax.bar(x, indirect_vals, bottom=direct_vals,     label='Indirect terms', color=COLOR_INDIRECT, alpha=0.9)

ax.set_title('Neutrality Language per Document\n(Stacked: Direct + Indirect)', fontsize=TITLE_SIZE, fontweight='bold')
ax.set_xlabel('Document', fontsize=LABEL_SIZE)
ax.set_ylabel('Frequency per 1,000 Words', fontsize=LABEL_SIZE)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=8, ha='center')
ax.legend(fontsize=TICK_SIZE)
ax.grid(axis='y', linestyle='--', alpha=0.4)
fig.tight_layout()
save(fig, '2_stacked_by_document')


# ── 3. Indirect-to-Direct ratio per platform ──────────────────────────────────
# High ratio = platform relies more on euphemistic framing
# This is substantively interesting for the theoretical argument

fig, ax = plt.subplots(figsize=(9, 5))

ratios = []
for p in platforms:
    sub = df[df['platform'] == p]
    d = sub['per_1000_words_direct'].mean()
    i = sub['per_1000_words_indirect'].mean()
    ratio = i / d if d > 0 else float('inf')
    ratios.append(ratio)

bars = ax.bar(platforms, ratios, color=COLOR_INDIRECT, alpha=0.85)
ax.axhline(y=1, color='grey', linestyle='--', linewidth=1, label='1:1 ratio (equal direct/indirect)')

# Label bars
for bar, ratio in zip(bars, ratios):
    label = f'{ratio:.1f}x' if ratio != float('inf') else '∞'
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
            label, ha='center', va='bottom', fontsize=TICK_SIZE, fontweight='bold')

ax.set_title('Indirect-to-Direct Neutrality Language Ratio by Platform\n(Higher = more euphemistic framing)', fontsize=TITLE_SIZE, fontweight='bold')
ax.set_xlabel('Platform', fontsize=LABEL_SIZE)
ax.set_ylabel('Indirect / Direct ratio', fontsize=LABEL_SIZE)
ax.legend(fontsize=TICK_SIZE)
ax.grid(axis='y', linestyle='--', alpha=0.4)
fig.tight_layout()
save(fig, '3_indirect_to_direct_ratio')


# ── 4. Top 20 individual keyword hits (across all documents) ──────────────────

count_cols = [c for c in df.columns if c.startswith('count_')]
keyword_totals = df[count_cols].sum().sort_values(ascending=False).head(20)
keyword_labels = [c.replace('count_', '').replace('_', ' ') for c in keyword_totals.index]

fig, ax = plt.subplots(figsize=(12, 7))
colors = []
from keyword_analysis import KEYWORDS_DIRECT
direct_set = set(k.replace(' ', '_') for k in KEYWORDS_DIRECT)
for col in keyword_totals.index:
    kw = col.replace('count_', '')
    colors.append(COLOR_DIRECT if kw in direct_set else COLOR_INDIRECT)

ax.barh(keyword_labels[::-1], keyword_totals.values[::-1], color=colors[::-1], alpha=0.9)
ax.set_title('Top 20 Keywords by Total Occurrences (All Documents)', fontsize=TITLE_SIZE, fontweight='bold')
ax.set_xlabel('Total Occurrences', fontsize=LABEL_SIZE)
ax.grid(axis='x', linestyle='--', alpha=0.4)

# Legend patches
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=COLOR_DIRECT,   label='Direct term'),
                   Patch(facecolor=COLOR_INDIRECT, label='Indirect term')]
ax.legend(handles=legend_elements, fontsize=TICK_SIZE)
fig.tight_layout()
save(fig, '4_top20_keywords')


# ── 5. Heatmap: keyword category presence by platform ─────────────────────────
# Clusters indirect terms into their conceptual groups for comparison

from keyword_analysis import KEYWORDS_INDIRECT

INDIRECT_CLUSTERS = {
    'Enforcement':     ['remove', 'removal', 'taken down', 'violates our policies', 'against our policies',
                        'policy violation', 'enforce', 'enforcement', 'suspend', 'suspension',
                        'ban', 'restrict', 'restriction', 'limit', 'limitation'],
    'Harm/Safety':     ['harmful content', 'harmful behavior', 'safety', 'safe environment',
                        'protect', 'protection', 'well-being', 'wellbeing', 'health',
                        'integrity', 'trust and safety'],
    'Equal Apply':     ['consistent', 'consistently', 'apply equally', 'applied equally',
                        'regardless of', 'irrespective of', 'without regard to',
                        'equally', 'uniformly', 'across the board'],
    'Transparency':    ['transparent', 'transparency', 'accountable', 'accountability',
                        'appeal', 'appeals process', 'review', 'oversight', 'independent oversight'],
    'Community':       ['community standards', 'community guidelines', 'community rules',
                        'shared values', 'our community', 'everyone', 'all users', 'all people'],
    'Voice/Expression':['voice', 'diverse', 'diversity', 'inclusion', 'inclusive',
                        'belonging', 'pluralism', 'open conversation', 'open dialogue',
                        'give everyone a voice'],
    'Conduit':         ['host', 'hosting', 'platform for', 'we do not endorse',
                        'does not represent', 'user-generated', 'third-party content',
                        'not responsible for'],
    'Algorithmic':     ['algorithm', 'algorithmic', 'automated', 'automated systems',
                        'machine learning', 'classifier', 'signal', 'ranking', 'recommendation'],
    'Legal/Compliance':['applicable law', 'legal', 'comply', 'compliance',
                        'lawful', 'unlawful', 'illegal', 'jurisdiction'],
}

heatmap_data = {}
for platform in platforms:
    sub = df[df['platform'] == platform]
    heatmap_data[platform] = {}
    for cluster, terms in INDIRECT_CLUSTERS.items():
        total = 0
        for term in terms:
            col = f"count_{term.replace(' ', '_').replace('/', '_')}"
            if col in sub.columns:
                total += sub[col].sum()
        heatmap_data[platform][cluster] = total

heatmap_df = pd.DataFrame(heatmap_data).T  # platforms as rows, clusters as cols

fig, ax = plt.subplots(figsize=(13, 5))
im = ax.imshow(heatmap_df.values, aspect='auto', cmap='YlOrRd')

ax.set_xticks(np.arange(len(heatmap_df.columns)))
ax.set_yticks(np.arange(len(heatmap_df.index)))
ax.set_xticklabels(heatmap_df.columns, fontsize=9, rotation=30, ha='right')
ax.set_yticklabels(heatmap_df.index, fontsize=10)

# Annotate cells with counts
for i in range(len(heatmap_df.index)):
    for j in range(len(heatmap_df.columns)):
        val = int(heatmap_df.values[i, j])
        ax.text(j, i, str(val), ha='center', va='center', fontsize=9,
                color='white' if val > heatmap_df.values.max() * 0.6 else 'black')

plt.colorbar(im, ax=ax, label='Total occurrences')
ax.set_title('Indirect Neutrality Language by Conceptual Cluster and Platform\n(Raw counts across all documents)', fontsize=TITLE_SIZE, fontweight='bold')
fig.tight_layout()
save(fig, '5_cluster_heatmap_by_platform')


print("\nAll visualizations saved to visualizations/")
print("\nFiles generated:")
for i, name in enumerate(['1_direct_vs_indirect_by_platform', '2_stacked_by_document',
                           '3_indirect_to_direct_ratio', '4_top20_keywords',
                           '5_cluster_heatmap_by_platform'], 1):
    print(f"  {name}.png")

# ── 6. Absence Analysis: Operational vs. Neutrality Language ─────────────────

absence_df = pd.read_csv('metadata/absence_analysis.csv')

fig, ax = plt.subplots(figsize=(12, 6))

labels = [f"{r['platform']}\n{r['document_type'].replace('_', ' ')}" 
          for _, r in absence_df.iterrows()]
x = np.arange(len(labels))
width = 0.35

ax.bar(x - width/2, absence_df['per_1000_words_indirect_neutrality'], 
       width, label='Indirect neutrality language', color=COLOR_INDIRECT, alpha=0.9)
ax.bar(x + width/2, absence_df['per_1000_words_operational'], 
       width, label='Operational reality terms', color=COLOR_DIRECT, alpha=0.9)

ax.set_title('Rhetorical Presence vs. Operational Absence\n(Indirect neutrality language vs. terms describing actual platform governance)', 
             fontsize=TITLE_SIZE, fontweight='bold')
ax.set_xlabel('Document', fontsize=LABEL_SIZE)
ax.set_ylabel('Frequency per 1,000 Words', fontsize=LABEL_SIZE)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=8, ha='center')
ax.legend(fontsize=TICK_SIZE)
ax.grid(axis='y', linestyle='--', alpha=0.4)
fig.tight_layout()
save(fig, '6_absence_analysis')