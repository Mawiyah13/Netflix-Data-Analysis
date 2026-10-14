-- =====================================================================
-- NETFLIX DATA ANALYSIS PROJECT: DATA IMPORT GUIDE & SCRIPTS
-- Author: Senior Data Engineer / Senior Data Analyst
-- =====================================================================

-- This script contains SQL import scripts for PostgreSQL and MySQL to load
-- both the staging/flat dataset and the fully normalized 1NF tables.
-- Verify that python/data_cleaning.py has been run and generated the CSVs first!

-- ---------------------------------------------------------------------
-- DATABASE SETUP AND SCHEMA VERIFICATION
-- ---------------------------------------------------------------------
-- Make sure schema.sql has been executed to create the tables.

-- =====================================================================
-- APPROACH A: LOAD PRE-NORMALIZED CSV FILES (RECOMMENDED & ETL STANDARD)
-- =====================================================================
-- Since our Python script (python/data_cleaning.py) exports clean, normalized
-- relational CSVs, we can load them directly into our schema tables.

-- ---------------------------------------------------------------------
-- A.1 POSTGRESQL DIRECT COPY (Run via psql command-line client)
-- ---------------------------------------------------------------------
/*
-- NOTE: Replace '<project_path>' with your absolute path (e.g., 'C:/Netflix-Data-Analysis' or '/path/to/Netflix-Data-Analysis')

-- 1. Load netflix_titles
\copy netflix_titles(show_id, type, title, date_added, release_year, rating, duration, duration_minutes, duration_seasons, description, year_added, month_added, day_added) FROM '<project_path>/data/normalized_titles.csv' DELIMITER ',' CSV HEADER;

-- 2. Load directors
\copy netflix_directors(show_id, director) FROM '<project_path>/data/normalized_directors.csv' DELIMITER ',' CSV HEADER;

-- 3. Load cast
\copy netflix_cast(show_id, actor) FROM '<project_path>/data/normalized_cast.csv' DELIMITER ',' CSV HEADER;

-- 4. Load countries
\copy netflix_countries(show_id, country) FROM '<project_path>/data/normalized_countries.csv' DELIMITER ',' CSV HEADER;

-- 5. Load genres
\copy netflix_genres(show_id, genre) FROM '<project_path>/data/normalized_genres.csv' DELIMITER ',' CSV HEADER;

-- Optional Data Hygiene: Strip any residual whitespace from bridge tables
UPDATE netflix_directors SET director = TRIM(director);
UPDATE netflix_cast SET actor = TRIM(actor);
UPDATE netflix_countries SET country = TRIM(country);
UPDATE netflix_genres SET genre = TRIM(genre);
*/

-- ---------------------------------------------------------------------
-- A.2 MYSQL LOAD DATA INFILE (Configure secure_file_priv if required)
-- ---------------------------------------------------------------------
/*
-- NOTE: Replace '<project_path>' with your server-accessible path (forward slashes '/' recommended)

-- 1. Load netflix_titles
LOAD DATA INFILE '<project_path>/data/normalized_titles.csv'
INTO TABLE netflix_titles
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(show_id, type, title, @date_added, release_year, rating, duration, @duration_minutes, @duration_seasons, description, year_added, month_added, day_added)
SET 
  date_added = NULLIF(@date_added, ''),
  duration_minutes = NULLIF(@duration_minutes, ''),
  duration_seasons = NULLIF(@duration_seasons, '');

-- 2. Load directors (with whitespace trimming)
LOAD DATA INFILE '<project_path>/data/normalized_directors.csv'
INTO TABLE netflix_directors
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(show_id, @director)
SET director = TRIM(@director);

-- 3. Load cast (with whitespace trimming)
LOAD DATA INFILE '<project_path>/data/normalized_cast.csv'
INTO TABLE netflix_cast
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(show_id, @actor)
SET actor = TRIM(@actor);

-- 4. Load countries (with whitespace trimming)
LOAD DATA INFILE '<project_path>/data/normalized_countries.csv'
INTO TABLE netflix_countries
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(show_id, @country)
SET country = TRIM(@country);

-- 5. Load genres (with whitespace trimming)
LOAD DATA INFILE '<project_path>/data/normalized_genres.csv'
INTO TABLE netflix_genres
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(show_id, @genre)
SET genre = TRIM(@genre);
*/


-- =====================================================================
-- APPROACH B: LOAD FLAT CLEANED CSV AND EXPLODE IN SQL (ELT METHOD)
-- =====================================================================
-- Use this if you only upload a single flat CSV to the database server and
-- split comma-separated values into tables inside the database engine.

-- Create a staging table to hold the flat CSV file
CREATE TEMP TABLE staging_netflix (
    show_id VARCHAR(10),
    type VARCHAR(20),
    title VARCHAR(255),
    director TEXT,
    "cast" TEXT,
    country TEXT,
    date_added VARCHAR(50),
    release_year INT,
    rating VARCHAR(20),
    duration VARCHAR(50),
    listed_in TEXT,
    description TEXT,
    year_added INT,
    month_added VARCHAR(20),
    day_added INT,
    duration_minutes INT,
    duration_seasons INT
);

-- Copy the CSV file into the staging table (PostgreSQL example)
-- \copy staging_netflix FROM '<project_path>/data/cleaned_netflix.csv' DELIMITER ',' CSV HEADER;

-- Once data is in staging_netflix, populate the normalized production tables:

-- 1. Insert core titles (date_added is already formatted as YYYY-MM-DD in cleaned_netflix.csv)
-- INSERT INTO netflix_titles (show_id, type, title, date_added, release_year, rating, duration, duration_minutes, duration_seasons, description, year_added, month_added, day_added)
-- SELECT 
--     show_id, 
--     type, 
--     title, 
--     date_added::DATE,
--     release_year, 
--     rating, 
--     duration, 
--     duration_minutes, 
--     duration_seasons, 
--     description, 
--     year_added, 
--     month_added, 
--     day_added
-- FROM staging_netflix;

-- 2. Populate netflix_directors by splitting comma-separated string
-- INSERT INTO netflix_directors (show_id, director)
-- SELECT 
--     show_id, 
--     TRIM(director_split) as director
-- FROM staging_netflix,
-- UNNEST(STRING_TO_ARRAY(director, ',')) as director_split
-- WHERE director IS NOT NULL AND director <> 'Unknown' AND TRIM(director_split) <> '';

-- 3. Populate netflix_cast by splitting comma-separated string
-- INSERT INTO netflix_cast (show_id, actor)
-- SELECT 
--     show_id, 
--     TRIM(actor_split) as actor
-- FROM staging_netflix,
-- UNNEST(STRING_TO_ARRAY("cast", ',')) as actor_split
-- WHERE "cast" IS NOT NULL AND "cast" <> 'Unknown' AND TRIM(actor_split) <> '';

-- 4. Populate netflix_countries by splitting comma-separated string
-- INSERT INTO netflix_countries (show_id, country)
-- SELECT 
--     show_id, 
--     TRIM(country_split) as country
-- FROM staging_netflix,
-- UNNEST(STRING_TO_ARRAY(country, ',')) as country_split
-- WHERE country IS NOT NULL AND country <> 'Unknown' AND TRIM(country_split) <> '';

-- 5. Populate netflix_genres by splitting comma-separated string
-- INSERT INTO netflix_genres (show_id, genre)
-- SELECT 
--     show_id, 
--     TRIM(genre_split) as genre
-- FROM staging_netflix,
-- UNNEST(STRING_TO_ARRAY(listed_in, ',')) as genre_split
-- WHERE listed_in IS NOT NULL AND TRIM(genre_split) <> '';
