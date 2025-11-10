import pymongo
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import datetime

def download_nltk_assets():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK 'stopwords'...")
        nltk.download('stopwords')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK 'wordnet'...")
        nltk.download('wordnet')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK 'punkt'...")
        nltk.download('punkt')
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        print("Downloading NLTK 'punkt_tab'...")
        nltk.download('punkt_tab')

def fetch_reddit_data(mongo_uri="mongodb://localhost:27017/", db_name="socialmedia", collection_name="reddit"):
    print(f"Connecting to MongoDB at {mongo_uri}...")
    try:
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        cursor = collection.find({}, {"title": 1})
        
        df = pd.DataFrame(list(cursor))
        
        if df.empty:
            print(f"No documents found in '{db_name}.{collection_name}'.")
            return pd.DataFrame()
            
        print(f"Successfully fetched {len(df)} documents.")
        client.close()
        return df
    except Exception as e:
        print(f"Error connecting to or fetching from MongoDB: {e}")
        return pd.DataFrame()

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
        
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'www\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    
    tokens = nltk.word_tokenize(text)
    
    clean_tokens = [
        lemmatizer.lemmatize(word) for word in tokens 
        if word not in stop_words and len(word) > 2
    ]
    
    return " ".join(clean_tokens)

def find_trends(data, n_topics=5):
    print("Vectorizing text data with TF-IDF...")
    vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(data)
    
    print(f"Building ML model (LDA) to find {n_topics} trends...")
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        n_jobs=-1,
        learning_method='online'
    )
    lda.fit(tfidf_matrix)
    
    print("Model training complete.")
    return lda, vectorizer

def display_text_trends(model, vectorizer, n_top_words):
    print("\n--- DISCOVERED TRENDS (TEXT) ---")
    feature_names = vectorizer.get_feature_names_out()
    
    for topic_idx, topic in enumerate(model.components_):
        top_word_indices = topic.argsort()[:-n_top_words - 1:-1]
        
        top_words = [feature_names[i] for i in top_word_indices]
        
        print(f"Trend #{topic_idx + 1}: {', '.join(top_words)}")

def plot_matplotlib_trends(model, vectorizer, n_top_words, n_topics):
    print("\nGenerating Matplotlib visualization...")
    feature_names = vectorizer.get_feature_names_out()
    
    fig, axes = plt.subplots(n_topics, 1, figsize=(10, n_topics * 4), sharex=False)
    
    if n_topics == 1:
        axes = [axes]
        
    for topic_idx, (topic, ax) in enumerate(zip(model.components_, axes)):
        top_word_indices = topic.argsort()[:-n_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_word_indices]
        top_weights = [topic[i] for i in top_word_indices]
        
        top_words.reverse()
        top_weights.reverse()
        
        ax.barh(top_words, top_weights, color='skyblue')
        ax.set_title(f"Trend #{topic_idx + 1}", fontdict={'fontsize': 14, 'fontweight': 'bold'})
        ax.set_xlabel("Word Importance (Weight)")
        ax.invert_yaxis()
    
    fig.suptitle("Top Words per Discovered Trend", fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout(pad=3.0)
    print("Displaying plot. Close the plot window to exit the script.")
    plt.show()

if __name__ == "__main__":
    NUM_TRENDS = 5
    NUM_TOP_WORDS = 10
    
    download_nltk_assets()
    
    df = fetch_reddit_data()
    
    if not df.empty:
        print("Preprocessing text data (this may take a moment)...")
        df.dropna(subset=['title'], inplace=True)
        df['clean_text'] = df['title'].apply(preprocess_text)
        
        processed_data = df[df['clean_text'].str.len() > 0]['clean_text']
        
        if len(processed_data) < NUM_TRENDS:
            print(f"Error: Not enough data to analyze. Found only {len(processed_data)} valid documents.")
        else:
            lda_model, tfidf_vectorizer = find_trends(processed_data, n_topics=NUM_TRENDS)
            
            display_text_trends(lda_model, tfidf_vectorizer, n_top_words=NUM_TOP_WORDS)
            
            plot_matplotlib_trends(lda_model, tfidf_vectorizer, n_top_words=NUM_TOP_WORDS, n_topics=NUM_TRENDS)
            
            print("\nAnalysis complete.")
    else:
        print("Exiting script as no data was loaded.")