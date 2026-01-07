import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import os
from datetime import date
from matplotlib.ticker import MaxNLocator
import logging
import matplotlib.font_manager as fm

# Silence font warnings
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# --- Configuration ---
CSV_FILE = "citations_history.csv"
WIDE_CSV_FILE = "citations_wide_format.csv"
PLOT_FILE = "top_10_citations_plot.png"
CUMULATIVE_PLOT_FILE = "cumulative_citations_plot.png"
XKCD_PLOT_FILE = "cumulative_citations_xkcd.png"
XKCD_TOP_5_FILE = "top_5_citations_xkcd.png"
# ---------------------

def create_wide_csv():
    if not os.path.exists(CSV_FILE):
        print(f"Error: Long format file '{CSV_FILE}' not found. Run scrape.py first.")
        return None

    try:
        df_long = pd.read_csv(CSV_FILE)
        df_long['Date'] = df_long['Date'].astype(str)
        df_wide = df_long.pivot(index='Title', columns='Date', values='Citations')
        df_wide.to_csv(WIDE_CSV_FILE)
        print(f"Successfully created WIDE format file: {WIDE_CSV_FILE}")
        return df_wide
    except Exception as e:
        print(f"CRITICAL ERROR during file creation: {e}")
        return None

def get_best_xkcd_font():
    """Returns the best available hand-drawn font name."""
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    for f in ["Humor Sans", "Comic Neue", "xkcd", "Comic Sans MS"]:
        if f in available_fonts:
            return f
    return "sans-serif"

def generate_xkcd_cumulative_plot(df_cumulative):
    try:
        chosen_font = get_best_xkcd_font()
        with plt.xkcd():
            plt.rcParams.update({'font.family': chosen_font})
            plt.figure(figsize=(12, 6))
            plt.plot(range(len(df_cumulative)), df_cumulative['Cumulative Citations'].values, color='#007400', linewidth=5)
            plt.title('LUKAS SCARFE: TOTAL CITATIONS', fontsize=25)
            plt.xticks(range(len(df_cumulative)), df_cumulative.index, rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(XKCD_PLOT_FILE, dpi=300)
            plt.close()
            print(f"Successfully saved XKCD-style cumulative plot to {XKCD_PLOT_FILE}")
    except Exception as e:
        print(f"Error generating XKCD cumulative plot: {e}")

def generate_xkcd_top_5_plot(df_wide):
    """Generates an XKCD-style plot for the top 5 papers."""
    try:
        chosen_font = get_best_xkcd_font()
        last_date = df_wide.columns[-1]
        df_top_5 = df_wide.sort_values(by=last_date, ascending=False).head(5)
        df_plot = df_top_5.T.fillna(0)
        
        # Format titles: Get first 5 words
        new_column_names = []
        for col in df_plot.columns:
            words = col.split()
            short_name = " ".join(words[:5])
            if len(words) > 5:
                short_name += "..."
            new_column_names.append(short_name)
        
        df_plot.columns = new_column_names

        with plt.xkcd():
            plt.rcParams.update({'font.family': chosen_font})
            plt.figure(figsize=(14, 8)) # Increased size for better legend fit
            
            colors = ['black', 'red', 'blue', 'green', 'purple']
            
            for i, col in enumerate(df_plot.columns):
                plt.plot(range(len(df_plot)), df_plot[col], label=col, linewidth=3, color=colors[i % len(colors)])

            plt.title('TOP 5 MOST CITED PAPERS', fontsize=22)
            plt.xticks(range(len(df_plot)), df_plot.index, rotation=45, ha='right')
            plt.ylabel('CITATIONS')
            
            # Larger legend placed slightly outside to avoid overlapping lines
            plt.legend(loc='upper left', fontsize=12, bbox_to_anchor=(0.01, 0.85), frameon=True)
            
            plt.annotate('THE HEAVY HITTERS', xy=(len(df_plot)-1, df_plot.iloc[-1].max()), 
                         xytext=(len(df_plot)-5, df_plot.iloc[-1].max() + 5),
                         arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2'))

            plt.tight_layout()
            plt.savefig(XKCD_TOP_5_FILE, dpi=300)
            plt.close()
            print(f"Successfully saved XKCD-style Top 5 plot to {XKCD_TOP_5_FILE}")
    except Exception as e:
        print(f"Error generating XKCD Top 5 plot: {e}")

def generate_reports(df_wide):
    if df_wide is None: return
    
    try:
        # --- Professional Plots ---
        sns.set_theme(style="whitegrid") 
        last_date_column = df_wide.columns[-1] 
        df_sorted = df_wide.sort_values(by=last_date_column, ascending=False)
        df_top_10 = df_sorted.head(10)
        df_plot = df_top_10.T.fillna(0)
        df_plot.columns = [col[:25] for col in df_plot.columns]

        # Top 10 Prof. Plot
        plt.figure(figsize=(16, 6)) 
        colors = sns.color_palette('viridis', n_colors=10)
        for idx, (col, color) in enumerate(zip(df_plot.columns, colors)):
            plt.plot(df_plot.index, df_plot[col], marker='o', linewidth=2, label=col, color=color)
        plt.title('Lukas Scarfe Citations by Paper', fontsize=18, fontweight='bold', pad=20)
        plt.legend(bbox_to_anchor=(0.05, 0.9), loc='upper left', fontsize=6, frameon=True, shadow=True)
        plt.xticks(rotation=45, ha='right')
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig(PLOT_FILE, dpi=300) 
        plt.close()

        # Cumulative Prof. Plot
        df_cumulative = df_wide.T.fillna(0)
        df_cumulative['Cumulative Citations'] = df_cumulative.sum(axis=1)
        plt.figure(figsize=(16, 6))
        plt.plot(range(len(df_cumulative)), df_cumulative['Cumulative Citations'].values, marker='o', color='#440154')
        plt.title('Lukas Scarfe Cumulative Citations Over Time', fontsize=20, fontweight='bold')
        plt.xticks(range(len(df_cumulative)), df_cumulative.index, rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(CUMULATIVE_PLOT_FILE, dpi=300)
        plt.close()

        # --- XKCD Plots ---
        generate_xkcd_cumulative_plot(df_cumulative)
        generate_xkcd_top_5_plot(df_wide)

    except Exception as e:
        print(f"CRITICAL ERROR during report generation: {e}")
        
if __name__ == "__main__":
    wide_data = create_wide_csv()
    generate_reports(wide_data)