import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patheffects as path_effects
import matplotlib.legend as mlegend
from scipy.interpolate import PchipInterpolator

# --- Configuration ---
PATHS = {"input": "citations_history.csv", "wide_output": "citations_wide_format.csv"}
FIG_SIZE = (12, 7)
DPI = 300

THEMES = {
    'white': {
        'dir': 'plots/white', 'bg': '#ffffff', 'txt': '#000000', 
        'edge': '#000000', 'line': '#007F00'
    },
    'dark': {
        'dir': 'plots/dark', 'bg': '#1D341E', 'txt': '#628E63', 
        'edge': '#1D341E', 'line': '#7F5DA2'
    },
    'light': {
        'dir': 'plots/light', 'bg': '#D5E4E4', 'txt': '#4A0F0F', 
        'edge': '#4A0F0F', 'line': '#DC0000'
    }
}

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# --- Helper Functions ---

def get_data():
    if not os.path.exists(PATHS["input"]): return None, None
    df = pd.read_csv(PATHS["input"])
    df_wide = df.pivot(index='Title', columns='Date', values='Citations')
    df_wide.to_csv(PATHS["wide_output"])
    return df_wide, df_wide.T.fillna(0).sum(axis=1)

def get_best_font():
    candidates = ["Humor Sans", "Comic Neue", "xkcd", "Comic Sans MS"]
    available = {f.name for f in fm.fontManager.ttflist}
    return next((f for f in candidates if f in available), "sans-serif")

def smooth_monotonic(x, y):
    x_new = np.linspace(min(x), max(x), 500)
    return x_new, PchipInterpolator(x, y)(x_new)

def clean_plot_elements(fig):
    """Removes path effects (white halos) and legend borders."""
    for artist in fig.findobj():
        if hasattr(artist, 'set_path_effects'):
            artist.set_path_effects([path_effects.Normal()])
    for legend in fig.findobj(mlegend.Legend):
        legend.get_frame().set_linewidth(0.0)

def apply_theme_params(config):
    plt.rcdefaults()
    plt.rcParams.update({
        'font.family': get_best_font(),
        'figure.facecolor': config['bg'],
        'axes.facecolor': config['bg'],
        'text.color': config['txt'],
        'axes.labelcolor': config['txt'],
        'xtick.color': config['txt'],
        'ytick.color': config['txt'],
        'axes.edgecolor': config['edge'],
        'axes.prop_cycle': plt.cycler(color=[config['line']]),
        'legend.frameon': False
    })

# --- Main Plotting Logic ---

def generate_version(df_wide, df_cumulative, config):
    os.makedirs(config['dir'], exist_ok=True)
    apply_theme_params(config)

    # 1. Total Citations
    with plt.xkcd():
        fig, ax = plt.subplots(figsize=FIG_SIZE)
        x, y = smooth_monotonic(range(len(df_cumulative)), df_cumulative.values)
        ax.plot(x, y, linewidth=6)
        ax.set_title('TOTAL CITATIONS', fontsize=26)
        ax.set_xticks(range(len(df_cumulative)))
        ax.set_xticklabels(df_cumulative.index, rotation=45, ha='right')
        
        clean_plot_elements(fig)
        plt.savefig(f"{config['dir']}/total_citations.png", dpi=DPI, facecolor=config['bg'], bbox_inches='tight')
        plt.close()

    # 2. Individual Papers
    for title, row in df_wide.iterrows():
        with plt.xkcd():
            fig, ax = plt.subplots(figsize=FIG_SIZE)
            y_vals = row.fillna(0).values
            x_sm, y_sm = smooth_monotonic(range(len(y_vals)), y_vals)
            ax.plot(x_sm, y_sm, linewidth=6)
            ax.set_title(title.upper(), fontsize=26, wrap=True)
            ax.set_xticks(range(len(y_vals)))
            ax.set_xticklabels(df_wide.columns, rotation=45, ha='right')
            
            clean_plot_elements(fig)
            filename = "_".join(["".join(filter(str.isalnum, w)) for w in title.split()[:5]]) + ".png"
            plt.savefig(f"{config['dir']}/{filename}", dpi=DPI, facecolor=config['bg'], bbox_inches='tight')
            plt.close()
            logging.info(f"Saved {config['dir']}/{filename}")

def main():
    df_wide, df_cumulative = get_data()
    if df_wide is None: return
    
    for theme_name, config in THEMES.items():
        logging.info(f"Generating {theme_name} theme...")
        generate_version(df_wide, df_cumulative, config)
    logging.info("All themes generated successfully.")

if __name__ == "__main__":
    main()