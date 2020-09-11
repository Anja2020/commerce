from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auctions/<int:listing_id>", views.details, name="details"),
    path("auctions/<int:listing_id>/bid", views.bid, name="bid"),
    path("auctions/<int:listing_id>/comment", views.comment, name="comment"),
    path("auctions/<int:listing_id>/addToWatchlist", views.addToWatchlist, name="addToWatchlist"),
    path("auctions/<int:listing_id>/removeFromWatchlist", views.removeFromWatchlist, name="removeFromWatchlist"),
    path("auctions/create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("auctions/categories/<str:category>", views.categoryListings, name="categoryListings"),
    path("auctions/<int:listing_id>/close", views.close, name="close")
]
