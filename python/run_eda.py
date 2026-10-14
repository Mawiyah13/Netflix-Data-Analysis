import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_eda(cleaned_csv_path, output_img_dir):
    print(f"Loading cleaned dataset from {cleaned_csv_path}...")
    if not os.path.exists(cleaned_csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {cleaned_csv_path}. Please run data_cleaning.py first.")
    
    df = pd.read_csv(cleaned_csv_path)
    os.makedirs(output_img_dir, exist_ok=True)
    print(f"Loaded {len(df)} records. Starting EDA and saving figures to {output_img_dir}...")

    # Set styling
    sns.set_theme(style="darkgrid")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['axes.facecolor'] = '#181818'
    plt.rcParams['figure.facecolor'] = '#121212'
    plt.rcParams['text.color'] = '#E5E5E5'
    plt.rcParams['axes.labelcolor'] = '#E5E5E5'
    plt.rcParams['xtick.color'] = '#E5E5E5'
    plt.rcParams['ytick.color'] = '#E5E5E5'

    # Color Palette: Netflix Red and Dark/Gray shades
    primary_color = '#E50914'
    secondary_color = '#564d4d'
    light_gray = '#B3B3B3'

    # 1. Content Types Breakdown (Movie vs TV Show)
    type_counts = df['type'].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', colors=[primary_color, secondary_color], 
            textprops={'fontsize': 12, 'color': 'white'}, startangle=90, explode=[0, 0.05])
    plt.title('Netflix Content Types: Movies vs TV Shows', fontsize=14, color='white', weight='bold')
    plt.savefig(os.path.join(output_img_dir, 'content_type_ratio.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved content_type_ratio.png")

    # 2. Cumulative Content Growth over Years
    growth_df = df.groupby(['year_added', 'type']).size().unstack(fill_value=0).cumsum()
    plt.figure(figsize=(10, 6))
    plt.plot(growth_df.index, growth_df['Movie'], color=primary_color, label='Movies', linewidth=3.0)
    plt.plot(growth_df.index, growth_df['TV Show'], color=light_gray, label='TV Shows', linewidth=3.0, linestyle='--')
    plt.title('Netflix Content Growth Trajectory (Cumulative)', fontsize=14, color='white', weight='bold')
    plt.xlabel('Year Added', fontsize=11, color='white')
    plt.ylabel('Cumulative Titles', fontsize=11, color='white')
    plt.legend(facecolor='#181818', edgecolor='none', labelcolor='white')
    plt.grid(color='#333333', linestyle=':')
    plt.savefig(os.path.join(output_img_dir, 'content_growth.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved content_growth.png")

    # 3. Top 10 Countries producing content
    countries_series = df['country'].str.split(', ').dropna().explode()
    countries_series = countries_series[countries_series != 'Unknown']
    top_countries = countries_series.value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_countries.values, y=top_countries.index, palette='Reds_r', hue=top_countries.index, legend=False)
    plt.title('Top 10 Countries Producing Netflix Content', fontsize=14, color='white', weight='bold')
    plt.xlabel('Number of Titles', fontsize=11, color='white')
    plt.ylabel('Country', fontsize=11, color='white')
    plt.savefig(os.path.join(output_img_dir, 'top_countries.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved top_countries.png")

    # 4. Top 10 Directors
    directors_series = df['director'].str.split(', ').dropna().explode()
    directors_series = directors_series[directors_series != 'Unknown']
    top_directors = directors_series.value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_directors.values, y=top_directors.index, palette='Reds_r', hue=top_directors.index, legend=False)
    plt.title('Top 10 Most Frequent Directors on Netflix', fontsize=14, color='white', weight='bold')
    plt.xlabel('Number of Titles Directed', fontsize=11, color='white')
    plt.ylabel('Director', fontsize=11, color='white')
    plt.savefig(os.path.join(output_img_dir, 'top_directors.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved top_directors.png")

    # 5. Top 10 Genres
    genres_series = df['listed_in'].str.split(', ').dropna().explode()
    top_genres = genres_series.value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_genres.values, y=top_genres.index, palette='Reds_r', hue=top_genres.index, legend=False)
    plt.title('Top 10 Netflix Content Genres', fontsize=14, color='white', weight='bold')
    plt.xlabel('Number of Titles', fontsize=11, color='white')
    plt.ylabel('Genre', fontsize=11, color='white')
    plt.savefig(os.path.join(output_img_dir, 'top_genres.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved top_genres.png")

    # 6. Ratings Distribution
    ratings_order = df['rating'].value_counts().index
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='rating', order=ratings_order, hue='type', palette=[primary_color, secondary_color])
    plt.title('Distribution of Content Ratings on Netflix', fontsize=14, color='white', weight='bold')
    plt.xlabel('Rating', fontsize=11, color='white')
    plt.ylabel('Count', fontsize=11, color='white')
    plt.legend(facecolor='#181818', edgecolor='none', labelcolor='white')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(output_img_dir, 'ratings_distribution.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved ratings_distribution.png")

    # 7. Movie Duration Analysis
    movies_df = df[df['type'] == 'Movie'].dropna(subset=['duration_minutes'])
    plt.figure(figsize=(10, 6))
    sns.histplot(movies_df['duration_minutes'].astype(float), kde=True, color=primary_color, bins=30)
    plt.title('Distribution of Movie Durations', fontsize=14, color='white', weight='bold')
    plt.xlabel('Duration (Minutes)', fontsize=11, color='white')
    plt.ylabel('Frequency', fontsize=11, color='white')
    plt.savefig(os.path.join(output_img_dir, 'movie_duration_dist.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved movie_duration_dist.png")

    # 8. TV Show Seasons Analysis
    tv_df = df[df['type'] == 'TV Show'].dropna(subset=['duration_seasons'])
    seasons_counts = tv_df['duration_seasons'].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=seasons_counts.index, y=seasons_counts.values, palette='dark:#E50914', hue=seasons_counts.index, legend=False)
    plt.title('Distribution of TV Show Seasons', fontsize=14, color='white', weight='bold')
    plt.xlabel('Number of Seasons', fontsize=11, color='white')
    plt.ylabel('Count', fontsize=11, color='white')
    plt.savefig(os.path.join(output_img_dir, 'tv_seasons_dist.png'), bbox_inches='tight', facecolor='#121212')
    plt.close()
    print("- Saved tv_seasons_dist.png")

    print("EDA Visuals Generation Completed Successfully!")

if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    cleaned_path = os.fspath(base_dir / "data" / "cleaned_netflix.csv")
    img_dir = os.fspath(base_dir / "dashboard_images")
    run_eda(cleaned_path, img_dir)
