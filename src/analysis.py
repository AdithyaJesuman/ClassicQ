import pandas as pd
from src.db import RockDB
from src import Queries
 
 
def load_all_songs(db: RockDB) -> pd.DataFrame:
    return db.query(Queries.ALL_songs)
 
 
def top_artists(db: RockDB, limit: int = 15) -> pd.DataFrame:
    sql = Queries.TOP_ARTISTS.replace("LIMIT 15", f"LIMIT {limit}")
    return db.query(sql)
 
 
def songs_by_artist_year(db: RockDB) -> pd.DataFrame:
    return db.query(Queries.SONGS_BY_ARTIST_YEAR, parse_dates=["Release_Year"])
 
 
def songs_by_decade(db: RockDB) -> pd.DataFrame:
    df = db.query(Queries.SONGS_BY_DECADE)
    df["decade_label"] = df["decade"].astype(int).astype(str) + "s"
    return df
 
 
def most_played(db: RockDB) -> pd.DataFrame:
    return db.query(Queries.MOST_PLAYED)
 
 
 
def play_count_distribution(db: RockDB) -> pd.Series:
    df = db.query(Queries.PLAY_COUNT_DISTRIBUTION)
    return df["PlayCount"]
 
 
def summary_stats(db: RockDB) -> dict:
    songs = load_all_songs(db)
    play_counts = songs["PlayCount"].dropna()
    top = top_artists(db, limit=1)
 
    return {
        "total_songs":     len(songs),
        "unique_artists":  songs["Artist"].nunique(),
        "year_range":      f"{int(songs['Release_Year'].min())} – {int(songs['Release_Year'].max())}",
        "top_artist":      top.iloc[0]["Artist"],
        "avg_play_count":  round(play_counts.mean(), 2),
        "median_plays":    round(play_counts.median(), 2),
        "max_plays":       int(play_counts.max()),
    }