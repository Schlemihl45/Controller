import sqlite3
from datetime import datetime
from pathlib import Path

from database.workpiece_model import Workpiece

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "database.db"
WORKPIECES_ROOT = BASE_DIR.parent / "workpieces"


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # ---------------------------------------------------------
    # Datenbank initialisieren
    # ---------------------------------------------------------
    def initialize(self):
        if not DB_PATH.exists():
            print(f"Database not found, creating new DB at {DB_PATH}")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                diameter REAL,
                radius REAL,
                cutting_length REAL,
                length REAL,
                flutes INTEGER NOT NULL,
                zOffset REAL,
                rOffset REAL,
                supplier TEXT,
                description TEXT,
                time_used REAL,
                last_used DATETIME
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workpieces (
                name TEXT PRIMARY KEY NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                json_path TEXT
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS gcodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workpiece_name TEXT NOT NULL,
                filename TEXT NOT NULL,
                tool_used TEXT,
                FOREIGN KEY (workpiece_name) REFERENCES workpieces(name)
            )
            """)

            conn.commit()
            conn.close()
            print("Database initialized successfully.")
        else:
            print(f"Database already exists at {DB_PATH}")

    def get_all_tools(self, order_by: str = "id"):
        query = f"""
            SELECT id, name, type, diameter, radius,
                   cutting_length, length, flutes,
                   zOffset, rOffset, supplier, description
            FROM tools ORDER BY {order_by} ASC
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def add_tool(self, tool_data: tuple):
        query = """
            INSERT INTO tools (name, type, diameter, radius,
                               cutting_length, length,
                               flutes, zOffset,
                               rOffset, supplier,
                               description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tool_data)
            conn.commit()

    def save_tool(self,
                  tool_id: int | None,
                  name: str,
                  type_: str,
                  diameter: float,
                  radius: float,
                  cutting_length: float,
                  length: float,
                  flutes: int | None,
                  zOffset: float,
                  rOffset: float,
                  supplier: str,
                  description: str):

        with self._connect() as conn:
            cursor = conn.cursor()

            if tool_id:
                cursor.execute("""
                    UPDATE tools SET
                        name=?, type=?, diameter=?, radius=?,
                        cutting_length=?, length=?, flutes=?,
                        zOffset=?, rOffset=?, supplier=?, description=?
                    WHERE id=?
                """, (name, type_, diameter, radius, cutting_length, length,
                      flutes, zOffset, rOffset, supplier, description, tool_id))
                print(f"Tool '{name}' updated.")
                return tool_id
            else:
                cursor.execute("""
                    INSERT INTO tools (name,type,diameter,radius,
                                       cutting_length,length,flutes,zOffset,rOffset,supplier,description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, type_, diameter, radius, cutting_length, length,
                      flutes, zOffset, rOffset, supplier, description))
                new_id = cursor.lastrowid
                print(f"Tool '{name}' created.")
                return new_id

    def delete_tool(self, id_: int) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM tools WHERE id=?", (id_,))
            result = cursor.fetchone()

            if not result:
                print(f"Tool with ID {id_} does not exist.")
                return False

            cursor.execute("DELETE FROM tools WHERE id=?", (id_,))
            print(f"Tool '{result[0]}' deleted.")
            return True

    # ---------------------------------------------------------
    # Workpieces synchronisieren mit Dateisystem
    # ---------------------------------------------------------
    def sync_with_filesystem(self):
        WORKPIECES_ROOT.mkdir(parents=True, exist_ok=True)
        existing_folders = {p for p in WORKPIECES_ROOT.iterdir() if p.is_dir()}

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM workpieces")
            db_workpieces = {row[0] for row in cur.fetchall()}

            new_workpieces = [f for f in existing_folders if f.name not in db_workpieces]
            removed_workpieces = [n for n in db_workpieces if n not in {f.name for f in existing_folders}]

            for folder in new_workpieces:
                wp_obj = Workpiece.load_from_json(folder)
                json_file = folder / f"{folder.name}.json"
                wp_obj.save_to_json(json_file)

                cur.execute("""
                    INSERT INTO workpieces (name,path,description,json_path)
                    VALUES (?, ?, ?, ?);
                """, (wp_obj.name, str(wp_obj.path), wp_obj.description, str(json_file)))

            for obsolete_name in removed_workpieces:
                cur.execute("DELETE FROM workpieces WHERE name=?", (obsolete_name,))

            conn.commit()

    # ---------------------------------------------------------
    # Workpieces laden
    # ---------------------------------------------------------
    def load_workpieces(self, order_by: str = "name"):
        WORKPIECES_ROOT.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name,path,description,json_path FROM workpieces ORDER BY name ASC")
            rows = cur.fetchall()
            db_names = {r[0] for r in rows}

        folders = [f for f in WORKPIECES_ROOT.iterdir() if f.is_dir()]

        with self._connect() as conn:
            cur = conn.cursor()

            for folder in folders:
                json_file = folder / f"{folder.name}.json"

                if folder.name not in db_names:
                    wp_obj = Workpiece(
                        name=folder.name, path=folder, description="", stats={}
                    )
                    wp_obj.save_to_json(json_file)
                    cur.execute("""
                        INSERT INTO workpieces (name,path,description,json_path)
                        VALUES (?, ?, ?, ?);
                    """, (wp_obj.name, str(wp_obj.path), wp_obj.description, str(json_file)))

                elif not json_file.exists():
                    wp_obj = Workpiece.load_from_json(folder)
                    wp_obj.save_to_json(json_file)
                    cur.execute(
                        "UPDATE workpieces SET json_path=? WHERE name=?",
                        (str(json_file), folder.name)
                    )

            conn.commit()

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name,path,json_path FROM workpieces ORDER BY name ASC")
            rows = cur.fetchall()

        return [
            Workpiece.load_from_json(Path(row[1]), Path(row[2]))
            for row in rows
        ]
