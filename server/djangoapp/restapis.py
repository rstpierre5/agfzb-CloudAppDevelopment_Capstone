import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, apikey="", **kwargs):

    print("GET from {} ".format(url))
    response = {}
    try:
        if apikey:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)

    except Exception as e:
        print('Network exception occurred: '+ str(e))

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs): 
    print("POST from {} ".format(url))
    response = {}
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except Exception as e:
        print('Network exception occurred: '+ str(e))
    status_code = response.status_code
    print("With status {} ".format(status_code))
    return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], state=dealer["state"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   st=dealer["st"], zip=dealer["zip"], short_name=dealer["short_name"], 
                                   full_name=dealer["full_name"])
            results.append(dealer_obj)

    return results


def get_dealer_by_state_from_cf(url, state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, state=state)
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], state=dealer["state"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   st=dealer["st"], zip=dealer["zip"], short_name=dealer["short_name"],
                                   full_name=dealer["full_name"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer state from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # For each dealer object
        for review in json_result:
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"],
                                   review=review["review"])
            if("purchase_date" in review.keys()):
                review_obj.purchase_date=review["purchase_date"]
            if("car_make" in review.keys()):
                review_obj.car_make=review["car_make"]
            if("car_model" in review.keys()):
                review_obj.car_model=review["car_model"]
            if("car_year" in review.keys()):
                review_obj.car_year=review["car_year"]
            if("id" in review.keys()):
                review_obj.id=review["id"]
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)

            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text, **kwargs):
    url = "https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/4784cb96-e084-4ff0-8e5b-1414f145494f" 

    api_key = "eW7ckV5zzs_Vc7LjsTBBRRXbvA0NZhuuCseGKASUGQnQ" 

    authenticator = IAMAuthenticator(api_key) 

    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2022-04-07',authenticator=authenticator) 

    natural_language_understanding.set_service_url(url) 

    response = natural_language_understanding.analyze( text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result() 

    label=json.dumps(response, indent=2) 

    label = response['sentiment']['document']['label'] 

    return(label) 




