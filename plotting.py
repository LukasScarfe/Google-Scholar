import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import os
from datetime import date
from matplotlib.ticker import MaxNLocator

import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# --- Configuration ---
CSV_FILE = "citations_history.csv"
WIDE_CSV_FILE = "citations_wide_format.csv"
PLOT_FILE = "top_10_citations_plot.png"
CUMULATIVE_PLOT_FILE = "cumulative_citations_plot.png"
XKCD_PLOT_FILE = "cumulative_citations_xkcd.png"
# ---------------------

def create_wide_csv():
    if not os.path.exists(CSV_FILE):
        print(f"Error: Long format file '{CSV_FILE}' not found. Run scrape.py first.")
        return None

    try:
        # Load the full, long-format history file
        df_long = pd.read_csv(CSV_FILE)
        df_long['Date'] = df_long['Date'].astype(str)
        
        # --- A. Create WIDE Format File ---
        df_wide = df_long.pivot(
            index='Title',
            columns='Date', 
            values='Citations'
        )
        df_wide.to_csv(WIDE_CSV_FILE)
        print(f"Successfully created WIDE format file: {WIDE_CSV_FILE}")
        return df_wide

    except Exception as e:
        print(f"CRITICAL ERROR during file creation: {e}")
        return None

def generate_xkcd_cumulative_plot(df_cumulative):
    """
    Generates a fun, hand-drawn style plot of cumulative citations.
    """
    try:
        # Use the xkcd context manager for the 'hand-drawn' look
        # This keeps the sketchy style isolated to this one plot
        with plt.xkcd():
            plt.figure(figsize=(12, 6))
            
            # Plot the data
            plt.plot(
                range(len(df_cumulative)), 
                df_cumulative['Cumulative Citations'].values, 
                color='black', 
                linewidth=3,
            )
            
            # Add titles and labels in the characteristic 'all caps' style
            plt.title('LUKAS SCARFE: TOTAL CITATIONS', fontsize=20)

            # Set X-axis ticks
            plt.xticks(
                range(len(df_cumulative)), 
                df_cumulative.index, 
                rotation=45, 
                ha='right'
            )


            plt.tight_layout()
            plt.savefig(XKCD_PLOT_FILE, dpi=150)
            plt.close()
            print(f"Successfully saved XKCD-style plot to {XKCD_PLOT_FILE}")

    except Exception as e:
        print(f"Error generating XKCD plot: {e}")

def generate_reports(df_wide):
    if df_wide is None:
        return
    
    try:
        # --- B. Generate Top 10 Plot (Professional Style) ---
        sns.set_theme(style="whitegrid") 

        last_date_column = df_wide.columns[-1] 
        df_sorted = df_wide.sort_values(by=last_date_column, ascending=False)
        df_top_10 = df_sorted.head(10)

        df_plot = df_top_10.T 
        df_plot = df_plot.fillna(0) 
        df_plot.columns = [col[:25] for col in df_plot.columns]

        plt.figure(figsize=(16, 6)) 
        markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'X', 'P']
        linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
        colors = sns.color_palette('viridis', n_colors=10)
        
        for idx, (col, marker, linestyle, color) in enumerate(zip(df_plot.columns, markers, linestyles, colors)):
            plt.plot(
                df_plot.index,
                df_plot[col],
                marker=marker,
                linestyle=linestyle,
                linewidth=2,
                markersize=8,
                label=col,
                color=color
            )

        plt.title('Lukas Scarfe Citations', fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Citations', fontsize=14)
        plt.legend(bbox_to_anchor=(0.05, 0.95), loc='upper left', fontsize=6, frameon=True, shadow=True)
        plt.xticks(rotation=45, ha='right', fontsize=10) 
        plt.yticks(fontsize=10)
        
        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        sns.despine(left=True)
        plt.grid(axis='y', linestyle=':', alpha=0.7) 

        plt.tight_layout()
        plt.savefig(PLOT_FILE, dpi=300) 
        plt.close()
        print(f"Successfully saved beautiful citation plot to {PLOT_FILE}")

        # --- C. Generate Cumulative Citations Plot ---
        df_cumulative = df_wide.T
        df_cumulative = df_cumulative.fillna(0)
        df_cumulative['Cumulative Citations'] = df_cumulative.sum(axis=1)
        
        plt.figure(figsize=(16, 6))
        plt.plot(
            range(len(df_cumulative)),
            df_cumulative['Cumulative Citations'].values,
            marker='o',
            linestyle='-',
            linewidth=2.5,
            color='#440154',
            markerfacecolor='#FDE724',
            markersize=8
        )
        
        plt.title('Lukas Scarfe Cumulative Citations Over Time', fontsize=20, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Cumulative Citations', fontsize=14)
        
        plt.xticks(range(len(df_cumulative)), df_cumulative.index, rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        sns.despine(left=True)
        
        plt.tight_layout()
        plt.savefig(CUMULATIVE_PLOT_FILE, dpi=300)
        plt.close()
        print(f"Successfully saved cumulative citation plot to {CUMULATIVE_PLOT_FILE}")

        # --- D. Generate XKCD Style Plot ---
        # We pass the cumulative data we just calculated to the new function
        generate_xkcd_cumulative_plot(df_cumulative)

    except Exception as e:
        print(f"CRITICAL ERROR during report generation: {e}")
        
if __name__ == "__main__":
    wide_data = create_wide_csv()
    generate_reports(wide_data)