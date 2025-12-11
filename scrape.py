import csv
from datetime import date
from scholarly import scholarly
import pandas as pd

# --- Configuration ---
USER_ID = "_eBW18oAAAAJ"
CSV_FILE = "citations_history.csv"         # Long Format File
WIDE_CSV_FILE = "citations_wide_format.csv" # Wide Format File (for analysis)

# NOTE: Since IDs are unreliable, exclusion is now based on Title (or simply removed)
# We will still process all papers unless you tell me specific titles to exclude.
# For now, this list is kept but is NOT USED.
EXCLUDE_PUB_IDS = [
    '9yKSN-GCB0IC', 
    'u5HHmVD_uO8C', 
    'qjMakFHDy7sC', 
    'd1gkVwhDpl0C', 
]
# ---------------------

try:
    author = scholarly.search_author_id(USER_ID)
    author = scholarly.fill(author, sections=['publications']) # type: ignore
except Exception as e:
    print(f"Error fetching author data: {e}")
    # Exit if the author data can't be fetched
    exit()

# Get today's date in YYYY-MM-DD format
today = date.today().isoformat()

data_to_save = []
for pub in author.get('publications', []):
    
    # --- ID Exclusion Check (REMOVED) ---
    # Since pub_id is unreliable and removed, the exclusion logic is also removed.
    # To exclude papers, you would need a list of Titles here.

    try:
        # Fill the publication details to get citation count
        pub_filled = scholarly.fill(pub)
        
        title = pub_filled.get('bib', {}).get('title', 'No title')
        citations = pub_filled.get('num_citations', 0)

        print(f'Getting Data for {title}')
        
        # --- DATA SAVE: Removed Scholarly_ID ---
        data_to_save.append({
            "Date": today,
            "Title": title,
            "Citations": int(citations),
        })
    except Exception as e:
        print(f"Error fetching details for a publication: {e}")

# --- CSV Saving Logic: Write to LONG Format File ---
if data_to_save:
    
    # --- FIELD NAMES: Removed Scholarly_ID ---
    fieldnames = ["Date", "Title", "Citations"]
    
    # Check if the file already exists to decide whether to write the header
    file_exists = False
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            if f.read(1):
                file_exists = True
    except FileNotFoundError:
        pass

    try:
        # Open the file in append mode ('a')
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()
                print("Created new LONG format CSV file with header.")
                
            writer.writerows(data_to_save)
        
        print(f"Successfully appended {len(data_to_save)} records to LONG format file: {CSV_FILE}")

    except Exception as e:
        print(f"CRITICAL ERROR SAVING LONG FORMAT CSV: {e}")
        exit()

#     # --- Pandas Transformation: Create WIDE Format File ---
#     try:
#         # Load the newly updated long-format history file
#         df_long = pd.read_csv(CSV_FILE)
        
#         # Ensure the date column is treated as strings for pivoting
#         df_long['Date'] = df_long['Date'].astype(str)
        
#         # 2. Pivot the data to the wide format
#         # --- INDEX: Only Title is used for the unique row identifier ---
#         df_wide = df_long.pivot(
#             index='Title',  # <-- Now uses Title as the sole row key
#             columns='Date', 
#             values='Citations'
#         )
        
#         # Save the Wide Format to a new file
#         df_wide.to_csv(WIDE_CSV_FILE)
        
#         print(f"Successfully created WIDE format file: {WIDE_CSV_FILE}")

#     except Exception as e:
#         print(f"CRITICAL ERROR during Pandas transformation or WIDE CSV saving: {e}")
        
else:
    print("No data was scraped to save.")