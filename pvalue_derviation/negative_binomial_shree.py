import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial as DiscreteNB
from statsmodels.stats.multitest import multipletests
import warnings

# Suppress common model fitting warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning, HessianInversionWarning
warnings.simplefilter("ignore", ConvergenceWarning)
warnings.simplefilter("ignore", HessianInversionWarning)
warnings.simplefilter("ignore", RuntimeWarning)  # Suppress log(0) warnings

# Load data
df = pd.read_csv("../resources/raw_data.csv")  # Adjust path as needed

# Define group columns
treated_cols = ['Treated_1', 'Treated_2', 'Treated_3']
pbs_cols = ['PBS_1', 'PBS_2', 'PBS_3']
all_cols = treated_cols + pbs_cols

# Group labels
group_labels = ['Treated'] * 3 + ['PBS'] * 3

# Run Negative Binomial regression row-wise
def run_nb(row):
    counts = row[all_cols].values.astype(float)
    counts += 1e-6  # Add small constant to avoid log(0)

    # Skip rows with no variation
    if np.all(counts == counts[0]):
        return np.nan

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
            return np.nan
        if 'group_code' not in model.pvalues:
            return np.nan

        return model.pvalues['group_code']

    except Exception:
        return np.nan

# Apply model
df['p_value_nb'] = df.apply(run_nb, axis=1)

# Adjust p-values with FDR
valid_pvals = df['p_value_nb'].dropna()
_, padj, _, _ = multipletests(valid_pvals, method='fdr_bh')

# Reinsert adjusted p-values
df['p_adj_nb'] = np.nan
df.loc[df['p_value_nb'].notna(), 'p_adj_nb'] = padj

# Save results
df.to_csv("../resources/generated/neg_binom_results.csv", index=False)
print("Saved results to neg_binom_results.csv")
