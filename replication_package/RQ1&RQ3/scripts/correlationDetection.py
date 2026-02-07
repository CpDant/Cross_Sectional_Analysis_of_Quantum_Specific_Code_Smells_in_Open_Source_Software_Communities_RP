import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import scipy.stats as stats

plt.style.use('default')
sns.set_palette("husl")

df = pd.read_excel('..\\results\\esempio.xlsx')
smell_columns = ['CG', 'ROC', 'NC', 'LC', 'IM', 'IdQ', 'IQ', 'LPQ']

prevalence_results = []
total_repos = len(df)
for smell in smell_columns:
    affected_repos = (df[smell] > 0).sum()
    prevalence = (affected_repos / total_repos) * 100
    prevalence_results.append({
        'Smell': smell,
        'Prevalence': prevalence
    })

prevalence_df = pd.DataFrame(prevalence_results)

por_results = []
for col1, col2 in combinations(smell_columns, 2):
    a = ((df[col1] > 0) & (df[col2] > 0)).sum()
    b = ((df[col1] > 0) & (df[col2] == 0)).sum()
    c = ((df[col1] == 0) & (df[col2] > 0)).sum()
    d = ((df[col1] == 0) & (df[col2] == 0)).sum()
    
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
        'Coppia': f"{col1}-{col2}",
        'Smell1': col1,
        'Smell2': col2,
        'POR': por,
        'p_value': p_value
    })

por_df = pd.DataFrame(por_results)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(prevalence_df['Smell'], prevalence_df['Prevalence'], color='gray')
ax.set_title('Smell Prevalence', fontsize=14, fontweight='bold')
ax.set_ylabel('Prevalence (%)', fontsize=12)
ax.set_xlabel('Smell', fontsize=12)
ax.tick_params(axis='both', labelsize=12)
ax.tick_params(axis='x', rotation=45)

for bar, val in zip(bars, prevalence_df['Prevalence']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=12)

plt.tight_layout()
plt.savefig('prevalence_plot.pdf', bbox_inches='tight')
plt.close()

por_matrix = pd.DataFrame(index=smell_columns, columns=smell_columns, dtype=float)
for _, row in por_df.iterrows():
    por_matrix.loc[row['Smell1'], row['Smell2']] = row['POR']
    por_matrix.loc[row['Smell2'], row['Smell1']] = row['POR']

np.fill_diagonal(por_matrix.values, 1)
mask = np.triu(np.ones_like(por_matrix, dtype=bool))
bounds = [0, 0.5, 1, 3, 8, 30, 1000]
norm = BoundaryNorm(bounds, ncolors=6)
colors = ['#00008B', '#87CEEB', '#FFFF00', '#FFA500', '#FF4500', '#FF0000']
cmap = LinearSegmentedColormap.from_list('clinical_scale_custom', colors, N=6)

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(por_matrix, 
            annot=True, 
            fmt='.2f', 
            cmap=cmap, 
            norm=norm,
            mask=mask,
            ax=ax, 
            cbar_kws={
                'label': 'Prevalence Odds Ratio',
                'shrink': 0.8
            })

cbar = ax.collections[0].colorbar
cbar.set_ticks([0.25, 0.75, 2, 5.5, 19, 515])
cbar.set_ticklabels(['0-0.5', '0.5-1', '1-3', '3-8', '8-30', '30+'])
ax.set_title('Prevalence Odds Ratio - Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
ax.tick_params(axis='both', labelsize=12)
cbar.ax.tick_params(labelsize=12)
cbar.ax.yaxis.label.set_size(12)

plt.tight_layout()
plt.savefig('por_matrix.pdf', bbox_inches='tight')
plt.close()