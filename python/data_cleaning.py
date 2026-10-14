import os
import pandas as pd
import numpy as np

def load_data(filepath):
    """Loads the Netflix CSV dataset."""
    print(f"Loading raw dataset from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    df = pd.read_csv(filepath)
    # Remove embedded line breaks from all text columns
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = (
            df[col]
            .str.replace(r'[\r\n]+', ' ', regex=True)
            .str.strip()
        )

    print(f"Dataset loaded with shape: {df.shape}")
    return df

def trim_strings(df):
    """Cleans whitespace and embedded line breaks from string columns."""
    print("Trimming whitespace from string columns...")
    
    string_cols = df.select_dtypes(include=['object', 'str']).columns

    for col in string_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace('\r', ' ', regex=False)
            .str.replace('\n', ' ', regex=False)
            .str.strip()
        )

    return df

def clean_missing_values(df):
    """Handles missing values in director, cast, country, date_added, and rating."""
    print("Handling missing values...")
    
    # 1. Fill missing values in text columns with 'Unknown'
    df['director'] = df['director'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')
    df['cast'] = df['cast'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')
    df['country'] = df['country'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')
    
    # 2. Impute missing ratings or mark as 'Unknown'
    # Netflix rating nulls can be mapped to typical ratings, or marked 'Unknown'
    df['rating'] = df['rating'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')
    
    # 3. Drop rows with missing date_added as they are very few (< 0.1%)
    initial_rows = len(df)
    df = df.dropna(subset=['date_added'])
    df = df[df['date_added'] != 'nan']
    dropped_rows = initial_rows - len(df)
    print(f"Dropped {dropped_rows} rows due to missing 'date_added'.")
    
    return df

def standardize_categories(df):
    """Standardizes type category values to 'Movie' and 'TV Show'."""
    print("Standardizing content categories (type)...")
    # Standardize case-insensitively using a mapping dictionary
    type_lower = df['type'].str.lower().str.strip()
    df['type'] = type_lower.map({'movie': 'Movie', 'tv show': 'TV Show', 'tv-show': 'TV Show'}).fillna('Unknown')
    # Validate types
    valid_types = ['Movie', 'TV Show']
    df = df[df['type'].isin(valid_types)]
    print(f"Unique types after standardization: {df['type'].unique()}")
    return df

def convert_dates(df):
    """Converts date_added into datetime and extracts year, month, and day added."""
    print("Converting date_added and extracting date parts...")
    
    # Parse dates robustly
    df['date_added_dt'] = pd.to_datetime(df['date_added'], errors='coerce', format='%B %d, %Y')
    
    # For any dates that failed standard parsing, try a generic parser or drop them if they cannot be parsed
    null_dates = df['date_added_dt'].isnull().sum()
    if null_dates > 0:
        print(f"Warning: {null_dates} dates failed to parse with standard format. Trying fallback parser...")
        df.loc[df['date_added_dt'].isnull(), 'date_added_dt'] = pd.to_datetime(df['date_added'], errors='coerce')
    
    # Drop rows that could not be parsed at all
    df = df.dropna(subset=['date_added_dt'])
    
    # Extract features
    df['year_added'] = df['date_added_dt'].dt.year.astype(int)
    df['month_added'] = df['date_added_dt'].dt.strftime('%B')
    df['day_added'] = df['date_added_dt'].dt.day.astype(int)

    # Convert date_added to MySQL DATE format: YYYY-MM-DD
    df['date_added'] = df['date_added_dt'].dt.strftime('%Y-%m-%d')

    # Clean up temporary column
    df = df.drop(columns=['date_added_dt'])
    return df

def convert_duration(df):
    """Converts duration to numeric values for minutes (Movies) and seasons (TV Shows)."""
    print("Converting duration to numeric values...")
    
    # Initialize new columns
    df['duration_minutes'] = np.nan
    df['duration_seasons'] = np.nan
    
    # Parse duration
    for idx, row in df.iterrows():
        duration_val = str(row['duration']).lower()
        if 'min' in duration_val:
            # Extract digits
            minutes = int(''.join(filter(str.isdigit, duration_val)))
            df.at[idx, 'duration_minutes'] = minutes
        elif 'season' in duration_val:
            seasons = int(''.join(filter(str.isdigit, duration_val)))
            df.at[idx, 'duration_seasons'] = seasons
            
    # Fill remaining NaNs with 0 or correct type and convert to nullable Int64
    df['duration_minutes'] = df['duration_minutes'].astype('Int64')
    df['duration_seasons'] = df['duration_seasons'].astype('Int64')
    
    return df

def export_normalized_tables(df, output_dir):
    """Generates and exports normalized dimension tables to resolve multi-valued columns."""
    print("Generating normalized dimension tables for SQL import...")
    
    # 1. netflix_titles (Dimension/Fact Table)
    # Remove columns that contain multi-valued strings to keep it normalized
    titles_df = df.drop(columns=['director', 'cast', 'country', 'listed_in'])
    # Align column order with schema.sql and import_data.sql
    titles_cols = [
        'show_id', 'type', 'title', 'date_added', 'release_year', 'rating',
        'duration', 'duration_minutes', 'duration_seasons', 'description',
        'year_added', 'month_added', 'day_added'
    ]
    titles_df = titles_df[titles_cols]
    titles_path = os.path.join(output_dir, 'normalized_titles.csv')
    titles_df.to_csv(titles_path, index=False)
    print(f"- Exported {titles_path} with shape {titles_df.shape}")

    
    # Helper function to explode comma-separated values and map back to show_id
    def split_and_explode(dataframe, column_name, target_col_name):
        split_df = dataframe[['show_id', column_name]].copy()
        split_df[column_name] = split_df[column_name].astype(str).str.split(',')
        exploded = split_df.explode(column_name)
        
        # Remove embedded double quotes for MySQL CSV compatibility
        exploded[column_name] = exploded[column_name].str.replace('"', '', regex=False)

        # Drop duplicates and rows that are empty or 'Unknown'
        exploded = exploded[exploded[column_name].notna() & (exploded[column_name] != '') & (exploded[column_name] != 'Unknown')]
        exploded = exploded.rename(columns={column_name: target_col_name}).drop_duplicates()
        return exploded

    # 2. netflix_directors
    directors_df = split_and_explode(df, 'director', 'director')
    directors_path = os.path.join(output_dir, 'normalized_directors.csv')
    directors_df.to_csv(directors_path, index=False)
    print(f"- Exported {directors_path} with shape {directors_df.shape}")

    # 3. netflix_cast
    cast_df = split_and_explode(df, 'cast', 'actor')
    cast_path = os.path.join(output_dir, 'normalized_cast.csv')
    cast_df.to_csv(cast_path, index=False)
    print(f"- Exported {cast_path} with shape {cast_df.shape}")

    # 4. netflix_countries
    countries_df = split_and_explode(df, 'country', 'country')
    countries_path = os.path.join(output_dir, 'normalized_countries.csv')
    countries_df.to_csv(countries_path, index=False)
    print(f"- Exported {countries_path} with shape {countries_df.shape}")

    # 5. netflix_genres
    genres_df = split_and_explode(df, 'listed_in', 'genre')
    genres_path = os.path.join(output_dir, 'normalized_genres.csv')
    genres_df.to_csv(genres_path, index=False)
    print(f"- Exported {genres_path} with shape {genres_df.shape}")

def clean_data_pipeline(input_path, output_path):
    """Executes the complete data cleaning pipeline."""
    df = load_data(input_path)
    
    # Drop duplicate rows
    initial_shape = df.shape
    df = df.drop_duplicates()
    print(f"Dropped {initial_shape[0] - df.shape[0]} duplicate rows.")
    
    # Run cleaning functions
    df = trim_strings(df)
    df = clean_missing_values(df)
    df = standardize_categories(df)
    df = convert_dates(df)
    df = convert_duration(df)
    
    # Sort by show_id for consistency
    df['id_num'] = df['show_id'].str.extract(r'(\d+)').astype(int)
    df = df.sort_values(by='id_num').drop(columns=['id_num'])
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Save cleaned dataset (flat table for Power BI)
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_csv(output_path, index=False)
    print(f"Cleaned dataset successfully exported to: {output_path}")
    print(f"Final shape: {df.shape}")
    
    # Save normalized tables for SQL
    export_normalized_tables(df, output_dir)
    return df

if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    raw_path = os.fspath(base_dir / "data" / "netflix_titles.csv")
    cleaned_path = os.fspath(base_dir / "data" / "cleaned_netflix.csv")
    clean_data_pipeline(raw_path, cleaned_path)
