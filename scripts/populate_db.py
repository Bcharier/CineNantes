import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.fetch_raw_showtimes import main as fetch_main
from scripts.parse_showtimes import process_raw_files

def main():
    print("Step 1: Fetching raw showtimes from Allociné...")
    fetch_main()
    print("Step 2: Parsing and inserting showtimes into Supabase...")
    process_raw_files(raw_dir="data/raw_showtimes")
    print("Done.")

if __name__ == "__main__":
    main()