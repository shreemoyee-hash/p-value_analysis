import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multitest import multipletests

# Load your data
df = pd.read_csv("../resources/raw_data.csv")  # Replace with actual file path

# Group and replicate column names
treated_cols = ['Treated_1', 'Treated_2', 'Treated_3']
pbs_cols = ['PBS_1', 'PBS_2', 'PBS_3']


# Combine into one structure for ANOVA
def run_anova(row):
    data = []

    # Add Treated values
    for i, col in enumerate(treated_cols):
        data.append({'value': row[col], 'group': 'Treated', 'replicate': f'Rep{i + 1}'})

    # Add PBS values
    for i, col in enumerate(pbs_cols):
        data.append({'value': row[col], 'group': 'PBS', 'replicate': f'Rep{i + 1}'})

    anova_df = pd.DataFrame(data)

    # Build model: two-way ANOVA with interaction
    model = ols('value ~ C(group) + C(replicate)', data=anova_df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    p_val = anova_table.loc["C(group)", "PR(>F)"]
    return p_val


# Apply ANOVA row-wise
df['p_value_anova'] = df.apply(run_anova, axis=1)

# Adjust p-values (Benjamini-Hochberg FDR)
_, padj, _, _ = multipletests(df['p_value_anova'], method='fdr_bh', alpha=0.05)
df['p_adj_anova'] = padj

# Save results
df.to_csv("../resources/generated/anova_results.csv", index=False)
print("Saved ANOVA results to anova_results.csv")