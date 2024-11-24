import pickle
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import json
import nltk

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Load a JSON file and return its contents as a dictionary
def load_json_as_dict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Preprocessing function
def preprocess_text(text):
    try:
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.lower() not in stop_words]
        return ' '.join(tokens)
    except Exception as e:
        print(f"Error processing text: {e}")
        return text  # Return the original text in case of an error

# Load the saved model and vectorizer
def load_model_and_vectorizer(model_path='../models/logistic_regression_model.pkl', vectorizer_path='../models/tfidf_vectorizer.pkl'):
    try:
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)
        with open(vectorizer_path, 'rb') as vectorizer_file:
            vectorizer = pickle.load(vectorizer_file)
        print("Model and vectorizer loaded successfully!")
        return model, vectorizer
    except Exception as e:
        print(f"Error loading model or vectorizer: {e}")
        raise

# Predict sentiment for a list of reviews
def predict_sentiment(reviews):
    try:
        # Load the model and vectorizer
        model, vectorizer = load_model_and_vectorizer()

        # Preprocess the reviews
        processed_reviews = [preprocess_text(review) for review in reviews]

        # Transform the preprocessed reviews using the loaded vectorizer
        tfidf_matrix = vectorizer.transform(processed_reviews)

        # Predict sentiment
        sentiments = model.predict(tfidf_matrix)

        # Return predictions as a DataFrame
        return pd.DataFrame({
            'Review': reviews,
            'Sentiment': sentiments
        })
    except Exception as e:
        print(f"Error during sentiment prediction: {e}")
        raise

# Plot sentiment distribution
def plot_sentiment_distribution(sentiment_df):
    # Define all sentiment categories
    categories = ['positive', 'neutral', 'negative']

    # Count sentiments and ensure all categories are included
    sentiment_counts = sentiment_df['Sentiment'].value_counts()
    sentiment_counts = sentiment_counts.reindex(categories, fill_value=0)  # Fill missing categories with 0

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(8, 4))  # Reduced figure size
    ax.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'yellow', 'red'], edgecolor='black')
    ax.set_title('Sentiment Distribution')
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Count')
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories)  # Ensure proper labels are displayed

    # Display the plot in Streamlit
    st.pyplot(fig)

# Main execution
if __name__ == '__main__':
    # Load review data
    review_data = load_json_as_dict('dashboard/reviews.json')
    if review_data:
        # Extract review texts for sentiment analysis
        reviews = [review['text']['full'] for review in review_data]

        # Predict sentiment
        sentiment_df = predict_sentiment(reviews)

        # Display the sentiment predictions
        print(sentiment_df)