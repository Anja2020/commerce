from django.contrib import admin

from .models import User, AuctionListing, Bid, Comment, Watchlist

# Register your models here.


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "start_bid")


admin.site.register(User)
admin.site.register(AuctionListing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)
