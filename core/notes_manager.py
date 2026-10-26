import os
import json
import time

NOTES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "notes.json"))

class NotesManager:
    @staticmethod
    def _load():
        if not os.path.exists(NOTES_FILE):
            return []
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save(notes):
        os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)

    @classmethod
    def add_note(cls, content):
        notes = cls._load()
        note = {
            "id": int(time.time() * 1000),
            "content": content.strip(),
            "created_at": time.strftime("%d/%m/%Y %H:%M")
        }
        notes.insert(0, note)
        cls._save(notes)
        return note

    @classmethod
    def list_notes(cls):
        return cls._load()

    @classmethod
    def delete_note(cls, note_id):
        notes = cls._load()
        notes = [n for n in notes if n["id"] != int(note_id)]
        cls._save(notes)
        return True

    @classmethod
    def clear_all(cls):
        cls._save([])
        return True
