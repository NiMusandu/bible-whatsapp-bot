from datetime import datetime, timedelta
import json

# Bible chapters
chapters = {
    "OT": [
        ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
        ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
        ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
        ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
        ("Esther", 10), ("Job", 42), ("Isaiah", 66), ("Jeremiah", 52),
        ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12), ("Hosea", 14),
        ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4), ("Micah", 7),
        ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3), ("Haggai", 2),
        ("Zechariah", 14), ("Malachi", 4)
    ],
    "NT": [
        ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21),
        ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13),
        ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4),
        ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Timothy", 6),
        ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13),
        ("James", 5), ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1),
        ("3 John", 1), ("Jude", 1), ("Revelation", 22)
    ],
    "PG": [
        ("Psalms", 150), ("Proverbs", 31), ("Ecclesiastes", 12), ("Song of Solomon", 8)
    ]
}

# Flatten books into chapter list
def flatten(lst):
    result = []
    for book, count in lst:
        for i in range(1, count + 1):
            result.append(f"{book} {i}")
    return result

ot = flatten(chapters["OT"])
nt = flatten(chapters["NT"])
pg = flatten(chapters["PG"])

plan = []
start = datetime(2025, 1, 1)

for i in range(365):
    day = i + 1
    date = (start + timedelta(days=i)).strftime("%Y-%m-%d")

    ot_slice = ot[i*2:(i*2)+2]
    nt_slice = nt[i:i+1]
    pg_slice = pg[i:i+1]

    plan.append({
        "day": day,
        "date": date,
        "old_testament": "; ".join(ot_slice),
        "new_testament": "; ".join(nt_slice),
        "psalm_or_gospel": "; ".join(pg_slice)
    })

with open("reading_plan.json", "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=2)

print("✅ reading_plan.json created with 365 entries.")
