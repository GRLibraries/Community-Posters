import email
import imaplib
import os
import sqlite3
from datetime import datetime
from PIL import Image
import pytesseract
import spacy

# --- Configuration ---
# Use environment variables for sensitive data
IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
EMAIL_ACCOUNT = os.environ.get("EMAIL_ACCOUNT")
PASSWORD = os.environ.get("EMAIL_PASSWORD")

ATTACHMENT_DIR = "attachments"
PROCESSED_MAILBOX = "Processed"
DATABASE_FILE = "database/posters.db"

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def create_db_connection():
    """Creates a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
    except sqlite3.Error as e:
        print(e)
    return conn

def insert_poster(conn, image_path, extracted_text, date_received):
    """Inserts a new poster into the posters table."""
    sql = ''' INSERT INTO posters(image_path,extracted_text,date_received)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (image_path, extracted_text, date_received))
    conn.commit()
    return cur.lastrowid

def insert_tag(conn, tag_name):
    """Inserts a tag if it doesn't exist and returns its id."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    data = cur.fetchone()
    if data is None:
        sql = ''' INSERT INTO tags(name) VALUES(?) '''
        cur.execute(sql, (tag_name,))
        conn.commit()
        return cur.lastrowid
    else:
        return data[0]

def link_poster_to_tag(conn, poster_id, tag_id):
    """Links a poster to a tag."""
    sql = ''' INSERT INTO poster_tags(poster_id,tag_id) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (poster_id, tag_id))
    conn.commit()

def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""

def extract_tags_from_text(text):
    """Extracts tags from text using spaCy NER."""
    doc = nlp(text)
    tags = set()
    for ent in doc.ents:
        if ent.label_ in ["GPE", "ORG", "EVENT", "FAC", "LOC"]:
            tags.add(ent.text.strip())
    return list(tags)

def connect_to_imap():
    """Connects to the IMAP server and logs in."""
    if not EMAIL_ACCOUNT or not PASSWORD:
        print("Error: EMAIL_ACCOUNT and EMAIL_PASSWORD environment variables must be set.")
        return None
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        return mail
    except imaplib.IMAP4.error as e:
        print(f"Error connecting to IMAP server: {e}")
        return None

def ensure_mailbox_exists(mail, mailbox):
    """Checks if a mailbox exists, and creates it if it doesn't."""
    status, mailboxes = mail.list()
    if status == 'OK':
        mailboxes = [m.decode().split(' "." ')[-1].strip('"') for m in mailboxes]
        if mailbox not in mailboxes:
            try:
                mail.create(mailbox)
            except imaplib.IMAP4.error as e:
                print(f"Error creating mailbox '{mailbox}': {e}")

def process_emails(mail):
    """Processes emails in the INBOX."""
    mail.select("inbox")
    status, messages = mail.search(None, "UNSEEN")
    if status != "OK":
        print("No new messages found!")
        return

    email_ids = messages[0].split()
    if not email_ids:
        print("No new messages to process.")
        return

    print(f"Found {len(email_ids)} new emails.")
    db_conn = create_db_connection()

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        date_received = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename and (filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))):
                filepath = os.path.join(ATTACHMENT_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))

                print(f"Processing {filename}...")
                text = extract_text_from_image(filepath)
                tags = extract_tags_from_text(text)

                if db_conn:
                    poster_id = insert_poster(db_conn, filepath, text, date_received)
                    for tag in tags:
                        tag_id = insert_tag(db_conn, tag)
                        link_poster_to_tag(db_conn, poster_id, tag_id)
                    print(f"Stored poster {poster_id} with tags: {tags}")

        mail.copy(email_id, PROCESSED_MAILBOX)
        mail.store(email_id, '+FLAGS', '\\Deleted')

    mail.expunge()
    if db_conn:
        db_conn.close()

def main():
    """Main function to run the email monitoring process."""
    if not os.path.exists(ATTACHMENT_DIR):
        os.makedirs(ATTACHMENT_DIR)

    mail = connect_to_imap()
    if mail:
        ensure_mailbox_exists(mail, PROCESSED_MAILBOX)
        process_emails(mail)
        mail.logout()
        print("Email processing complete.")

if __name__ == "__main__":
    main()
