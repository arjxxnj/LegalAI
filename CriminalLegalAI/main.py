from app import app
import nltk

# Ensure NLTK data is downloaded at startup
def download_nltk_dependencies():
    print("Checking NLTK dependencies...")
    dependencies = ['punkt', 'stopwords', 'wordnet']
    for dependency in dependencies:
        try:
            nltk.data.find(f'{"corpora" if dependency != "punkt" else "tokenizers"}/{dependency}')
            print(f"- {dependency} already downloaded")
        except LookupError:
            print(f"- Downloading {dependency}...")
            nltk.download(dependency)
            print(f"- {dependency} downloaded successfully")

# Download NLTK dependencies before starting
download_nltk_dependencies()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
