import asyncio
import sys
import os
import argparse
from pathlib import Path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.parsers.tnved_word_parser import TNVedParser

async def main(file_path: str):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Parsing {file_path}...")
    parser = TNVedParser(file_path)
    data = parser.parse()
    print(f"Found {len(data)} codes. Saving to database...")
    
    async with AsyncSessionLocal() as db:
        await parser.save_to_db(db, data)
    
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load TNVED codes from Word file")
    parser.add_argument("--file", type=str, required=True, help="Path to .docx file")
    args = parser.parse_args()
    
    asyncio.run(main(args.file))
