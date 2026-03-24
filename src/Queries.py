ALL_songs="""
SELECT * FROM rock_songs;
"""

SONGS_BY_ARTIST_YEAR ="""
    SELECT 
        Artist,
        Release_Year,
        COUNT(*) AS num_songs,
        AVG(PlayCount) AS avg_plays,
        SUM(PlayCount) AS total_plays

        from rock_songs 
        GROUP BY Artist,Release_Year ORDER BY num_songs DESC;
"""

TOP_ARTISTS ="""
    SELECT
        Artist,
        COUNT(*)       AS num_songs,
        AVG(PlayCount) AS avg_plays,
        SUM(PlayCount) AS total_plays
    FROM rock_songs
    GROUP BY Artist
    ORDER BY num_songs DESC
    LIMIT 15;
"""
 
SONGS_BY_DECADE ="""
    SELECT
        (CAST(Release_Year AS INT) / 10) * 10 AS decade,
        COUNT(*)                               AS num_songs,
        AVG(PlayCount)                         AS avg_plays
    FROM rock_songs
    WHERE Release_Year IS NOT NULL
    GROUP BY decade
    ORDER BY decade;
"""
 
MOST_PLAYED ="""
    SELECT Song, Artist, Release_Year, PlayCount
    FROM rock_songs
    ORDER BY PlayCount DESC
    LIMIT 20;
"""
 
PLAY_COUNT_DISTRIBUTION ="""
    SELECT PlayCount
    FROM rock_songs
    WHERE PlayCount IS NOT NULL;
"""