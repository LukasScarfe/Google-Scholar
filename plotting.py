import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patheffects as path_effects
import matplotlib.legend as mlegend
import matplotlib.ticker as mticker
from scipy.interpolate import PchipInterpolator

# --- Configuration & Themes ---
PATHS = {
    "input": "citations_history.csv",
    "wide_output": "citations_wide_format.csv",
}
FIG_SIZE = (12, 7)
DPI = 300

THEMES = {
    'white': {
        'dir': 'plots/white', 'bg': '#ffffff', 'txt': '#000000', 
        'edge': '#000000', 'line': '#007F00', 'grid': '#dddddd'
    },
    'dark': {
        'dir': 'plots/dark', 'bg': '#1D341E', 'txt': '#F8FCF8', 
        'edge': '#1D341E', 'line': '#7F5DA2', 'grid': '#2A4D2C'
    },
    'light': {
        'dir': 'plots/light', 'bg': '#E5DBDB', 'txt': '#4A0F0F', 
        'edge': '#4A0F0F', 'line': '#257D83', 'grid': '#BFCFCF'
    }
}

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# --- Helper Functions ---

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

def get_best_font():
    candidates = ["xkcd", "xkcd Script", "Humor Sans", "Comic Neue", "Comic Sans MS"]
    available = {f.name for f in fm.fontManager.ttflist}
    return next((f for f in candidates if f in available), "sans-serif")

def smooth_monotonic(x, y):
    x_new = np.linspace(min(x), max(x), 500)
    pchip = PchipInterpolator(x, y)
    return x_new, pchip(x_new)

def add_custom_grids(ax, x_labels, grid_color):
    """Adds theme-colored y-grid and vertical lines for the 1st and 15th."""
    ax.grid(axis='y', color=grid_color, linestyle='--', linewidth=1, zorder=0)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    
    for i, date in enumerate(x_labels):
        day = date.split('-')[-1].zfill(2)
        if day == '01' or day == '15':
            ax.axvline(x=i, color=grid_color, linestyle='--', linewidth=1, zorder=0)

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
        'legend.frameon': False,
        'path.effects': []
    })

# --- Main Plotting Logic ---

def generate_version(df_wide, df_cumulative, config):
    os.makedirs(config['dir'], exist_ok=True)
    apply_theme_params(config)

    # 1. Total Citations Plot
    with plt.xkcd():
        fig, ax = plt.subplots(figsize=FIG_SIZE)
        x_vals = np.array(range(len(df_cumulative)))
        x_smooth, y_smooth = smooth_monotonic(x_vals, df_cumulative.values)
        
        ax.plot(x_smooth, y_smooth, linewidth=6, zorder=3)
        add_custom_grids(ax, df_cumulative.index, config['grid']) # Grid added here
        
        ax.set_title('TOTAL CITATIONS', fontsize=22)
        ax.set_xticks(list(x_vals))
        ax.set_xticklabels(df_cumulative.index, rotation=45, ha='right')
        ax.set_ylabel('CITATIONS')
        
        clean_plot_elements(fig)
        plt.tight_layout()
        plt.savefig(
            f"{config['dir']}/total_citations.png", 
            dpi=DPI, 
            transparent=True,    # Makes the background see-through
            facecolor='none',    # Ensures no background color is painted
            bbox_inches='tight'
        )
        # plt.savefig(f"{config['dir']}/total_citations.png", dpi=DPI, facecolor=config['bg'])
        plt.close()

    # 2. Individual Paper Plots
    for title, row in df_wide.iterrows():
        with plt.xkcd():
            fig, ax = plt.subplots(figsize=FIG_SIZE)
            y_values = row.fillna(0).values
            x_vals = np.array(range(len(y_values)))
            x_smooth, y_smooth = smooth_monotonic(x_vals, y_values)
            
            ax.plot(x_smooth, y_smooth, linewidth=8, zorder=3)
            add_custom_grids(ax, df_wide.columns, config['grid']) # Grid added here
            
            ax.set_title(title.upper(), fontsize=18, wrap=True)
            ax.set_xticks(list(x_vals))
            ax.set_xticklabels(df_wide.columns, rotation=45, ha='right')
            ax.set_ylabel('CITATIONS')
            
            clean_plot_elements(fig)
            
            words = title.split()[:5]
            clean_words = ["".join(filter(str.isalnum, w)) for w in words]
            filename = "_".join(clean_words) + ".png"
            
            plt.tight_layout()
            plt.savefig(
                os.path.join(config['dir'], filename), 
                dpi=DPI, 
                transparent=True,    # Makes the background see-through
                facecolor='none',    # Ensures no background color is painted
                bbox_inches='tight'
            )
            #plt.savefig(os.path.join(config['dir'], filename), dpi=DPI, facecolor=config['bg'])
            plt.close()
            logging.info(f"Saved {config['dir']}/{filename}")

def main():
    df_wide, df_cumulative = get_data()
    if df_wide is not None:
        for theme_name, config in THEMES.items():
            logging.info(f"Generating {theme_name.upper()} theme...")
            generate_version(df_wide, df_cumulative, config)
        logging.info("Process Complete!")

if __name__ == "__main__":
    main()