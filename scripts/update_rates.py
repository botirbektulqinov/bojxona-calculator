import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.parsers.lex_uz_parser import LexUzParser
from app.core.config import settings

async def main():
    print("Starting Tariff Rate Update from Lex.uz...")
    print("Tariff update logic is not fully implemented yet (requires complex HTML parsing).")

if __name__ == "__main__":
    asyncio.run(main())
