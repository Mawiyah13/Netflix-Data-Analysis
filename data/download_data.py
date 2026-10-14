import os
import urllib.request

def download_netflix_dataset():
    url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2021/2021-04-20/netflix_titles.csv"
    from pathlib import Path
    output_dir = Path(__file__).resolve().parent
    output_path = output_dir / "netflix_titles.csv"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
        
    print(f"Downloading dataset from {url}...")
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"Dataset successfully downloaded and saved to: {output_path}")
        
        # Verify size
        size_bytes = os.path.getsize(output_path)
        print(f"File size: {size_bytes / (1024 * 1024):.2f} MB")
        
        # Print first few lines to verify structure
        with open(output_path, 'r', encoding='utf-8') as f:
            for i in range(5):
                print(f.readline().strip())
    except Exception as e:
        print(f"Error downloading file: {e}")

if __name__ == "__main__":
    download_netflix_dataset()
