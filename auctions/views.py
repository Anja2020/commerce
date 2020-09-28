from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from .models import User, AuctionListing, Watchlist, Bid, Comment
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt



class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    description = forms.CharField(
        label="Description", widget=forms.Textarea(attrs={'class': 'form-control'}))
    start_bid = forms.DecimalField(label="Start Bid in $")
    image_url = forms.URLField(label="URL of image", required=False)
    category = forms.CharField(label="Category", required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}))


class NewBidForm(forms.Form):
    bid = forms.DecimalField(label="Bid in $")


class NewCommentForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    text = forms.CharField(label="Comment", widget=forms.Textarea(
        attrs={'class': 'form-control'}))


def index(request):
    listings = AuctionListing.objects.filter(active=True)
    for listing in listings:
        print(listing)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
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
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
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
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def details(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    comment_form, comments, bid_form, num_bids, in_watchlist, message = getInitialDetailsParam(
        request.user, listing)

    return render(request, "auctions/details.html", {
        "listing": listing,
        "user": request.user,
        "comment_form": comment_form,
        "comments": comments,
        "bid_form": bid_form,
        "num_bids": num_bids,
        "in_watchlist": in_watchlist,
        "message": message

    })


def getInitialDetailsParam(user, listing):
    comment_form = NewCommentForm()
    comments = Comment.objects.filter(listing=listing).order_by('-created_at')
    bid_form = NewBidForm()
    num_bids = Bid.objects.filter(listing=listing).count(),
    message = None
    if user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(
            user=user, listing=listing).exists()
    else:
        in_watchlist = None

    return (comment_form, comments, bid_form, num_bids[0], in_watchlist, message)

@csrf_exempt
@login_required
def bid(request, listing_id):

    listing = AuctionListing.objects.get(id=listing_id)

    if request.method == "POST":
        form = NewBidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data['bid']
            if bid >= listing.start_bid and bid > listing.current_price:
                author = request.user

                listing.current_price = bid
                listing.winner = author
                listing.save()

                bid = Bid.objects.create(
                    bid=bid, author=author, listing=listing)
                bid.save()
            else:
                comment_form, comments, _, num_bids, in_watchlist, _ = getInitialDetailsParam(
                    request.user, listing)
                message = "Bid must be higher than the current price!"
                return render(request, "auctions/details.html", {

                    "listing": listing,
                    "user": request.user,
                    "comment_form": comment_form,
                    "comments": comments,
                    "bid_form": form,
                    "num_bids": num_bids,
                    "in_watchlist": in_watchlist,
                    "message": message
                })
    return redirect("details", listing_id)

@csrf_exempt
@login_required
def comment(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            author = request.user

            comment = Comment.objects.create(
                title=title, text=text, author=author, listing=listing)
            comment.save()
        else:
            _, comments, bid_form, num_bids, in_watchlist, message = getInitialDetailsParam(
                request.user, listing)

            return render(request, "auctions/details.html", {
                "listing": listing,
                "user": request.user,
                "comment_form": form,
                "comments": comments,
                "bid_form": bid_form,
                "num_bids": num_bids,
                "in_watchlist": in_watchlist,
                "message": message

            })
    return redirect("details", listing_id)

@csrf_exempt
@login_required
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            start_bid = form.cleaned_data['start_bid']
            current_price = start_bid
            image_url = form.cleaned_data['image_url']
            category = form.cleaned_data['category']
            winner = None
            active = True
            author = request.user

            listing = AuctionListing(title=title, description=description, start_bid=start_bid, current_price=current_price,
                                     image_url=image_url, category=category, winner=winner, active=active, author=author)

            listing.save()

            return redirect("index")

        else:
            return render(request, "auctions/create.html", {
                "form": form
            })

    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })


@csrf_exempt
@login_required
def watchlist(request):
    user_id = request.user.id
    users_watchlist = Watchlist.objects.filter(user=user_id)
    return render(request, "auctions/watchlist.html", {
        "users_watchlist": users_watchlist
    })

@csrf_exempt
@login_required
def addToWatchlist(request, listing_id):
    user = request.user
    listing = AuctionListing.objects.get(id=listing_id)
    watchlist_item = Watchlist.objects.create(user=user, listing=listing)
    watchlist_item.save()
    return redirect("details", listing.id)

@csrf_exempt
@login_required
def removeFromWatchlist(request, listing_id):
    user = request.user
    listing = AuctionListing.objects.get(id=listing_id)
    Watchlist.objects.filter(user=user, listing=listing).delete()
    return redirect("details", listing.id)


def categories(request):
    categories = {
        listing.category for listing in AuctionListing.objects.exclude(category="").filter(active=True)}
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def categoryListings(request, category):
    listings = AuctionListing.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def close(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    listing.active = False
    listing.save()
    return redirect("details", listing.id)
