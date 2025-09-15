import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA

# --- Load your data file ---
# Replace with the actual file name if reading from CSV or Excel
df = pd.read_csv("../resources/PCA_Full_Data.csv")

# --- Clean and prepare ---
# Remove 'gene_id' column and transpose the dataframe
expression_data = df.set_index('gene_id').T

# Check and convert to numeric (if any cells are strings)
expression_data = expression_data.apply(pd.to_numeric, errors='coerce')

# Drop samples (rows) with NaNs after conversion
expression_data = expression_data.dropna()

# Add sample group info: 'Treated' or 'PBS'
group_labels = ['Treated' if 'Treated' in sample else 'PBS' for sample in expression_data.index]

# --- PCA ---
pca = PCA(n_components=2)
components = pca.fit_transform(expression_data)

# Create DataFrame for PCA plot
pca_df = pd.DataFrame(components, columns=['PC1', 'PC2'])
pca_df['Sample'] = expression_data.index
pca_df['Group'] = group_labels

# --- Plot ---
plt.figure(figsize=(8, 6))
sns.scatterplot(data=pca_df, x='PC1', y='PC2', hue='Group', s=100)

# Optional: annotate sample names
for _, row in pca_df.iterrows():
    plt.text(row['PC1'] + 2, row['PC2'], row['Sample'], fontsize=9)

plt.title("PCA Plot of Samples - All Data")
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0] * 100:.2f}% variance)")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1] * 100:.2f}% variance)")
plt.grid(True)
plt.tight_layout()
plt.show()
