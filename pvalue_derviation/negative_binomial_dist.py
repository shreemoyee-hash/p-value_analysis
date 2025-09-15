import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.genmod.families import NegativeBinomial
from statsmodels.stats.multitest import multipletests

# Load data
df = pd.read_csv("../resources/raw_data.csv")  # Replace with the actual file path

# Define group columns
treated_cols = ['Treated_1', 'Treated_2', 'Treated_3']
pbs_cols = ['PBS_1', 'PBS_2', 'PBS_3']
all_cols = treated_cols + pbs_cols

# Group labels
group_labels = ['Treated'] * 3 + ['PBS'] * 3


# Run Negative Binomial regression row-wise
def run_nb(row):
    counts = row[all_cols].values.astype(float)
    df_nb = pd.DataFrame({
        'count': counts,
        'group': group_labels
    })

    # Encode group (Treated=1, PBS=0)
    df_nb['group_code'] = df_nb['group'].map({'PBS': 0, 'Treated': 1})

    # Add intercept manually
    x = sm.add_constant(df_nb['group_code'])
    y = df_nb['count']

    try:
        model = sm.GLM(y, x, family=NegativeBinomial()).fit()
        p_val = model.pvalues['group_code']
    except Exception:
        p_val = np.nan

    return p_val


# Apply to each row
df['p_value_nb'] = df.apply(run_nb, axis=1)

# Adjust p-values using Benjamini-Hochberg
_, padj, _, _ = multipletests(df['p_value_nb'].dropna(), method='fdr_bh')

# Re-insert adjusted p-values correctly
df['p_adj_nb'] = np.nan
df.loc[df['p_value_nb'].notna(), 'p_adj_nb'] = padj

# Save results
df.to_csv("../resources/generated/neg_binom_results.csv", index=False)
print("Saved results to neg_binom_results.csv")
