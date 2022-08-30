from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass

CATEGORY = {
    ("Home", "Home"),
    ("Electronics", "Electronics"),
    ("Toys", "Toys"),
    ("Fashion", "Fashion"),
    ("Other", "Other")
}

# one to many: 1 user can have many listings
class Listing(models.Model):
    item = models.CharField(null=True, max_length=200)
    description = models.TextField(null=True, blank=True, max_length=500)
    starting_bid = models.FloatField()
    current_bid = models.FloatField(null=True, blank=True)
    category = models.CharField(null=True, blank=True, max_length=64, choices=CATEGORY)
    img_url = models.URLField(blank=True)
    img = models.ImageField(upload_to='', default='default_img.png')
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    closed = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"{self.item}"

# one to one: 1 listing can only have one set of bids
class Bid(models.Model):
    bidder = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    bidding_on = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE)
    bid = models.FloatField()

    def __str__(self):
        return f"{self.bidding_on} - {self.bid} - {self.bidder}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="listings")

# one to many: 1 listing can have many comments
class Comment(models.Model):
    auction = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="get_comments")
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    comment = models.TextField(null=True, max_length=500)
