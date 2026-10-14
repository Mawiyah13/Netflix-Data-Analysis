import json
import os

def create_data_cleaning_notebook(target_path):
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Netflix Data Cleaning & Preprocessing\n",
                    "**Role**: Senior Data Engineer / Senior Data Analyst  \n",
                    "**Project**: End-to-End Netflix Data Analysis  \n",
                    "\n",
                    "This notebook performs professional-grade data cleaning on the raw Netflix dataset (`netflix_titles.csv`). \n",
                    "We will handle missing values, duplicates, standardise text, parse dates, convert durations into numeric features, and prepare the dataset for SQL database ingestion and Power BI reporting."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "\n",
                    "print(\"Libraries successfully imported!\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Load the Raw Data"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "raw_data_path = '../data/netflix_titles.csv'\n",
                    "df = pd.read_csv(raw_data_path)\n",
                    "\n",
                    "# Display first 5 rows\n",
                    "df.head()"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Dataset Info and Null summary\n",
                    "print(df.info())\n",
                    "print(\"\\nMissing values count per column:\")\n",
                    "print(df.isnull().sum())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Data Cleaning Tasks\n",
                    "We will address the following:\n",
                    "- Trim whitespaces from string columns.\n",
                    "- Clean missing values in `director`, `cast`, `country`, `rating`, and `date_added`.\n",
                    "- Check for and drop duplicate rows.\n",
                    "- Standardize categorical fields.\n",
                    "- Parse `date_added` and extract `year_added`, `month_added`, and `day_added`.\n",
                    "- Parse `duration` into numeric format (minutes for Movies, seasons for TV Shows)."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2.1 Trim Whitespace & Handle Missing Values"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Trim whitespaces from string columns\n",
                    "string_cols = df.select_dtypes(include=['object']).columns\n",
                    "for col in string_cols:\n",
                    "    df[col] = df[col].astype(str).str.strip()\n",
                    "\n",
                    "# Handle text missing values\n",
                    "df['director'] = df['director'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')\n",
                    "df['cast'] = df['cast'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')\n",
                    "df['country'] = df['country'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')\n",
                    "df['rating'] = df['rating'].replace({'nan': 'Unknown', '': 'Unknown'}).fillna('Unknown')\n",
                    "\n",
                    "# Drop rows with missing date_added since they are very few (< 10 rows)\n",
                    "df = df[df['date_added'] != 'nan']\n",
                    "df = df.dropna(subset=['date_added'])\n",
                    "\n",
                    "print(\"Remaining missing values:\")\n",
                    "print(df.isnull().sum())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2.2 Standardise Type Column"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Standardize categories to 'Movie' and 'TV Show'\n",
                    "type_lower = df['type'].str.lower().str.strip()\n",
                    "df['type'] = type_lower.map({'movie': 'Movie', 'tv show': 'TV Show', 'tv-show': 'TV Show'}).fillna('Unknown')\n",
                    "print(\"Content types after standardization:\", df['type'].unique())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2.3 Date Parsing and Feature Engineering"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Convert date_added to datetime format\n",
                    "df['date_added_dt'] = pd.to_datetime(df['date_added'], errors='coerce', format='%B %d, %Y')\n",
                    "\n",
                    "# For dates that did not match format, use fallback parser\n",
                    "if df['date_added_dt'].isnull().sum() > 0:\n",
                    "    df.loc[df['date_added_dt'].isnull(), 'date_added_dt'] = pd.to_datetime(df['date_added'], errors='coerce')\n",
                    "\n",
                    "# Drop any remaining unparseable dates\n",
                    "df = df.dropna(subset=['date_added_dt'])\n",
                    "\n",
                    "# Extract new date-based features\n",
                    "df['year_added'] = df['date_added_dt'].dt.year.astype(int)\n",
                    "df['month_added'] = df['date_added_dt'].dt.strftime('%B')\n",
                    "df['day_added'] = df['date_added_dt'].dt.day.astype(int)\n",
                    "\n",
                    "# Convert date_added to MySQL DATE format: YYYY-MM-DD\n",
                    "df['date_added'] = df['date_added_dt'].dt.strftime('%Y-%m-%d')\n",
                    "\n",
                    "# Remove temporary column\n",
                    "df = df.drop(columns=['date_added_dt'])\n",
                    "print(\"Date added columns engineered:\")\n",
                    "df[['date_added', 'year_added', 'month_added', 'day_added']].head()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2.4 Parse Duration Column\n",
                    "Movies have durations in 'min' (minutes) and TV Shows in 'Season(s)'. We will parse these and split them into distinct numeric fields: `duration_minutes` and `duration_seasons`."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "df['duration_minutes'] = np.nan\n",
                    "df['duration_seasons'] = np.nan\n",
                    "\n",
                    "for idx, row in df.iterrows():\n",
                    "    duration_val = str(row['duration']).lower()\n",
                    "    if 'min' in duration_val:\n",
                    "        minutes = int(''.join(filter(str.isdigit, duration_val)))\n",
                    "        df.at[idx, 'duration_minutes'] = minutes\n",
                    "    elif 'season' in duration_val:\n",
                    "        seasons = int(''.join(filter(str.isdigit, duration_val)))\n",
                    "        df.at[idx, 'duration_seasons'] = seasons\n",
                    "\n",
                    "# Cast numeric columns to Pandas nullable Int64\n",
                    "df['duration_minutes'] = df['duration_minutes'].astype('Int64')\n",
                    "df['duration_seasons'] = df['duration_seasons'].astype('Int64')\n",
                    "\n",
                    "print(\"Duration columns after parsing:\")\n",
                    "df[['type', 'duration', 'duration_minutes', 'duration_seasons']].sample(5)"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2.5 Remove Duplicates & Verify Final Cleaned Data"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Identify and drop duplicate records\n",
                    "initial_rows = df.shape[0]\n",
                    "df = df.drop_duplicates()\n",
                    "print(f\"Dropped {initial_rows - df.shape[0]} duplicates.\")\n",
                    "\n",
                    "# Clean up order by sorting show_id numerically\n",
                    "df['id_num'] = df['show_id'].str.extract(r'(\\d+)').astype(int)\n",
                    "df = df.sort_values(by='id_num').drop(columns=['id_num']).reset_index(drop=True)\n",
                    "\n",
                    "print(f\"Final clean data shape: {df.shape}\")\n",
                    "df.head()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Export Cleaned Dataset"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "output_path = '../data/cleaned_netflix.csv'\n",
                    "df.to_csv(output_path, index=False)\n",
                    "print(f\"Successfully saved clean dataset to: {output_path}\")\n",
                    "\n",
                    "# Save normalized tables for relational SQL database ingestion\n",
                    "output_dir = '../data'\n",
                    "titles_cols = [\n",
                    "    'show_id', 'type', 'title', 'date_added', 'release_year', 'rating',\n",
                    "    'duration', 'duration_minutes', 'duration_seasons', 'description',\n",
                    "    'year_added', 'month_added', 'day_added'\n",
                    "]\n",
                    "titles_df = df.drop(columns=['director', 'cast', 'country', 'listed_in'])[titles_cols]\n",
                    "titles_df.to_csv(os.path.join(output_dir, 'normalized_titles.csv'), index=False)\n",
                    "\n",
                    "def split_and_explode(dataframe, column_name, target_col_name):\n",
                    "    split_df = dataframe[['show_id', column_name]].copy()\n",
                    "    split_df[column_name] = split_df[column_name].astype(str).str.split(',')\n",
                    "    exploded = split_df.explode(column_name)\n",
                    "    exploded[column_name] = exploded[column_name].str.replace('\"', '', regex=False)\n",
                    "    exploded = exploded[exploded[column_name].notna() & (exploded[column_name] != '') & (exploded[column_name] != 'Unknown')]\n",
                    "    return exploded.rename(columns={column_name: target_col_name}).drop_duplicates()\n",
                    "\n",
                    "split_and_explode(df, 'director', 'director').to_csv(os.path.join(output_dir, 'normalized_directors.csv'), index=False)\n",
                    "split_and_explode(df, 'cast', 'actor').to_csv(os.path.join(output_dir, 'normalized_cast.csv'), index=False)\n",
                    "split_and_explode(df, 'country', 'country').to_csv(os.path.join(output_dir, 'normalized_countries.csv'), index=False)\n",
                    "split_and_explode(df, 'listed_in', 'genre').to_csv(os.path.join(output_dir, 'normalized_genres.csv'), index=False)\n",
                    "print(\"Normalized dimension tables successfully exported for SQL!\")"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    print(f"Created notebook {target_path}")

