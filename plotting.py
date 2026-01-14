import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as mticker
import numpy as np
from scipy.interpolate import PchipInterpolator

# --- Configuration ---
PATHS = {
    "input": "citations_history.csv",
    "wide_output": "citations_wide_format.csv",
    "xkcd_cumulative": "cumulative_citations_xkcd.png",
    "xkcd_top_5": "top_5_citations_xkcd.png",
    "individual_folder": "individual_plots"
}

FIG_SIZE = (12, 7)
DPI = 300

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

def get_data():
    if not os.path.exists(PATHS["input"]):
        logging.error(f"Source file {PATHS['input']} not found.")
        return None, None
    df_long = pd.read_csv(PATHS["input"])
    df_long['Date'] = df_long['Date'].astype(str)
    df_wide = df_long.pivot(index='Title', columns='Date', values='Citations')
    df_wide.to_csv(PATHS["wide_output"])
    df_cumulative = df_wide.T.fillna(0).sum(axis=1)
    return df_wide, df_cumulative

def get_xkcd_font():
    candidates = ["Humor Sans", "Comic Neue", "xkcd", "Comic Sans MS"]
    available = {f.name for f in fm.fontManager.ttflist}
    return next((f for f in candidates if f in available), "sans-serif")

def add_custom_grids(ax, x_labels):
    """Adds light grey y-grid and vertical lines for the 1st and 15th."""
    ax.grid(axis='y', color='lightgrey', linestyle='--', linewidth=1, zorder=0)
    # Force integer ticks for citation counts
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    
    for i, date in enumerate(x_labels):
        day = date.split('-')[-1].zfill(2)
        if day == '01' or day == '15':
            ax.axvline(x=i, color='lightgrey', linestyle='--', linewidth=1, zorder=0)

def smooth_monotonic(x, y):
    x_new = np.linspace(min(x), max(x), 500)
    pchip = PchipInterpolator(x, y)
    y_smooth = pchip(x_new)
    return x_new, y_smooth

def plot_cumulative_xkcd(df_cumulative):
    with plt.xkcd():
        fig, ax = plt.subplots(figsize=FIG_SIZE)
        plt.rcParams.update({'font.family': get_xkcd_font()})
        
        x_values = np.array(range(len(df_cumulative)))
        y_values = df_cumulative.values
        x_smooth, y_smooth = smooth_monotonic(x_values, y_values)
        
        ax.plot(x_smooth, y_smooth, color='green', linewidth=6, zorder=3)
        add_custom_grids(ax, df_cumulative.index)
        
        ax.set_title('TOTAL CITATIONS', fontsize=22)
        ax.set_xticks(list(x_values))
        ax.set_xticklabels(df_cumulative.index, rotation=45, ha='right')
        ax.set_ylabel('CITATIONS')
        
        plt.tight_layout()
        plt.savefig(PATHS["xkcd_cumulative"], dpi=DPI)
        plt.close()

def plot_top_5_xkcd(df_wide):
    with plt.xkcd():
        fig, ax = plt.subplots(figsize=FIG_SIZE)
        plt.rcParams.update({'font.family': get_xkcd_font()})
        
        last_date = df_wide.columns[-1]
        top_5 = df_wide.sort_values(by=last_date, ascending=False).head(5).T.fillna(0)
        
        x_values = np.array(range(len(top_5)))
        colours = plt.get_cmap('tab10').colors

        for i, col in enumerate(top_5.columns):
            y_values = top_5[col].values
            x_smooth, y_smooth = smooth_monotonic(x_values, y_values)
            ax.plot(x_smooth, y_smooth, label=col[:40]+"...", linewidth=3, color=colours[i % len(colours)], zorder=3)

        add_custom_grids(ax, top_5.index)
        ax.set_title('THE TOP 5', fontsize=22)
        ax.set_xticks(list(x_values))
        ax.set_xticklabels(top_5.index, rotation=45, ha='right')
        ax.set_ylabel('CITATIONS')
        ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.9), fontsize=10, frameon=True)

        plt.tight_layout()
        plt.savefig(PATHS["xkcd_top_5"], dpi=DPI)
        plt.close()

def plot_individual_papers_xkcd(df_wide):
    if not os.path.exists(PATHS["individual_folder"]):
        os.makedirs(PATHS["individual_folder"])

    with plt.xkcd():
        plt.rcParams.update({'font.family': get_xkcd_font()})
        
        for title, row in df_wide.iterrows():
            fig, ax = plt.subplots(figsize=FIG_SIZE)
            y_values = row.fillna(0).values
            x_values = np.array(range(len(y_values)))
            x_smooth, y_smooth = smooth_monotonic(x_values, y_values)
            
            ax.plot(x_smooth, y_smooth, color='green', linewidth=6, zorder=3)
            add_custom_grids(ax, df_wide.columns)
            
            # Title exactly as paper title
            ax.set_title(title.upper(), fontsize=18, wrap=True)
            ax.set_xticks(list(x_values))
            ax.set_xticklabels(df_wide.columns, rotation=45, ha='right')
            ax.set_ylabel('CITATIONS')
            
            # --- Filename Logic ---
            # Take first 5 words, join with underscore, remove special characters
            words = title.split()[:5]
            clean_words = ["".join(filter(str.isalnum, w)) for w in words]
            filename = "_".join(clean_words) + ".png"
            file_path = os.path.join(PATHS["individual_folder"], filename)
            
            plt.tight_layout()
            plt.savefig(file_path, dpi=DPI)
            plt.close()
            logging.info(f"Saved: {filename}")

def main():
    df_wide, df_cumulative = get_data()
    if df_wide is not None:
        logging.info("Generating reports...")
        plot_cumulative_xkcd(df_cumulative)
        plot_top_5_xkcd(df_wide)
        plot_individual_papers_xkcd(df_wide)
        logging.info("Process Complete!")

if __name__ == "__main__":
    main()