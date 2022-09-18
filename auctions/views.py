from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError, transaction

from .models import *
from .forms import *

# function that retrieves 3 similarly watched items "Users who watched this also watched __"
def get_shared_watched_items(user, listing):
    # get list of users that aren't current user AND watch this listing
    users_watching_listing = Watchlist.objects.filter(listing=listing).exclude(user=user)
    users = []
    for watched_listing in users_watching_listing:
        users.append(watched_listing.user.id)
    # get distinct list of watchlist items that are watched by these users, excluding this listing
    # limit list of listings to 3 results
    other_watched_listings = Watchlist.objects.filter(user__in=users).exclude(listing=listing).distinct('listing')
    listings = []
    for other_listing in other_watched_listings:
        if len(listings) < 3:
            listings.append(other_listing.listing)
    return listings

def check_if_watched(user, listing):
    return user.watchlist.filter(listing = listing)

def check_if_seller(user, listing):
    return user == listing.seller

def check_if_winner(user, listing):
    try:
        if not check_if_seller(user, listing):
            if listing.closed:
                return listing.get_current_bidder() == user
    except ObjectDoesNotExist:
        pass
    return False

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(auction=listing)
    # if logged in
    if request.user.is_authenticated:
        user = request.user
        watched = check_if_watched(user, listing)
        seller = check_if_seller(user, listing)
        winner = check_if_winner(user, listing)
    # if not logged in, set false (these are used for bid/watch functionality, authenticated users only)
    else:
        watched = False
        seller = False
        winner = False

    # set common context
    context = {
        "listing": listing,
        "comments": comments,
        "bid_form": NewBidForm(),
        "watch_form": NewWatchForm(),
        "comment_form": NewCommentForm(),
        "watched": watched,
        "seller": seller,
        "closed": listing.closed,
        "winner": winner
    }

    # add similar watched items if watched
    if watched:
        similar_watched = get_shared_watched_items(user, listing)
        context["listings"] = similar_watched

    if request.method == "POST" and request.user.is_authenticated:

        # close auction functionality for seller only
        if request.POST.get("button") == "Close" and seller:
            listing.closed = True
            listing.save()

        # watch item functionality
        elif request.POST.get("button") == "Watchlist":
            if not watched:
                # create a watch item
                Watchlist.objects.create(
                    user = user,
                    listing = listing
                )
            else:
                # delete from user watchlist
                user.watchlist.filter(listing=listing).delete()

        # comment functionality
        elif request.POST.get("button") == "comment":
            form = NewCommentForm(request.POST)
            if form.is_valid():
                form.save()

        # bid functionality
        else:
            form = NewBidForm(request.POST)
            if form.is_valid():
                # retrieve bid data
                new_bid_amt = form.cleaned_data['bid']
                # bid checks: bid must be greater than starting and current bid
                if (new_bid_amt > listing.starting_bid):
                    if (new_bid_amt > listing.get_current_bid()):
                        # save bid 
                        new_bid = form.save()
                        # set current bid to the new saved bid
                        listing.current_bid = new_bid
                        listing.save()
                        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
                    else:
                        context["bid_error"] = "Bid must exceed current"
                else:
                    context["bid_error"] = "Bid must exceed starting bid and current bid"

            # handling of invalid form
            else:
                context["bid_error"] = "Bid cannot be negative or exceedingly large"
                
            # return method for all bid errors
            return render(request, "auctions/listing.html", context)
        
        # return method for close, watch, comment functionality
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))


    # if POST but not logged in
    elif request.method == 'POST':
        context["error"] = "You must be logged in"

    # return method for GET request or POST (not logged in)
    return render(request, "auctions/listing.html", context)

def search_category(request, category_id):
    listings = Listing.objects.filter(category = category_id)
    context = {
        "listings": listings
    }
    return render(request, "auctions/index.html", context)

@login_required
def watchlist(request):
    user = request.user
    watched_items = user.watchlist.filter(user_id = user)
    context = {
        "watchlist": watched_items
    }
    return render(request, "auctions/watchlist.html", context)

@login_required
def user_listings(request):
    user = request.user
    user_listings = Listing.objects.filter(seller = user)
    context = {
        "user_listings": user_listings
    }
    return render(request, "auctions/user_listings.html", context)

def index(request):
    listings = Listing.objects.all()
    context = {
        "listings": listings
    }
    return render(request, "auctions/index.html", context)

@login_required
def create(request):
    # post method
    if request.method == 'POST':
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("index")
    # get method
    else:
        form = NewListingForm()
    # streamlined return for both methods
    context = {
        "form": form,
    }
    return render(request, "auctions/create.html", context)

def login_view(request):
    # post method
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    # get method
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    # post method
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        if User.objects.filter(username=username).exists():
            return render(request, "auctions/register.html", {
            "message": "Username already taken."
        })
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    # get method
    else:
        return render(request, "auctions/register.html")
