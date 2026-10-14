-- =====================================================================
-- NETFLIX DATA ANALYSIS PROJECT: DATABASE SCHEMA
-- Author: Senior Data Engineer / Senior Data Analyst
-- Target: PostgreSQL / MySQL / SQL Server compatible DDL
-- =====================================================================

-- Drop tables in reverse dependency order if they exist
DROP TABLE IF EXISTS netflix_genres;
DROP TABLE IF EXISTS netflix_countries;
DROP TABLE IF EXISTS netflix_cast;
DROP TABLE IF EXISTS netflix_directors;
DROP TABLE IF EXISTS netflix_titles;

-- Create core dim/fact table for Netflix Titles
CREATE TABLE netflix_titles (
    show_id VARCHAR(10) PRIMARY KEY,
    type VARCHAR(10) NOT NULL CHECK (type IN ('Movie', 'TV Show')),
    title VARCHAR(255) NOT NULL,
    date_added DATE NULL,
    release_year INT NOT NULL,
    rating VARCHAR(10) DEFAULT 'Unknown',
    duration VARCHAR(50) NULL,
    duration_minutes INT NULL,
    duration_seasons INT NULL,
    description TEXT NULL,
    year_added INT NULL,
    month_added VARCHAR(15) NULL,
    day_added INT NULL
);

-- Create bridge table for Directors (resolves multi-valued 'director' attribute)
CREATE TABLE netflix_directors (
    show_id VARCHAR(10),
    director VARCHAR(100),
    PRIMARY KEY (show_id, director),
    FOREIGN KEY (show_id) REFERENCES netflix_titles(show_id) ON DELETE CASCADE
);

-- Create bridge table for Cast/Actors (resolves multi-valued 'cast' attribute)
CREATE TABLE netflix_cast (
    show_id VARCHAR(10),
    actor VARCHAR(100),
    PRIMARY KEY (show_id, actor),
    FOREIGN KEY (show_id) REFERENCES netflix_titles(show_id) ON DELETE CASCADE
);

-- Create bridge table for Country (resolves multi-valued 'country' attribute)
CREATE TABLE netflix_countries (
    show_id VARCHAR(10),
    country VARCHAR(100),
    PRIMARY KEY (show_id, country),
    FOREIGN KEY (show_id) REFERENCES netflix_titles(show_id) ON DELETE CASCADE
);

-- Create bridge table for Genres (resolves multi-valued 'listed_in' attribute)
CREATE TABLE netflix_genres (
    show_id VARCHAR(10),
    genre VARCHAR(100),
    PRIMARY KEY (show_id, genre),
    FOREIGN KEY (show_id) REFERENCES netflix_titles(show_id) ON DELETE CASCADE
);

-- Create indexes for performance optimization
CREATE INDEX idx_titles_type ON netflix_titles(type);
CREATE INDEX idx_titles_release_year ON netflix_titles(release_year);
CREATE INDEX idx_titles_rating ON netflix_titles(rating);
CREATE INDEX idx_directors_name ON netflix_directors(director);
CREATE INDEX idx_cast_actor ON netflix_cast(actor);
CREATE INDEX idx_countries_name ON netflix_countries(country);
CREATE INDEX idx_genres_name ON netflix_genres(genre);
