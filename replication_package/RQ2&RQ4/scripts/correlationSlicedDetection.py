import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import scipy.stats as stats

plt.style.use('default')
sns.set_palette("husl")

df = pd.read_excel('dataset_quantum_code_smells_sliced.xlsx')
smell_columns = ['CG', 'ROC', 'NC', 'LC', 'IM', 'IdQ', 'IQ', 'LPQ']

prevalence_results = []
for slice_id, slice_df in df.groupby('Slice ID'):
    total_repos = len(slice_df)
    for smell in smell_columns:
        affected_repos = (slice_df[smell] > 0).sum()
        prevalence = (affected_repos / total_repos) * 100
        prevalence_results.append({
            'Slice ID': slice_id,
            'Smell': smell,
            'Prevalence': prevalence
        })

prevalence_df = pd.DataFrame(prevalence_results)

por_results = []
for slice_id, slice_df in df.groupby('Slice ID'):
    for col1, col2 in combinations(smell_columns, 2):
        a = ((slice_df[col1] > 0) & (slice_df[col2] > 0)).sum()
        b = ((slice_df[col1] > 0) & (slice_df[col2] == 0)).sum()
        c = ((slice_df[col1] == 0) & (slice_df[col2] > 0)).sum()
        d = ((slice_df[col1] == 0) & (slice_df[col2] == 0)).sum()
        
        table = [[a, b], [c, d]]
        try:
            chi2, p_value, _, _ = stats.chi2_contingency(table)
        except:
            p_value = np.nan
            
        if b == 0 or c == 0:
            por = np.nan
        else:
            por = (a * d) / (b * c)
        
        por_results.append({
            'Slice ID': slice_id,
            'Pair': f"{col1}-{col2}",
            'POR': por,
            'p_value': p_value
        })

por_df = pd.DataFrame(por_results)

p_value_table = por_df.pivot(index='Pair', columns='Slice ID', values='p_value')
significance_matrix = p_value_table.applymap(lambda x: 1 if pd.notna(x) and x < 0.05 else 0 if pd.notna(x) else np.nan)
p_value_annot = p_value_table.applymap(lambda x: f'{x:.3f}' if pd.notna(x) and x >= 0.001 else '<0.001' if pd.notna(x) else 'NaN')

fig, ax = plt.subplots(figsize=(18, 12))
sns.heatmap(significance_matrix, 
            annot=p_value_annot, 
            cmap=['lightgray', 'red'], 
            fmt='',
            vmin=0,
            vmax=1,
            ax=ax,
            cbar_kws={
                'label': 'Significance (0=NS, 1=Sig)', 
                'shrink': 0.8,
                'ticks': [0, 1]
            })

ax.set_title('P-values for Smell Pairs and Time Slices\n(Red = p < 0.05)', fontsize=14, fontweight='bold', pad=20)
ax.tick_params(axis='both', labelsize=12)
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('p_value_matrix_sliced.pdf', bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(20, 14))
pivot_prev = prevalence_df.pivot(index='Smell', columns='Slice ID', values='Prevalence')
sns.heatmap(pivot_prev, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Prevalence (%)'})
ax.set_title('Smell Prevalence by Time Slice', fontsize=14, fontweight='bold', pad=20)
ax.tick_params(axis='both', labelsize=12)
plt.tight_layout()
plt.savefig('prevalence_heatmap.pdf', bbox_inches='tight')
plt.close()

bounds = [0, 0.5, 1, 3, 8, 30, 1000]
norm = BoundaryNorm(bounds, ncolors=6)
colors = ['#00008B', '#87CEEB', '#FFFF00', '#FFA500', '#FF4500', '#FF0000']
cmap = LinearSegmentedColormap.from_list('clinical_scale_custom', colors, N=6)

fig, ax = plt.subplots(figsize=(18, 24))
pivot_por = por_df.pivot(index='Pair', columns='Slice ID', values='POR')
sns.heatmap(pivot_por, 
            annot=True, 
            fmt='.2f', 
            cmap=cmap, 
            norm=norm,
            ax=ax, 
            cbar_kws={
                'label': 'Prevalence Odds Ratio', 
                'shrink': 0.8,
                'ticks': [0.25, 0.75, 2, 5.5, 19, 515]
            })

cbar = ax.collections[0].colorbar
cbar.set_ticklabels(['0-0.5', '0.5-1', '1-3', '3-8', '8-30', '30+'])
ax.set_title('Prevalence Odds Ratio by Smell Pair and Time Slice', fontsize=14, fontweight='bold', pad=20)
ax.tick_params(axis='both', labelsize=12)
ax.tick_params(axis='x', rotation=45)
cbar.ax.tick_params(labelsize=12)
cbar.ax.yaxis.label.set_size(12)
plt.tight_layout()
plt.savefig('por_heatmap.pdf', bbox_inches='tight')
plt.close()

valid_pairs = pivot_por.dropna(how='all')
n_pairs = len(valid_pairs)
n_cols = 4
n_rows = (n_pairs + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 4))
axes = axes.flatten()

for i, pair in enumerate(valid_pairs.index):
    axes[i].plot(valid_pairs.columns, valid_pairs.loc[pair], marker='o', linewidth=2.5, 
                 markersize=6, markerfacecolor='white', markeredgewidth=2)
    axes[i].set_title(pair, fontsize=12, fontweight='bold', pad=10)
    axes[i].set_xlabel('Slice ID', fontsize=12)
    axes[i].set_ylabel('POR', fontsize=12)
    axes[i].grid(True, alpha=0.3)
    axes[i].tick_params(axis='both', labelsize=12)
    axes[i].set_xticks(valid_pairs.columns)

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.suptitle('POR Trends by Smell Pair', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.subplots_adjust(top=0.93, hspace=0.4, wspace=0.3)
plt.savefig('por_mini_trends.pdf', bbox_inches='tight')
plt.close()