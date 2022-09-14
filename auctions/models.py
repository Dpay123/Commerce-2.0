from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    category = models.CharField(max_length=24, blank=False)

    def __str__(self):
        return self.category

# one to many: 1 user can have many listings
class Listing(models.Model):

    item = models.CharField(max_length=200, blank=False)
    description = models.TextField(null=True, blank=True, max_length=500)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10, null=False, validators=[MinValueValidator(Decimal('0.01'))])
    current_bid = models.ForeignKey('Bid', null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, default=Category.objects.filter(pk=0), null=False, blank=False)
    img = models.ImageField(upload_to='', default='default_img.png', null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.item

    def get_current_bid(self):
        return self.current_bid.bid if self.current_bid else 0

    def get_current_bidder(self):
        return self.current_bid.bidder if self.current_bid else 0

class Bid(models.Model):
    bidder = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='bids')
    bid = models.DecimalField(decimal_places=2, max_digits=10, null=False, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.bid} - {self.bidder}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} is watching {self.listing}"

# one to many: 1 listing can have many comments
class Comment(models.Model):
    auction = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    comment = models.TextField(null=True, max_length=500)

    def __str__(self):
        return f"{self.author} commented on {self.auction}"
