from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator

CATEGORY = {
    ("Misc", "Misc"),
    ("Home", "Home"),
    ("Electronics", "Electronics"),
    ("Toys", "Toys"),
    ("Fashion", "Fashion"),
    ("Other", "Other")
}

class User(AbstractUser):
    pass

# one to many: 1 user can have many listings
class Listing(models.Model):

    item = models.CharField(max_length=200, blank=False)
    description = models.TextField(null=True, blank=True, max_length=500)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10, null=False, validators=[MinValueValidator(Decimal('0.01'))])
    current_bid = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.CharField(null=True, blank=True, max_length=64, choices=CATEGORY, default="Misc")
    img = models.ImageField(upload_to='', default='default_img.png', null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.item

# one to one: 1 listing can only have one set of bids
class Bid(models.Model):
    bidder = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    bidding_on = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=10, null=False, validators=[MinValueValidator(Decimal('0.01'))])
    ### can minValueValidator be used in context of bidding_on.current_bid?

    def __str__(self):
        return f"{self.bidding_on} - {self.bid} - {self.bidder}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f"{self.user} is watching {self.listing}"

# one to many: 1 listing can have many comments
class Comment(models.Model):
    auction = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="get_comments")
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    comment = models.TextField(null=True, max_length=500)

    def __str__(self):
        return f"{self.author} commented on {self.auction}"
