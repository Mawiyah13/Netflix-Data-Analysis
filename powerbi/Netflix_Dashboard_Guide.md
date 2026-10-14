# Power BI Dashboard Implementation Guide

This guide details the step-by-step instructions for constructing the professional, recruiter-ready **Netflix Data Analysis Dashboard** in Power BI Desktop using our cleaned dataset `cleaned_netflix.csv`.

---

## 1. Data Connection & Power Query Steps
1. Open **Power BI Desktop**.
2. Click on **Get Data** -> **Text/CSV** and select [cleaned_netflix.csv](../data/cleaned_netflix.csv).
3. In the preview window, click **Transform Data** to open the **Power Query Editor**.
4. **Create Dimension Tables (Star Schema Optimization)**:
   - To build a highly professional data model (rather than a single flat table), we split the comma-separated multi-value columns:
     - Right-click the `cleaned_netflix` query and select **Reference** (name this new query `Country_Dim`).
     - Select `show_id` and `country` columns, right-click and choose **Remove Other Columns**.
     - Select `country`, click **Split Column** -> **By Delimiter** -> select **Comma**, and click **Advanced Options** -> Split into **Rows**.
     - Trim whitespaces: Select the `country` column, go to **Transform** -> **Format** -> **Trim**.
     - Filter out any "Unknown" values if you wish to analyze producing countries exclusively.
     - Repeat the same referencing process to create `Genre_Dim` (using `listed_in`) and `Cast_Dim` (using `cast`).
5. Click **Close & Apply** to load the data model.

---

## 2. Data Modeling & Relationships
1. Navigate to the **Model View** in Power BI.
2. Arrange your tables in a **Star Schema** layout:
   - Centred Fact Table: `cleaned_netflix` (contains core attributes, runtimes, dates)
   - Dimension Tables: `Country_Dim`, `Genre_Dim`, and `Cast_Dim`
3. Establish relationships:
   - Connect `cleaned_netflix[show_id]` (1) to `Country_Dim[show_id]` (*) (1-to-many, Single cross-filter direction).
   - Connect `cleaned_netflix[show_id]` (1) to `Genre_Dim[show_id]` (*) (1-to-many, Single cross-filter direction).
   - Connect `cleaned_netflix[show_id]` (1) to `Cast_Dim[show_id]` (*) (1-to-many, Single cross-filter direction).

---

## 3. DAX Measures
Create a dedicated table named `_Measures` and write the following DAX calculations:

```dax
-- 1. Total Content Titles on the platform
Total Titles = COUNTROWS(cleaned_netflix)

-- 2. Total Movie Titles
Total Movies = CALCULATE([Total Titles], cleaned_netflix[type] = "Movie")

-- 3. Total TV Show Titles
Total TV Shows = CALCULATE([Total Titles], cleaned_netflix[type] = "TV Show")

-- 4. Movie Percentage
Movie % = DIVIDE([Total Movies], [Total Titles], 0)

-- 5. TV Show Percentage
TV Show % = DIVIDE([Total TV Shows], [Total Titles], 0)

-- 6. Unique Countries represented
Unique Countries Count = DISTINCTCOUNT(Country_Dim[country])
```

---

## 4. UI Design & Layout (Netflix Theme)
To build a stunning, premium interface, we apply a **dark mode Netflix theme**:
- **Page Background**: Dark Charcoal (`#121212`)
- **Card Background**: Semi-transparent Obsidian (`#181818` with 10% transparency, soft rounded corners)
- **Primary Color (Accent)**: Netflix Red (`#E50914`)
- **Secondary Color**: Slate Gray (`#808080`) or Muted Silver (`#D3D3D3`)
- **Font**: Outfit or Inter (Premium Sans-serif)

### 4.1 Card Visuals (KPI Block)
Place 4 card visuals at the top of the dashboard:
1. **Total Titles Card**: Displays `[Total Titles]` measure.
2. **Movies Card**: Displays `[Total Movies]` measure (with a sub-label showing `[Movie %]`).
3. **TV Shows Card**: Displays `[Total TV Shows]` measure (with a sub-label showing `[TV Show %]`).
4. **Countries Card**: Displays `[Unique Countries Count]` measure.

### 4.2 Chart Visuals
1. **Movie vs. TV Show Distribution (Donut Chart)**:
   - Legend: `type`
   - Values: `[Total Titles]`
   - Colors: Netflix Red (`#E50914`) and Slate Gray (`#404040`)
2. **Top 10 Genres (Horizontal Bar Chart)**:
   - Y-Axis: `Genre_Dim[genre]`
   - X-Axis: `[Total Titles]`
   - Sort by: `[Total Titles]` descending. Color: Netflix Red gradient.
3. **Top 10 Countries (Horizontal Bar Chart)**:
   - Y-Axis: `Country_Dim[country]`
   - X-Axis: `[Total Titles]`
   - Color: Netflix Red.
4. **Ratings Distribution (Column Chart)**:
   - X-Axis: `cleaned_netflix[rating]`
   - Y-Axis: `[Total Titles]`
   - Legend: `cleaned_netflix[type]` (stacked or clustered column)
5. **Content Added Trend Over Time (Area Chart)**:
   - X-Axis: `cleaned_netflix[year_added]`
   - Y-Axis: `[Total Titles]`
   - Legend: `cleaned_netflix[type]`
   - Shaded area with smooth interpolation for a premium feel.
6. **Country Production Map (Filled Map / Bubble Map)**:
   - Location: `Country_Dim[country]`
   - Bubble Size: `[Total Titles]`
   - Colors: Red bubbles with dark base map styles (Dark theme map setting).

### 4.3 Interactive Slicers
Arrange these slicers vertically on a collapsible side panel or horizontally along the top filter bar:
1. **Year Slicer**: Slider or list utilizing `cleaned_netflix[year_added]`.
2. **Country Slicer**: Searchable dropdown utilizing `Country_Dim[country]`.
3. **Type Slicer**: Single-select buttons for `cleaned_netflix[type]`.
4. **Rating Slicer**: Multi-select checklist for `cleaned_netflix[rating]`.
