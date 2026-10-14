-- =====================================================================
-- NETFLIX DATA ANALYSIS PROJECT: ANALYTICAL SQL QUERIES
-- Author: Senior Data Analyst / BI Developer
-- Target: Standard ANSI SQL (works on PostgreSQL, MySQL, SQL Server)
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: Movie vs TV Show Count
-- Purpose: Understand the breakdown of Netflix's library content types.
-- ---------------------------------------------------------------------
SELECT 
    type, 
    COUNT(*) as total_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM netflix_titles), 2) as percentage
FROM netflix_titles
GROUP BY type;

-- ---------------------------------------------------------------------
-- QUERY 2: Top 10 Countries Producing the Most Content
-- Purpose: Geographical distribution of production (handles split countries).
-- ---------------------------------------------------------------------
SELECT 
    TRIM(country) as country, 
    COUNT(*) as total_titles,
    RANK() OVER (ORDER BY COUNT(*) DESC) as country_rank
FROM netflix_countries
GROUP BY TRIM(country)
ORDER BY total_titles DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 3: Movies by Country
-- Purpose: Analyze specifically which countries produce the most movies.
-- ---------------------------------------------------------------------
SELECT 
    TRIM(nc.country) as country, 
    COUNT(nt.show_id) as movie_count
FROM netflix_countries nc
JOIN netflix_titles nt ON nc.show_id = nt.show_id
WHERE nt.type = 'Movie'
GROUP BY TRIM(nc.country)
ORDER BY movie_count DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 4: Top 10 Directors by Content Count
-- Purpose: Identify the most frequent directors collaborating with Netflix.
-- ---------------------------------------------------------------------
SELECT 
    TRIM(director) as director, 
    COUNT(show_id) as directed_count
FROM netflix_directors
GROUP BY TRIM(director)
ORDER BY directed_count DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 5: Most Common Genres (listed_in)
-- Purpose: Genre distribution analysis.
-- ---------------------------------------------------------------------
SELECT 
    TRIM(genre) as genre, 
    COUNT(show_id) as genre_count,
    ROUND(COUNT(show_id) * 100.0 / (SELECT COUNT(*) FROM netflix_titles), 2) as coverage_percentage
FROM netflix_genres
GROUP BY TRIM(genre)
ORDER BY genre_count DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 6: Year-wise Releases (Original Content Release Year)
-- Purpose: Distribution of titles based on original theatrical/broadcast year.
-- ---------------------------------------------------------------------
SELECT 
    release_year, 
    COUNT(*) as titles_released
FROM netflix_titles
GROUP BY release_year
ORDER BY release_year DESC
LIMIT 20;

-- ---------------------------------------------------------------------
-- QUERY 7: Content Added Every Year (Platform Growth Trend)
-- Purpose: Monitor how Netflix has scaled its content addition volume over years.
-- ---------------------------------------------------------------------
SELECT 
    year_added, 
    COUNT(*) as titles_added,
    SUM(COUNT(*)) OVER (ORDER BY year_added) as cumulative_titles
FROM netflix_titles
GROUP BY year_added
ORDER BY year_added ASC;

-- ---------------------------------------------------------------------
-- QUERY 8: Content Added Every Month (Seasonality Analysis)
-- Purpose: Determine if Netflix prefers adding content in specific months.
-- ---------------------------------------------------------------------
SELECT 
    month_added, 
    COUNT(*) as titles_added
FROM netflix_titles
GROUP BY month_added
ORDER BY titles_added DESC;

-- ---------------------------------------------------------------------
-- QUERY 9: Distribution of Content Ratings
-- Purpose: Identify the target audience mix (Adult, Teens, Kids).
-- ---------------------------------------------------------------------
SELECT 
    rating, 
    type,
    COUNT(*) as count
FROM netflix_titles
GROUP BY rating, type
ORDER BY count DESC;

