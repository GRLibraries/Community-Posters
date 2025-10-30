# Poster-Processor

This project automates the processing of scanned community posters from an email inbox. It uses OCR and AI to extract data, which is then stored in a SQLite database and displayed on a static web frontend.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd poster-processor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory.
   - Add the following variables to the `.env` file:
     ```
     IMAP_SERVER=imap.example.com
     EMAIL_ACCOUNT=your-email@example.com
     EMAIL_PASSWORD=your-email-password
     ```

## Database Setup

The project uses a SQLite database to store poster information. The database is located at `database/posters.db`.

- **`posters` table:** Stores the main poster information, including the image path, extracted text, and date received.
- **`tags` table:** Stores the tags extracted from the posters.
- **`poster_tags` table:** Links posters to their corresponding tags.

The database is automatically initialized when you run the main script for the first time.

## Adding Posters to the Database

To add posters to the database, send an email with the poster image as an attachment to the email account specified in the `.env` file. The `main.py` script will monitor the inbox, process the attachments, and add the poster information to the database.
