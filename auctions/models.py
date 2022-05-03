from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# TODO: Class for Listing, Bids, Comments

# one to many: 1 user can have many listings
class Listing(models.Model):
    CATEGORY = {
        ("Home", "Home"),
        ("Electronics", "Electronics"),
        ("Toys", "Toys"),
        ("Fashion", "Fashion")
    }

    item = models.CharField(null=True, max_length=200)
    description = models.TextField(null=True, blank=True, max_length=500)
    starting_bid = models.IntegerField(null=True)
    current_bid = models.ForeignKey("Bid", on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(null=True, blank=True, max_length=64, choices=CATEGORY)
    img_url = models.URLField(blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.item}"

# one to one: 1 listing can only have one set of bids
class Bid(models.Model):
    bidder = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    bidding_on = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE)
    bid = models.IntegerField()

    def __str__(self):
        return f"${self.bid}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="watched")

    def __str__(self):
        return f"{self.item}"

# one to many: 1 listing can have many comments
class Comment(models.Model):
    comment_on = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    summary = models.CharField(null=True, max_length=100)
    body = models.TextField(null=True, max_length=500)

    def __str__(self):
        return f"{self.summary} - {self.author}"
