from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    # Logout user in the request
    logout(request)
    # Redirect user back to index view
    return render(request, 'djangoapp/user_logout.html', context)

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/1686f636-ea14-43bd-a3c1-b8a570415c60/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id, full_name):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/1686f636-ea14-43bd-a3c1-b8a570415c60/dealership-package/reviews"
        # Get dealers from the URL
        ratings = get_dealer_reviews_from_cf(url, dealer_id)
        context["reviews"] = ratings
        context["dealer"] = full_name
        context["dealer_id"] = dealer_id
        # Concat all dealer's short name
        to_print = ' '.join([rating.review + " sentiment: " + rating.sentiment for rating in ratings])
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id, full_name):
    
    review = {}
    if not request.user.is_authenticated:
        return render(request, 'djangoapp/user_login.html', review)

    
    # Handles POST request
    if request.method == "POST":
        review["review"] = request.POST["content" ]
        review["purchase"] = request.POST["purchasecheck" ]
        review["purchase_date"] = request.POST["purchasedate" ]
        review["name"] = request.user.first_name + request.user.last_name

        car_model = CarModel.objects.get(id=request.POST["car"])
        review["car_make"] = car_model.car_make.Name
        review["car_model"] = car_model.Name
        review["car_year"] = car_model.Year.strftime("%Y")

        review["time"] = datetime.utcnow().isoformat()
        review["dealership"] = dealer_id
        json_payload = {}
        json_payload["review"] = review
        print(json_payload)

        json_result = post_request("https://us-east.functions.appdomain.cloud/api/v1/web/1686f636-ea14-43bd-a3c1-b8a570415c60/dealership-package/reviews",
                                    json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id, full_name=full_name)
    else:
        review["dealer_id"]=dealer_id
        review["full_name"]=full_name
        cars = CarModel.objects.filter(DealerId=dealer_id)
        review["cars"]=cars
        return render(request, 'djangoapp/add_review.html', review)
