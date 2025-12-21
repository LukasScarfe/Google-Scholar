import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import os
from datetime import date
from matplotlib.ticker import MaxNLocator

# --- Configuration (Must match scrape.py) ---
CSV_FILE = "citations_history.csv"
WIDE_CSV_FILE = "citations_wide_format.csv"
PLOT_FILE = "top_10_citations_plot.png"
# ---------------------------------------------

def create_wide_csv():
    if not os.path.exists(CSV_FILE):
        print(f"Error: Long format file '{CSV_FILE}' not found. Run scrape.py first.")
        return

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

def generate_reports(df_wide):
    """
    Reads the long-format CSV, pivots it to wide format, 
    and generates the plot of the top 10 most cited papers over time.
    """
    
    try:
        
        # --- B. Generate Top 10 Plot (Improved Styling) ---

        # Apply Seaborn style for better aesthetics
        sns.set_theme(style="whitegrid") 

        # 1. Identify the 'current' citation count
        # This now works because df_wide is defined above
        last_date_column = df_wide.columns[-1] 

        # 2. Sort by the current citation count and select the top 10
        df_sorted = df_wide.sort_values(by=last_date_column, ascending=False)
        df_top_10 = df_sorted.head(10)

        # 3. Transpose the data for plotting (Dates become the X-axis)
        df_plot = df_top_10.T 
        df_plot = df_plot.fillna(0) 

        df_plot.columns = [col[:25] for col in df_plot.columns]

        # Create the plot
        plt.figure(figsize=(16, 6)) 

        # Define distinct markers and line styles for each paper
        markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'X', 'P']
        linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
        
        # Get a color palette with 10 distinct colors
        colors = sns.color_palette('viridis', n_colors=10)
        
        # Plot each column manually to apply distinct markers and line styles
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

        # Add Labels and Formatting
        plt.title(
            f'Lukas Scarfe Citations', 
            fontsize=18, 
            fontweight='bold', 
            pad=20 
        )

        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Citations', fontsize=14)

        # Legend Placement
        plt.legend(
            bbox_to_anchor=(0.05, 0.95), 
            loc='upper left', 
            fontsize=6,
            frameon=True, 
            shadow=True
        )

        # Clean up the X-axis ticks
        plt.xticks(rotation=45, ha='right', fontsize=10) 
        plt.yticks(fontsize=10)
        
        # Set y-axis to only show integer values
        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Remove the top and right spines (border lines) for a cleaner look
        sns.despine(left=True)

        # Add a light horizontal grid for easier tracking
        plt.grid(axis='y', linestyle=':', alpha=0.7) 

        plt.tight_layout()

        # Save Plot
        PLOT_FILE = "top_10_citations_plot.png"
        plt.savefig(PLOT_FILE, dpi=300) 
        plt.close()

        print(f"Successfully saved beautiful citation plot to {PLOT_FILE}")

        # --- C. Generate Cumulative Citations Plot ---
        # Calculate cumulative citations per date (sum across all papers)
        df_cumulative = df_wide.T
        df_cumulative = df_cumulative.fillna(0)
        df_cumulative['Cumulative Citations'] = df_cumulative.sum(axis=1)
        
        # Create the cumulative plot with matching style
        plt.figure(figsize=(16, 6))
        
        plt.plot(
            range(len(df_cumulative)),
            df_cumulative['Cumulative Citations'].values,
            marker='o',
            linestyle='-',
            linewidth=2.5,
            color='#440154',  # Dark purple from viridis
            markerfacecolor='#FDE724',  # Yellow from viridis
            markersize=8
        )
        
        # Add Labels and Formatting (matching the top 10 plot style)
        plt.title(
            f'Lukas Scarfe Cumulative Citations Over Time',
            fontsize=18,
            fontweight='bold',
            pad=20
        )
        
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Cumulative Citations', fontsize=14)
        
        # Set X-axis ticks with dates
        plt.xticks(
            range(len(df_cumulative)),
            df_cumulative.index,
            rotation=45,
            ha='right',
            fontsize=10
        )
        plt.yticks(fontsize=10)
        
        # Set y-axis to only show integer values
        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Remove the top and right spines
        sns.despine(left=True)
        
        # Add a light horizontal grid for easier tracking
        plt.grid(axis='y', linestyle=':', alpha=0.7)
        
        plt.tight_layout()
        
        # Save cumulative plot
        CUMULATIVE_PLOT_FILE = "cumulative_citations_plot.png"
        plt.savefig(CUMULATIVE_PLOT_FILE, dpi=300)
        plt.close()
        
        print(f"Successfully saved cumulative citation plot to {CUMULATIVE_PLOT_FILE}")

    except Exception as e:
        print(f"CRITICAL ERROR during report generation: {e}")
        
if __name__ == "__main__":
    
    generate_reports(create_wide_csv())