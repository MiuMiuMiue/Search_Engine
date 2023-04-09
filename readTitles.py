import sys
import sqlite3
from pathlib import Path
from read import TextProcessor

def ReadTitles():
    path = Path(sys.argv[1])
    conn = sqlite3.connect("titles.db")
    cursor = conn.cursor()
    reader = TextProcessor()

    cursor.execute("""
        CREATE TABLE titleTable (
            docID TEXT,
            title TEXT
        )
    """)
    counter = 0
    for dir in path.iterdir():
        if dir.is_dir():
            for file in dir.iterdir():
                counter += 1
                print(f"Current Progress: {(counter / 37497) * 100:.2f}/100")

                soup = reader.readText(file)
                docID = dir.name + "/" + file.name
                title = "Anonymous Website"

                if soup.find_all("title"):
                    # print(soup.find_all("title")[0].get_text())
                    title = soup.find_all("title")[0].get_text()

                title = title.replace("\x00", "")

                cursor.execute(f"""
                    INSERT INTO titleTable (docID, title)
                    VALUES ('{docID}', ?)
                """, (title,))

    conn.commit()
    conn.close()