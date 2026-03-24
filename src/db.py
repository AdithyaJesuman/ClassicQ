import sqlite3
import pandas as pd
from pathlib import Path

class RockDB:
    
    DB_URL = (
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud"
        "/IBM-ML0232EN-SkillsNetwork/asset/classic_rock.db"
    )

    def __init__(self, db_path: str = "data/classic_rock.db"):
        self.db_path = Path(db_path)
        self._con: sqlite3.Connection | None = None


    def connect(self) -> "RockDB":
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found at '{self.db_path}'.\n"
                "Run:  python main.py --download"
            )
        self._con = sqlite3.connect(self.db_path)
        print(f"Connected → {self.db_path}")
        return self

    def query(self, sql: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
        self._ensure_connected()
        return pd.read_sql(sql,self._con, parse_dates=parse_dates) # type: ignore

    def tables(self) -> list[str]:
        self._ensure_connected()
        df = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        return df["name"].tolist()

    def close(self) -> None:
        if self._con:
            self._con.close()
            self._con = None
            print("🔌 Connection closed.")

    def __enter__(self) -> "RockDB":
        return self.connect()

    def __exit__(self, *_) -> None:
        self.close()

    def _ensure_connected(self) -> None:
        if self._con is None:
            raise RuntimeError("No active connection — call .connect() first.")