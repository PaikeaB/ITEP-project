import pandas as pd

print("Creating consensus dataset from individual codings...\n")

nathan = pd.read_csv('metadata/nathan_coded_passages.csv')
paikea = pd.read_csv('metadata/paikea_coded_passages.csv')

merged = nathan.merge(paikea, on='passage_id', suffixes=('_nathan', '_paikea'))

consensus = []

for idx, row in merged.iterrows():
    if row['category_nathan'] == row['category_paikea']:
        category = row['category_nathan']
        resolution = 'agreement'
    else:
        category = row['category_paikea']
        resolution = 'disagreement_resolved_to_paikea'

    consensus.append({
        'passage_id': row['passage_id'],
        'platform': row['platform_nathan'],
        'document': row['document_nathan'],
        'passage': row['passage_nathan'],
        'category': category,
        'resolution_method': resolution
    })

consensus_df = pd.DataFrame(consensus)
consensus_df.to_csv('metadata/final_coded_passages.csv', index=False)

print(f"✓ Consensus dataset created: {len(consensus_df)} passages")
print(f"  - Agreements: {len(consensus_df[consensus_df['resolution_method'] == 'agreement'])}")
print(f"  - Resolved disagreements: {len(consensus_df[consensus_df['resolution_method'] != 'agreement'])}")
print("✓ Saved to metadata/final_coded_passages.csv\n")