def create_eda_notebook(target_path):
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Netflix Exploratory Data Analysis (EDA)\n",
                    "**Role**: Senior Data Analyst / BI Developer  \n",
                    "**Project**: End-to-End Netflix Data Analysis  \n",
                    "\n",
                    "This notebook explores the cleaned Netflix dataset (`cleaned_netflix.csv`) to uncover critical business insights and generate publication-quality visualizations for the portfolio. \n",
                    "Insights include content growth patterns, geographical distribution of content, top genres, directors, rating analysis, and oldest/newest titles."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "\n",
                    "# Set aesthetic styling (Dark/Premium theme matching Netflix color palette)\n",
                    "sns.set_theme(style=\"darkgrid\")\n",
                    "plt.rcParams['figure.figsize'] = (12, 6)\n",
                    "plt.rcParams['figure.dpi'] = 150\n",
                    "plt.rcParams['axes.facecolor'] = '#181818'\n",
                    "plt.rcParams['figure.facecolor'] = '#121212'\n",
                    "plt.rcParams['text.color'] = '#E5E5E5'\n",
                    "plt.rcParams['axes.labelcolor'] = '#E5E5E5'\n",
                    "plt.rcParams['xtick.color'] = '#E5E5E5'\n",
                    "plt.rcParams['ytick.color'] = '#E5E5E5'\n",
                    "\n",
                    "netflix_colors = ['#E50914', '#221F1F', '#F5F5F1']\n",
                    "print(\"EDA environment initialized successfully!\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Load the Cleaned Data"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "df = pd.read_csv('../data/cleaned_netflix.csv')\n",
                    "df.head()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Key Metrics Summary"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "total_titles = df.shape[0]\n",
                    "movie_count = df[df['type'] == 'Movie'].shape[0]\n",
                    "tv_show_count = df[df['type'] == 'TV Show'].shape[0]\n",
                    "unique_countries = df['country'].nunique()\n",
                    "\n",
                    "print(f\"=== NETFLIX KEY METRICS ===\")\n",
                    "print(f\"Total Content Titles: {total_titles}\")\n",
                    "print(f\"Total Movies: {movie_count} ({movie_count/total_titles*100:.1f}%)\")\n",
                    "print(f\"Total TV Shows: {tv_show_count} ({tv_show_count/total_titles*100:.1f}%)\")\n",
                    "print(f\"Unique Production Countries: {unique_countries}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Visual Analysis"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.1 Content Types Breakdown (Movie vs. TV Show)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "type_counts = df['type'].value_counts()\n",
                    "plt.figure(figsize=(6, 6))\n",
                    "plt.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', colors=['#E50914', '#564d4d'], \n",
                    "        textprops={'fontsize': 14, 'color': 'white'}, startangle=90, explode=[0, 0.05])\n",
                    "plt.title('Netflix Content Types: Movies vs TV Shows', fontsize=16, color='white', weight='bold')\n",
                    "\n",
                    "os.makedirs('../dashboard_images', exist_ok=True)\n",
                    "plt.savefig('../dashboard_images/content_type_ratio.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.2 Content Growth over Years (Cumulative)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "growth_df = df.groupby(['year_added', 'type']).size().unstack(fill_value=0).cumsum()\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "plt.plot(growth_df.index, growth_df['Movie'], color='#E50914', label='Movies', linewidth=3.5)\n",
                    "plt.plot(growth_df.index, growth_df['TV Show'], color='#B3B3B3', label='TV Shows', linewidth=3.5, linestyle='--')\n",
                    "plt.title('Netflix Content Growth Trajectory (Cumulative)', fontsize=16, color='white', weight='bold')\n",
                    "plt.xlabel('Year Added', fontsize=12, color='white')\n",
                    "plt.ylabel('Cumulative Number of Titles', fontsize=12, color='white')\n",
                    "plt.legend(facecolor='#181818', edgecolor='none', labelcolor='white')\n",
                    "plt.grid(color='#333333', linestyle=':')\n",
                    "plt.savefig('../dashboard_images/content_growth.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.3 Top 10 Countries Producing Content"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Countries can be multi-valued (e.g. \"United States, India\"). We explode them to get a clean count\n",
                    "countries_series = df['country'].str.split(', ').dropna().explode()\n",
                    "countries_series = countries_series[countries_series != 'Unknown']\n",
                    "top_countries = countries_series.value_counts().head(10)\n",
                    "\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "sns.barplot(x=top_countries.values, y=top_countries.index, palette='Reds_r')\n",
                    "plt.title('Top 10 Countries Producing Netflix Content', fontsize=16, color='white', weight='bold')\n",
                    "plt.xlabel('Number of Titles', fontsize=12, color='white')\n",
                    "plt.ylabel('Country', fontsize=12, color='white')\n",
                    "plt.savefig('../dashboard_images/top_countries.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.4 Top 10 Directors"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "directors_series = df['director'].str.split(', ').dropna().explode()\n",
                    "directors_series = directors_series[directors_series != 'Unknown']\n",
                    "top_directors = directors_series.value_counts().head(10)\n",
                    "\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "sns.barplot(x=top_directors.values, y=top_directors.index, palette='Reds_r')\n",
                    "plt.title('Top 10 Most Frequent Directors on Netflix', fontsize=16, color='white', weight='bold')\n",
                    "plt.xlabel('Number of Titles Directed', fontsize=12, color='white')\n",
                    "plt.ylabel('Director', fontsize=12, color='white')\n",
                    "plt.savefig('../dashboard_images/top_directors.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.5 Top 10 Genres (listed_in)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "genres_series = df['listed_in'].str.split(', ').dropna().explode()\n",
                    "top_genres = genres_series.value_counts().head(10)\n",
                    "\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "sns.barplot(x=top_genres.values, y=top_genres.index, palette='Reds_r')\n",
                    "plt.title('Top 10 Netflix Content Genres', fontsize=16, color='white', weight='bold')\n",
                    "plt.xlabel('Number of Titles', fontsize=12, color='white')\n",
                    "plt.ylabel('Genre', fontsize=12, color='white')\n",
                    "plt.savefig('../dashboard_images/top_genres.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.6 Ratings Distribution"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "ratings_order = df['rating'].value_counts().index\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "sns.countplot(data=df, x='rating', order=ratings_order, hue='type', palette=['#E50914', '#564d4d'])\n",
                    "plt.title('Distribution of Content Ratings on Netflix', fontsize=16, color='white', weight='bold')\n",
                    "plt.xlabel('Rating', fontsize=12, color='white')\n",
                    "plt.ylabel('Count', fontsize=12, color='white')\n",
                    "plt.legend(facecolor='#181818', edgecolor='none', labelcolor='white')\n",
                    "plt.xticks(rotation=45)\n",
                    "plt.savefig('../dashboard_images/ratings_distribution.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.7 Movie Duration Analysis"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "movies_df = df[df['type'] == 'Movie'].dropna(subset=['duration_minutes'])\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "sns.histplot(movies_df['duration_minutes'], kde=True, color='#E50914', bins=30)\n",
                    "plt.title('Distribution of Movie Durations', fontsize=16, color='white', weight='bold')\n",
                    "plt.xlabel('Duration (Minutes)', fontsize=12, color='white')\n",
                    "plt.ylabel('Frequency', fontsize=12, color='white')\n",
                    "plt.savefig('../dashboard_images/movie_duration_dist.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.8 TV Show Seasons Analysis"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "tv_df = df[df['type'] == 'TV Show'].dropna(subset=['duration_seasons'])\n",
                    "seasons_counts = tv_df['duration_seasons'].value_counts().sort_index()\n",
                    "\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "sns.barplot(x=seasons_counts.index, y=seasons_counts.values, palette='dark:#E50914', hue=seasons_counts.index, legend=False)\n",
                    "plt.title('Distribution of TV Show Seasons', fontsize=16, color='white', weight='bold')\n",
                    "plt.xlabel('Number of Seasons', fontsize=12, color='white')\n",
                    "plt.ylabel('Count', fontsize=12, color='white')\n",
                    "plt.savefig('../dashboard_images/tv_seasons_dist.png', bbox_inches='tight', facecolor='#121212')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3.9 Oldest & Newest Content"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "print(\"=== OLDEST 5 TITLES ON NETFLIX ===\")\n",
                    "print(df[['title', 'type', 'release_year', 'country']].sort_values(by='release_year').head(5).to_string(index=False))\n",
                    "\n",
                    "print(\"\\n=== NEWEST 5 TITLES ON NETFLIX (BY RELEASE YEAR) ===\")\n",
                    "print(df[['title', 'type', 'release_year', 'country']].sort_values(by='release_year', ascending=False).head(5).to_string(index=False))"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    print(f"Created notebook {target_path}")

if __name__ == "__main__":
    os.makedirs(r"C:\Users\Admin\.gemini\antigravity-ide\scratch\Netflix-Data-Analysis\python", exist_ok=True)
    create_data_cleaning_notebook(r"C:\Users\Admin\.gemini\antigravity-ide\scratch\Netflix-Data-Analysis\python\data_cleaning.ipynb")
    create_eda_notebook(r"C:\Users\Admin\.gemini\antigravity-ide\scratch\Netflix-Data-Analysis\python\eda.ipynb")
