import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json
from collections import Counter
import streamlit as st

# Function to load data
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# -------------------- 1. Distribution of Ratings --------------------
def plot_rating_distribution(reviews_data):
    ratings = [review['rating'] for review in reviews_data]
    rating_counts = Counter(ratings)
    
    all_ratings = range(1, 6)
    rating_counts_fixed = {rating: rating_counts.get(rating, 0) for rating in all_ratings}
    
    x_fixed = list(rating_counts_fixed.keys())
    y_fixed = list(rating_counts_fixed.values())
    
    # Plot distribution
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(x_fixed, y_fixed, color='skyblue', edgecolor='black')
    ax.set_title('Distribution of Ratings (Adjusted)')
    ax.set_xlabel('Ratings')
    ax.set_ylabel('Count')
    ax.set_xticks(x_fixed)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

# -------------------- 3. Feedback Reactions Analysis --------------------
def plot_feedback_reactions(reviews_data):
    feedback_data = {'Helpful': 0, 'Cool': 0, 'Funny': 0}
    
    for review in reviews_data:
        feedback_data['Helpful'] += review['feedback']['usefulCount']
        feedback_data['Cool'] += review['feedback']['coolCount']
        feedback_data['Funny'] += review['feedback']['funnyCount']
    
    # Plot reactions
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(feedback_data.keys(), feedback_data.values(), color=['green', 'orange', 'red'], edgecolor='black')
    ax.set_title('Feedback Reactions Analysis')
    ax.set_xlabel('Reaction Type')
    ax.set_ylabel('Count')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

# -------------------- 7. Common Themes in Review Text --------------------
def plot_wordclouds(reviews_data, display_positive=True):
    positive_reviews = [review['text']['full'] for review in reviews_data if review['rating'] >= 4]
    negative_reviews = [review['text']['full'] for review in reviews_data if review['rating'] <= 3]
    
    # Generate word cloud for the selected category
    if display_positive:
        combined_text = " ".join(positive_reviews)
        wordcloud_title = "Positive Reviews"
    else:
        combined_text = " ".join(negative_reviews)
        wordcloud_title = "Negative Reviews"

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)

    # Display the Word Cloud
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)