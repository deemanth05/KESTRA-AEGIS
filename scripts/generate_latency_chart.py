import matplotlib.pyplot as plt
import numpy as np

# Set dark theme styling
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
fig.patch.set_facecolor('#0f172a') # Dark slate background
ax.set_facecolor('#0f172a')

# Data
categories = ['Memory Cache Hit\n(Aegis Learning Loop)', 'Gemini 2.5 Flash\n(LLM Cache Miss)']
latencies = [0.45, 9.80]
colors = ['#10b981', '#f43f5e'] # Emerald Green vs Rose Pink

# Plot horizontal bars
bars = ax.barh(categories, latencies, color=colors, height=0.55, edgecolor='none')

# Add values on the bars
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
            f' {width:.2f}s', 
            va='center', ha='left', color='#ffffff', fontweight='bold', fontsize=11)

# Add title and labels
ax.set_title('Healing Latency: Gemini Call vs. Aegis Cache Hit', 
             fontsize=14, fontweight='bold', pad=20, color='#ffffff')
ax.set_xlabel('Mean Ingestion Healing Time (Seconds)', fontsize=11, labelpad=10, color='#94a3b8')

# Clean spines and grid
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#334155')
ax.spines['bottom'].set_color('#334155')
ax.tick_params(colors='#94a3b8', labelsize=11)
ax.xaxis.grid(True, linestyle='--', alpha=0.15, color='#ffffff')

# Highlight the latency speedup
ax.text(5.0, 0.4, '21.7x Faster Resolution\n100% API Cost Saved', 
        color='#38bdf8', va='center', ha='center', fontsize=12, fontweight='bold',
        bbox=dict(facecolor='#1e293b', edgecolor='#0284c7', boxstyle='round,pad=0.8'))

# Adjust layout & save
plt.tight_layout()
plt.savefig('docs/latency_comparison.png', facecolor=fig.get_facecolor(), edgecolor='none')
print("Chart generated successfully at docs/latency_comparison.png!")
