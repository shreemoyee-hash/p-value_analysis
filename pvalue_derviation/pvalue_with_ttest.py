import pandas as pd
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

# Load your data
# df = pd.read_excel('your_file.xlsx')  # Use this if working with Excel
df = pd.read_csv('../resources/raw_data.csv')  # Replace with actual file path

# Define the columns for both groups
treated_cols = ['Treated_1', 'Treated_2', 'Treated_3']
pbs_cols = ['PBS_1', 'PBS_2', 'PBS_3']

# Function to calculate t-statistic and p-value for each row
def calculate_stats(row):
    treated = row[treated_cols].values.astype(float)
    pbs = row[pbs_cols].values.astype(float)
    t_stat, p_val = ttest_ind(treated, pbs, equal_var=False)
    return pd.Series({'t_stat': t_stat, 'p_value': p_val})

# Apply function row-wise
results = df.apply(calculate_stats, axis=1)

# Adjust p-values using Benjamini-Hochberg (FDR)
adjusted = multipletests(results['p_value'], method='bonferroni', alpha=0.05)
results['p_adj'] = adjusted[1]

# Merge with original data
df_with_stats = pd.concat([df, results], axis=1)

# Save result
df_with_stats.to_csv('../resources/generated/ttest_bonferroni_results.csv', index=False)

print("Done. Results saved.")
