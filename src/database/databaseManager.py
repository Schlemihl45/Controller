import sqlite3
from pathlib import Path
from datetime import datetime
from database.project_model import Project

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "database.db"
PROJECTS_ROOT = BASE_DIR.parent / "projects"


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
            CREATE TABLE IF NOT EXISTS projects (
                name TEXT PRIMARY KEY NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                json_path TEXT
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS gcodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                filename TEXT NOT NULL,
                tool_used TEXT,
                FOREIGN KEY (project_name) REFERENCES projects(name)
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
        """Löscht ein Werkzeug nach ID. Gibt True zurück wenn gelöscht."""
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
    # Projekte synchronisieren mit Dateisystem
    # ---------------------------------------------------------
    def sync_with_filesystem(self):
        """Synchronisiert DB-Einträge mit vorhandenen Projektordnern."""
        PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
        existing_folders = {p for p in PROJECTS_ROOT.iterdir() if p.is_dir()}

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM projects")
            db_projects = {row[0] for row in cur.fetchall()}

            new_projects = [f for f in existing_folders if f.name not in db_projects]
            removed_projects = [n for n in db_projects if n not in {f.name for f in existing_folders}]

            # Neue hinzufügen + JSON erzeugen falls nötig
            for folder in new_projects:
                proj_obj = Project.load_from_json(folder)

                json_file = folder / f"{folder.name}.json"

                proj_obj.save_to_json(json_file)  # schreibt Datei mit Zeitpunkten

                cur.execute("""
                    INSERT INTO projects (name,path,description,json_path)
                    VALUES (?, ?, ?, ?);
                    """, (proj_obj.name, str(proj_obj.path), proj_obj.description, str(json_file)))

            # Nicht mehr existierende löschen
            for obsolete_name in removed_projects:
                cur.execute("DELETE FROM projects WHERE name=?", (obsolete_name,))

            conn.commit()

        # ---------------------------------------------------------
        # Projekte laden + fehlende JSON erzeugen falls nötig
        # ---------------------------------------------------------

    def load_projects(self, order_by: str = "name"):
        PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name,path,description,json_path FROM projects ORDER BY name ASC")
            rows = cur.fetchall()
            db_names = {r[0] for r in rows}

        folders = [f for f in PROJECTS_ROOT.iterdir() if f.is_dir()]

        with self._connect() as conn:
            cur = conn.cursor()

            for folder in folders:
                json_file = folder / f"{folder.name}.json"

                if folder.name not in db_names:
                    print(f"Adding missing project '{folder.name}' to database.")
                    proj_obj = Project(
                        name=folder.name, path=folder, description="", stats={})
                    proj_obj.save_to_json(json_file)
                    cur.execute("""
                         INSERT INTO projects (name,path,description,json_path)
                         VALUES (?, ?, ?, ?);
                     """, (proj_obj.name, str(proj_obj.path), proj_obj.description, str(json_file)))

                elif not json_file.exists():
                    print(f"Creating missing JSON file for project '{folder.name}'.")
                    proj_obj = Project.load_from_json(folder)
                    proj_obj.save_to_json(json_file)
                    cur.execute("UPDATE projects SET json_path=? WHERE name=?",
                                (str(json_file), folder.name))

            conn.commit()

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name,path,json_path FROM projects ORDER BY name ASC")
            rows = cur.fetchall()

        return [
            Project.load_from_json(Path(row[1]), Path(row[2]))
            for row in rows
        ]