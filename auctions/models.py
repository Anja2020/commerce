from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(max_digits=8, decimal_places=2)
    current_price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wins", null=True, blank=True)
    active = models.BooleanField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)

class Bid(models.Model):
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="bids")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")


class Comment(models.Model):
    title = models.CharField(max_length=64)
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)


class Watchlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users")
    listing = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="listings")
