from scripts import monitor_inbox
from scripts import generate_static_json
from database import initialize_database
import os
from dotenv import load_dotenv

def main():
    """
    Main function to run the entire process of monitoring emails,
    processing posters, and generating the static site data.
    """
    # Load environment variables from .env file
    load_dotenv()

    print("Starting the process...")

    # 1. Initialize the database if it doesn't exist
    if not os.path.exists("database/posters.db"):
        print("Database not found. Initializing...")
        initialize_database.main()

    # 2. Monitor inbox, process new posters
    print("\n--- Checking for new emails ---")
    monitor_inbox.main()

    # 3. Generate the static JSON for the frontend
    print("\n--- Generating static data for the frontend ---")
    generate_static_json.main()

    print("\nProcess finished successfully!")

if __name__ == "__main__":
    main()
