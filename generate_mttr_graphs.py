import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define paths
data_path = 'reports/mttr_logs.csv'
output_dir = 'reports/figures'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Check if data exists
if not os.path.isfile(data_path):
    print(f"[!] No MTTR data found at {data_path}. Run your attack simulations first!")
    exit()

# Load Data
df = pd.read_csv(data_path)

if df.empty:
    print("[!] The MTTR log is empty. No attacks were mitigated yet.")
    exit()

# Set IEEE academic styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})

# --- CHART 1: Average MTTR by Attack Type (Bar Chart) ---
plt.figure(figsize=(9, 6)) # Slightly wider figure
ax = sns.barplot(x='Attack_Type', y='MTTR_Seconds', data=df, errorbar=None, palette='Blues_d')
plt.title('HawkGrid CIRS: Mean Time to Respond (MTTR) by Threat Vector', pad=15)
plt.ylabel('Response Time (Seconds)')
plt.xlabel('Attack Classification')

# 🚨 THIS IS THE FIX: Tilt the labels 30 degrees 🚨
plt.xticks(rotation=30, ha='right')

# Annotate bars with exact timing
for p in ax.patches:
    ax.annotate(format(p.get_height(), '.2f') + 's', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha = 'center', va = 'center', xytext = (0, 12), textcoords = 'offset points')

plt.tight_layout()
plt.savefig(f'{output_dir}/mttr_bar_chart.png', dpi=300)
print(f"[*] Saved Bar Chart to {output_dir}/mttr_bar_chart.png")

# --- CHART 2: MTTR Variance (Box Plot) ---
plt.figure(figsize=(9, 6)) # Slightly wider figure
sns.boxplot(x='Attack_Type', y='MTTR_Seconds', data=df, palette='Set2')
plt.title('Operational Consistency of Autonomous Mitigation', pad=15)
plt.ylabel('Latency (Seconds)')
plt.xlabel('Attack Classification')

# 🚨 THIS IS THE FIX: Tilt the labels 30 degrees 🚨
plt.xticks(rotation=30, ha='right')

plt.tight_layout()
plt.savefig(f'{output_dir}/mttr_box_plot.png', dpi=300)
print(f"[*] Saved Box Plot to {output_dir}/mttr_box_plot.png")