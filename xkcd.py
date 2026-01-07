import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import os
from datetime import date
from matplotlib.ticker import MaxNLocator
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

CSV_FILE = "citations_history.csv"
XKCD_PLOT_FILE = "cumulative_citations_xkcd.png"


df_long = pd.read_csv(CSV_FILE)
df_long['Date'] = df_long['Date'].astype(str)

# --- A. Create WIDE Format File ---
df_wide = df_long.pivot(
    index='Title',
    columns='Date', 
    values='Citations'
)

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
                color='#007400', 
                linewidth=5
            )
            
            # Add titles and labels in the characteristic 'all caps' style
            plt.title('LUKAS SCARFE: TOTAL CITATIONS', fontsize=25)

            # Set X-axis ticks
            plt.xticks(
                range(len(df_cumulative)), 
                df_cumulative.index, 
                rotation=45, 
                ha='right'
            )



            plt.tight_layout()
            plt.savefig(XKCD_PLOT_FILE, dpi=300)
            plt.close()
            print(f"Successfully saved XKCD-style plot to {XKCD_PLOT_FILE}")

    except Exception as e:
        print(f"Error generating XKCD plot: {e}")


df_cumulative = df_wide.T
df_cumulative = df_cumulative.fillna(0)
df_cumulative['Cumulative Citations'] = df_cumulative.sum(axis=1)

generate_xkcd_cumulative_plot(df_cumulative)