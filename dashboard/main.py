import streamlit as st
from scrapper import run  # Import the scraping function
from viz import plot_rating_distribution, plot_feedback_reactions, plot_wordclouds  # Import visualization functions
from sentiment_pred  import plot_sentiment_distribution, predict_sentiment, load_json_as_dict


# -------------------- Page Configuration --------------------
st.set_page_config(page_title="Yelp Reviews Dashboard", layout="wide")  # Set this as the first Streamlit command

# -------------------- Custom CSS for Dark Mode --------------------
def add_custom_css():
    st.markdown(
        """
        <style>
        /* Set background color to black */
        .main {
            background-color: #000000 !important;
        }

        /* Text color and font adjustments for readability */
        h1, h2, h3, h4, h5, h6, p, div, label {
            color: #FFFFFF !important;
        }

        /* Sidebar styling */
        .sidebar-content {
            background-color: #1E1E1E !important;
        }

        /* Change button colors */
        button {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }

        /* Adjust iframe (dashboard embed) styling */
        iframe {
            border: none;
            box-shadow: 0 4px 8px rgba(255, 255, 255, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# -------------------- Streamlit Application --------------------
def main():
    # Apply custom CSS
    add_custom_css()
   


    # Create tabs
    tab1, tab2 = st.tabs(["Dashboard", "Yelp Scraper"])

    # -------------------- Tab 1: Dashboard --------------------
    with tab1:
        st.title("Yelp Reviews Dashboard")
        st.markdown(
            """
            <iframe
              style="background: #F1F5F4;border: none;border-radius: 2px;box-shadow: 0 2px 10px 0 rgba(70, 76, 79, .2);width: 100vw;height: 100vh;"
              src="https://charts.mongodb.com/charts-yelp-adsc-wyaqeey/embed/dashboards?id=b39168bc-15c6-4fd2-a32c-b0b47557540a&theme=light&autoRefresh=true&maxDataAge=3600&showTitleAndDesc=true&scalingWidth=fixed&scalingHeight=fixed">
              </iframe>
            """,
            unsafe_allow_html=True,
        )

    # -------------------- Tab 2: Yelp Scraper --------------------
     # -------------------- Tab 2: Yelp Scraper --------------------
    with tab2:
        st.title("Scrape Yelp Reviews and Visualize")

        api_key = st.text_input("Enter Scrapfly API Key:", type="password")

        # Input box for Yelp URL
        yelp_url = st.text_input("Enter Yelp Business Page URL:", placeholder="https://www.yelp.com/biz/example")
        
        # Button to trigger scraping
        if st.button("Scrape and Analyze"):
            if not yelp_url:
                st.error("Please enter a valid Yelp URL.")
            else:
                try:
                    # Run the scraper to get the review dictionary
                    # review_data=load_json_as_dict('dashboard/reviews.json') ## sample file to test
                    review_data = run(yelp_url,api_key)

                    # Extract review texts for sentiment analysis
                    reviews = [review['text']['full'] for review in review_data]

                    # Predict sentiment
                    sentiment_df = predict_sentiment(reviews)

                    # Create a 2x2 grid
                    col1, col2 = st.columns(2)  # First row with two columns
                    col3, col4 = st.columns(2)  # Second row with two columns

                    # Generate and display visualizations in the grid
                    with col1:
                        st.subheader("1. Distribution of Ratings")
                        plot_rating_distribution(review_data)

                    with col2:
                        st.subheader("2. Feedback Reactions Analysis")
                        plot_feedback_reactions(review_data)

                    with col3:
                        st.subheader("3. Word Cloud: Positive Reviews")
                        plot_wordclouds(review_data, display_positive=True)

                    with col4:
                        st.subheader("4. Word Cloud: Negative Reviews")
                        plot_wordclouds(review_data, display_positive=False)

                    # Sentiment Distribution
                    st.subheader("5. Sentiment Distribution")
                    plot_sentiment_distribution(sentiment_df)

                except Exception as e:
                    st.error(f"An error occurred: {e}")


# Run the application
if __name__ == "__main__":
    main()