-- ---------------------------------------------------------------------
-- QUERY 10: Most Frequent Content Rating (Overall Mode)
-- Purpose: Extract the modal rating value.
-- ---------------------------------------------------------------------
SELECT 
    rating, 
    COUNT(*) as frequency
FROM netflix_titles
GROUP BY rating
ORDER BY frequency DESC
LIMIT 1;

-- ---------------------------------------------------------------------
-- QUERY 11: Average Movie Duration
-- Purpose: Average runtime of feature films.
-- ---------------------------------------------------------------------
SELECT 
    ROUND(AVG(duration_minutes), 2) as avg_duration_minutes,
    MIN(duration_minutes) as min_duration_minutes,
    MAX(duration_minutes) as max_duration_minutes
FROM netflix_titles
WHERE type = 'Movie';

-- ---------------------------------------------------------------------
-- QUERY 12: Top 10 Longest Movies
-- Purpose: Identify outliers/extremely long movies.
-- ---------------------------------------------------------------------
SELECT 
    title, 
    duration_minutes, 
    release_year
FROM netflix_titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL
ORDER BY duration_minutes DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 13: Top 10 TV Shows with the Most Seasons
-- Purpose: Longest-running television series.
-- ---------------------------------------------------------------------
SELECT 
    title, 
    duration_seasons, 
    release_year
FROM netflix_titles
WHERE type = 'TV Show' AND duration_seasons IS NOT NULL
ORDER BY duration_seasons DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 14: Top 15 Most Common Actors (Cast members)
-- Purpose: Identify most frequent cast members.
-- ---------------------------------------------------------------------
SELECT 
    TRIM(actor) as actor, 
    COUNT(show_id) as appearances
FROM netflix_cast
WHERE TRIM(actor) <> 'Unknown'
GROUP BY TRIM(actor)
ORDER BY appearances DESC
LIMIT 15;

-- ---------------------------------------------------------------------
-- QUERY 15: Latest 10 Added Titles on Netflix
-- Purpose: Monitor recently published items.
-- ---------------------------------------------------------------------
-- Note: Ordered by date_added DESC for accurate chronological sorting.
-- Sorting by text 'month_added DESC' would be alphabetical ('September' > 'December').
SELECT 
    title, 
    type, 
    date_added, 
    release_year
FROM netflix_titles
ORDER BY date_added DESC, show_id DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 16 (BONUS): Top 5 Directors who specialize in Dramas
-- Purpose: Advanced analysis joining titles, directors, and genres.
-- ---------------------------------------------------------------------
SELECT 
    TRIM(nd.director) as director, 
    COUNT(nd.show_id) as drama_count
FROM netflix_directors nd
JOIN netflix_genres ng ON nd.show_id = ng.show_id
WHERE TRIM(ng.genre) LIKE '%Drama%'
GROUP BY TRIM(nd.director)
ORDER BY drama_count DESC
LIMIT 5;

-- ---------------------------------------------------------------------
-- QUERY 17 (BONUS): Countries Producing Most Movies vs TV Shows
-- Purpose: CTE showing comparison metrics.
-- ---------------------------------------------------------------------
WITH CountryCounts AS (
    SELECT 
        TRIM(nc.country) as country,
        SUM(CASE WHEN nt.type = 'Movie' THEN 1 ELSE 0 END) as movie_count,
        SUM(CASE WHEN nt.type = 'TV Show' THEN 1 ELSE 0 END) as tv_count,
        COUNT(*) as total_count
    FROM netflix_countries nc
    JOIN netflix_titles nt ON nc.show_id = nt.show_id
    GROUP BY TRIM(nc.country)
)
SELECT 
    country, 
    movie_count, 
    tv_count, 
    total_count,
    ROUND(movie_count * 100.0 / total_count, 2) as movie_percentage
FROM CountryCounts
WHERE total_count >= 10
ORDER BY total_count DESC
LIMIT 10;
