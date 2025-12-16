from pathlib import Path
from typing import List, Dict, Optional
import docx
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.tnved import tnved
from app.schemas.tnved import TNVedCreate

class TNVedParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> List[Dict]:
        doc = docx.Document(self.file_path)
        codes = []
        
        # Strategy: Iterate through all tables, looking for Code/Description pairs.
        # This assumes the document contains one or more tables with this structure.
        for table in doc.tables:
            for row in table.rows:
                # Assuming 2 columns or simple structure: Code | Description
                cells = row.cells
                if not cells:
                    continue
                
                text_content = [cell.text.strip() for cell in cells]
                # Heuristic: Find the cell that looks like a code
                code_text = ""
                description = ""
                
                # Check column 0 for code
                possible_code = text_content[0].replace(" ", "").replace("\n", "")
                if self._is_code(possible_code):
                    code_text = possible_code
                    if len(text_content) > 1:
                        description = " ".join(text_content[1:])
                # In some files code might be in different column, but Standard is col 0
                
                if code_text:
                    # Clean code
                    clean_code = re.sub(r"[^\d]", "", code_text)
                    if not clean_code: 
                        continue

                    # Determine hierarchy level
                    # 2 digits = Chapter
                    # 4 digits = Heading
                    # 6 digits = Subheading
                    # 10 digits = Full Code
                    level = self._get_level(clean_code)
                    
                    codes.append({
                        "code": clean_code,
                        "full_code": code_text, # Keep original formatting if needed
                        "description": description.replace("\n", " ").strip(),
                        "level": level
                    })
        return codes

    def _is_code(self, text: str) -> bool:
        # Simple check: starts with digit, length checks?
        # Remove non-digits
        clean = re.sub(r"[^\d]", "", text)
        return len(clean) >= 2

    def _get_level(self, code: str) -> int:
        l = len(code)
        if l == 2: return 1
        if l == 4: return 2
        if l == 6: return 3
        if l >= 10: return 4
        return 0

    async def save_to_db(self, db: AsyncSession, data: List[Dict]):
        # Saving needs to handle hierarchy (parent_id)
        # We process in order. We assume the list is ordered by code.
        # We need to cache parents.
        # Stack concept: 
        # last_level_1, last_level_2, last_level_3
        
        parents = {} # {level: db_id}

        for item in data:
            level = item["level"]
            parent_id = None
            
            # Find closest parent level < current level
            # e.g. for level 4, parent could be 3, 2, or 1
            for p_level in range(level - 1, 0, -1):
                if p_level in parents:
                    parent_id = parents[p_level]
                    break
            
            # Prepare schema
            tnved_in = TNVedCreate(
                code=item["code"],
                full_code=item["full_code"],
                description=item["description"],
                level=level,
                parent_id=parent_id
            )
            
            try:
                # Check if exists to avoid duplicates
                existing = await tnved.get_by_code(db, code=item["code"])
                if existing:
                    # Update
                    # db_obj = await tnved.update(db, db_obj=existing, obj_in=tnved_in)
                    # For bulk load simplicity we might skip update if content same or overwrite
                    # Let's overwrite description
                    db_obj = await tnved.update(db, db_obj=existing, obj_in=tnved_in)
                else:
                    db_obj = await tnved.create(db, obj_in=tnved_in)
                
                # Update parent cache
                parents[level] = db_obj.id
                
                # Clear deeper levels as we are on a new branch for this level
                to_remove = [k for k in parents.keys() if k > level]
                for k in to_remove:
                    del parents[k]

            except Exception as e:
                print(f"Error saving {item['code']}: {e}")
                # Continue or generic error handling
