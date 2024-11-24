import json
import base64
import jmespath
from typing import List, Dict
from parsel import Selector
from scrapfly import ScrapflyClient, ScrapeConfig, ScrapeApiResponse

# Initialize the ScrapFly client with your API key
# scrapfly = ScrapflyClient(key="scp-live-466e309755fb4cdcb946c3f472b96c8a")  # Replace with your actual ScrapFly API key
  # Replace with your actual ScrapFly API key

def request_reviews_api(url: str, start_index: int, business_id,scrapfly):
    """Request the GraphQL API for review data using ScrapFly's SDK with your configuration"""
    pagination_data = {
        "version": 1,
        "type": "offset",
        "offset": start_index
    }
    pagination_data_json = json.dumps(pagination_data)
    after = base64.b64encode(pagination_data_json.encode('utf-8')).decode('utf-8')  # Encode the pagination values for the payload

    # Construct the payload as a Python object, not a JSON string
    payload = [
        {
            "operationName": "GetBusinessReviewFeed",
            "variables": {
                "encBizId": business_id,
                "reviewsPerPage": 10,
                "selectedReviewEncId": "",
                "hasSelectedReview": False,
                "sortBy": "DATE_DESC",
                "languageCode": "en",
                "ratings": [5, 4, 3, 2, 1],
                "isSearching": False,
                "after": after,  # Pagination parameter
                "isTranslating": False,
                "translateLanguageCode": "en",
                "reactionsSourceFlow": "businessPageReviewSection",
                "minConfidenceLevel": "HIGH_CONFIDENCE",
                "highlightType": "",
                "highlightIdentifier": "",
                "isHighlighting": False
            },
            "extensions": {
                "operationType": "query",
                # Static value required by the API
                "documentId": "ef51f33d1b0eccc958dddbf6cde15739c48b34637a00ebe316441031d4bf7681"
            }
        }
    ]

    # Include the User-Agent and Referer headers
    headers = {
        'authority': 'www.yelp.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.yelp.com',
        'referer': url,  # Main business page URL
        'x-apollo-operation-name': 'GetBusinessReviewFeed',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                      'Chrome/96.0.4664.110 Safari/537.36',
    }


    # Use ScrapFly's SDK with your configuration
    scrape_config = ScrapeConfig(
        url="https://www.yelp.com/gql/batch",
        method="POST",
        headers=headers,
        data=payload,  # Pass the payload as a Python object
        tags=["player", "project:default"],
        proxy_pool="public_residential_pool",
        country="ca",
        asp=True,
        render_js=False  # Disable JavaScript rendering for API call
    )
    result: ScrapeApiResponse = scrapfly.scrape(scrape_config)
    response_text = result.content

    # # Debugging: Print response status and content if there's an error
    # if result.context["http_status"] != 200:
    #     print(f"Error: Received status code {result.context['http_status']}")
    #     print("Response content:")
    #     print(response_text)
    #     raise Exception(f"Failed to fetch reviews: HTTP {result.context['http_status']}")

    return response_text

def parse_review_data(response_text: str):
    """Parse review data from the JSON response"""
    data = json.loads(response_text)
    reviews = data[0]["data"]["business"]["reviews"]["edges"]
    parsed_reviews = []
    for review in reviews:
        result = jmespath.search(
            """{
            encid: encid,
            text: text.{full: full, language: language},
            rating: rating,
            feedback: feedback.{coolCount: coolCount, funnyCount: funnyCount, usefulCount: usefulCount},
            author: author.{encid: encid, displayName: displayName, displayLocation: displayLocation, reviewCount: reviewCount, friendCount: friendCount, businessPhotoCount: businessPhotoCount},
            business: business.{encid: encid, alias: alias, name: name},
            createdAt: createdAt.utcDateTime,
            businessPhotos: businessPhotos[].{encid: encid, photoUrl: photoUrl.url, caption: caption, helpfulCount: helpfulCount},
            businessVideos: businessVideos,
            availableReactions: availableReactionsContainer.availableReactions[].{displayText: displayText, reactionType: reactionType, count: count}
            }""",
            review["node"]
        )
        parsed_reviews.append(result)
    total_reviews = data[0]["data"]["business"]["reviewCount"]
    return {"reviews": parsed_reviews, "total_reviews": total_reviews}

def scrape_reviews(url: str, max_reviews: int = None, api_key: str=None) -> List[Dict]:

    """Scrape reviews from Yelp using ScrapFly's SDK with your configuration"""
    # First, find the business ID from the business URL
    print("Scraping the business ID from the business page")
    scrapfly = ScrapflyClient(key=api_key)

    scrape_config = ScrapeConfig(
        url=url,
        tags=["player", "project:default"],
        proxy_pool="public_residential_pool",
        country="ca",
        asp=True,
        render_js=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/96.0.4664.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.yelp.com/',
        }
    )
    result: ScrapeApiResponse = scrapfly.scrape(scrape_config)
    selector = Selector(text=result.content)
    business_id = selector.css('meta[name="yelp-biz-id"]::attr(content)').get()

    if not business_id:
        print("Failed to extract business ID. Response content:")
        print(result.content)
        raise ValueError("Failed to extract business ID")

    print("Scraping the first review page")
    first_page_text = request_reviews_api(url=url, business_id=business_id, start_index=1)
    review_data = parse_review_data(first_page_text)
    reviews = review_data["reviews"]
    total_reviews = review_data["total_reviews"]

    # Adjust total reviews if max_reviews is set
    if max_reviews and max_reviews < total_reviews:
        total_reviews = max_reviews

    # Next, scrape the remaining review pages
    pages_to_scrape = (total_reviews - 1) // 10  # Since we already scraped the first page
    print(f"Scraping review pagination, remaining ({pages_to_scrape}) more pages")
    for offset in range(11, total_reviews + 1, 10):
        response_text = request_reviews_api(url=url, business_id=business_id, start_index=offset,scrapfly=scrapfly)
        new_reviews = parse_review_data(response_text)["reviews"]
        reviews.extend(new_reviews)
    print(f"Scraped {len(reviews)} reviews from review pages")
    return reviews

def run(url,api_key):
    # Use the URL from your configuration
    reviews = scrape_reviews(
        url=url,
        max_reviews=28,
        api_key=api_key  # Adjust the number of reviews as needed
    )
    # Save the results to a JSON file
    return reviews
    # with open("reviews.json", "w", encoding="utf-8") as file:
    #     json.dump(reviews, file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run(url = "https://www.yelp.com/biz/zarak-by-afghan-kitchen-vancouver")