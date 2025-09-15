import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial as DiscreteNB
from statsmodels.stats.multitest import multipletests
import warnings

# Suppress convergence and Hessian warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning, HessianInversionWarning
warnings.simplefilter("ignore", ConvergenceWarning)
warnings.simplefilter("ignore", HessianInversionWarning)
warnings.simplefilter("ignore", RuntimeWarning)

# Load data
df = pd.read_csv("../resources/raw_data.csv")  # Replace with your actual path

# Define group columns
treated_cols = ['Treated_1', 'Treated_2', 'Treated_3']
pbs_cols = ['PBS_1', 'PBS_2', 'PBS_3']
all_cols = treated_cols + pbs_cols

# Group labels
group_labels = ['Treated'] * 3 + ['PBS'] * 3

# Run Negative Binomial regression row-wise + log2FC
def run_nb(row):
    counts = row[all_cols].values.astype(float)
    counts += 1e-6  # Avoid zeros

    # Compute log2 fold change
    treated_mean = np.mean(row[treated_cols].values.astype(float)) + 1e-6
    pbs_mean = np.mean(row[pbs_cols].values.astype(float)) + 1e-6
    log2fc = np.log2(treated_mean / pbs_mean)

    # Skip rows with no variation
    if np.all(counts == counts[0]):
        return pd.Series([np.nan, log2fc])

    df_nb = pd.DataFrame({
        'count': counts,
        'group': group_labels
    })
    df_nb['group_code'] = df_nb['group'].map({'PBS': 0, 'Treated': 1})

    x = sm.add_constant(df_nb['group_code'])
    y = df_nb['count']

    try:
        model = DiscreteNB(y, x).fit(disp=0, maxiter=1000)

        if not model.mle_retvals.get('converged', False):
            return pd.Series([np.nan, log2fc])
        if 'group_code' not in model.pvalues:
            return pd.Series([np.nan, log2fc])

        return pd.Series([model.pvalues['group_code'], log2fc])

    except Exception:
        return pd.Series([np.nan, log2fc])

# Apply model and log2FC
df[['p_value_nb', 'log2FC']] = df.apply(run_nb, axis=1)

# Adjust p-values using Benjamini-Hochberg
valid_pvals = df['p_value_nb'].dropna()
_, padj, _, _ = multipletests(valid_pvals, method='fdr_bh')

# Insert adjusted p-values
df['p_adj_nb'] = np.nan
df.loc[df['p_value_nb'].notna(), 'p_adj_nb'] = padj

# Save results
df.to_csv("../resources/generated/neg_binom_results.csv", index=False)
print("Saved results to neg_binom_results.csv")
