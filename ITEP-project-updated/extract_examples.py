import pandas as pd
import random

# Load coded passages
coded = pd.read_csv('metadata/final_coded_passages.csv')

# For each category, extract 2 representative examples
categories = sorted(coded['category'].unique())

examples = {}

for category in categories:
    category_passages = coded[coded['category'] == category]
    
    # Get up to 2 examples
    n_samples = min(2, len(category_passages))
    if n_samples > 0:
        samples = category_passages.sample(n=n_samples, random_state=42)
        examples[category] = samples[['platform', 'document', 'passage']].to_dict('records')

# Write to markdown file
with open('reports/framing_examples.md', 'w', encoding='utf-8') as f:
    f.write("# Representative Examples by Framing Category\n\n")
    f.write("*For inclusion in Data Section*\n\n")
    f.write("---\n\n")
    
    for category in sorted(examples.keys()):
        passages = examples[category]
        f.write(f"## {category}\n\n")
        
        for i, passage in enumerate(passages, 1):
            f.write(f"**Example {i}** (*{passage['platform']} - {passage['document']}*)\n\n")
            f.write(f"> {passage['passage']}\n\n")
        
        f.write("---\n\n")

print("✓ Representative examples saved to reports/framing_examples.md\n")