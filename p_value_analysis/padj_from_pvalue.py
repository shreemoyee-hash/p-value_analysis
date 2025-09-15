from statsmodels.stats.multitest import multipletests

# Example: Replace this list with your own p-values (as floats)
raw_pvalues = []

# Apply Benjamini–Hochberg correction
# method='fdr_bh' corresponds to Benjamini-Hochberg FDR
rejected, pvals_corrected, _, _ = multipletests(raw_pvalues, alpha=0.05, method='fdr_bh')

# Print original and adjusted p-values
print(f"{'Index':<5} {'Raw p-value':<15} {'Adjusted p-value':<20} {'Reject H0':<10}")
for i, (raw, adj, rej) in enumerate(zip(raw_pvalues, pvals_corrected, rejected)):
    print(f"{i:<5} {raw:<15.10f} {adj:<20.10f} {rej}")

# Optional: Save to CSV
import pandas as pd

df = pd.DataFrame({'raw_p': raw_pvalues, 'adjusted_p': pvals_corrected, 'reject_null': rejected})
df.to_csv("../resources/generated/padj_results.csv", index=False)
