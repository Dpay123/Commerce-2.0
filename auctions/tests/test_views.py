from typing import List
from django.test import TestCase, Client
from django.urls import reverse
from auctions.models import *
from auctions.views import *

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username='user1')
        # assign password to created test user
        self.user1.set_password('pass')
        self.user1.save()
        self.user2 = User.objects.create(username='user2')
        self.listing1 = Listing.objects.create(
            id= 0,
            item='Item 1',
            description='This is a description',
            starting_bid=34.99,
            category= 'Home',
            seller=self.user1
        )
        self.listing_url = reverse('listing', args=['0'])
        self.categories_url = reverse('categories')
        self.watchlist_url = reverse('watchlist')
        self.index_url = reverse('index')
        self.create_url = reverse('create')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.register_url = reverse('register')
        
    def test_check_if_watched(self):
        # set listing1 watched by user1
        Watchlist.objects.create(
            user=self.user1,
            listing=self.listing1
        )
        self.assertTrue(check_if_watched(self.user1, self.listing1))
        self.assertFalse(check_if_watched(self.user2, self.listing1))

    def test_check_if_seller(self):
        self.assertTrue(check_if_seller(self.user1, self.listing1))
        self.assertFalse(check_if_seller(self.user2, self.listing1))

    def test_check_if_winner_valid_bid_closed_auction(self):
        winning_bid = Bid.objects.create(
            bidder=self.user2,
            bid=50.00
        )
        listing2 = Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=winning_bid,
            category= 'Home',
            seller=self.user1,
            closed=True
        )
        # user2 is not seller and is current bidder
        # auction is closed
        self.assertTrue(check_if_winner(self.user2, listing2))
    
    def test_check_if_seller_is_winner(self):
        # user1 is seller, cannot be winner
        winning_bid = Bid.objects.create(
            bidder=self.user1,
            bid=50.00
        )
        listing2 = Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=winning_bid,
            category= 'Home',
            seller=self.user1,
            closed=True
        )
        self.assertFalse(check_if_winner(self.user1, listing2))

    def test_check_if_seller_valid_bid_open_auction(self):
        # cannot be winner if auction is not closed
        winning_bid = Bid.objects.create(
            bidder=self.user2,
            bid=50.00
        )
        listing2 = Listing.objects.create(
            id= 1,
            item='Item 2',
            starting_bid=34.99,
            current_bid=winning_bid,
            category= 'Home',
            seller=self.user1,
            closed=False
        )
        self.assertFalse(check_if_winner(self.user2, listing2))

    def test_listing_GET(self):
        response = self.client.get(self.listing_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')

    # def test_listing_POST

    def test_categories_GET(self):
        # represents a page that shows all categories
        response = self.client.get(self.categories_url)
        self.assertEquals(response.status_code, 200)
        # should return categories page
        self.assertTemplateUsed(response, "auctions/categories.html")
        # should pass a list to template
        self.assertIsInstance(response.context['categories'], list)
        # list should contain all categories
        self.assertEquals(len(response.context['categories']), len(CATEGORY))

    def test_search_category_GET(self):
        # represents a search for items with 'Home' category
        search_category_url = reverse('search category', args=['Home'])
        response = self.client.get(search_category_url)
        self.assertEquals(response.status_code, 200)
        # should return index page
        self.assertTemplateUsed(response, "auctions/index.html")
        # should return queryset with all Listings in 'Home' category
        self.assertQuerysetEqual(response.context['listings'], Listing.objects.filter(category='Home'))

    def test_watchlist_GET(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # add test item to watchlist
        Watchlist.objects.create(
            user=self.user1,
            listing=self.listing1
        )
        response = self.client.get(self.watchlist_url)
        self.assertEquals(response.status_code, 200)
        # should return watchlist page
        self.assertTemplateUsed(response, "auctions/watchlist.html")
        # should return a queryset of all items in user watchlist
        self.assertQuerysetEqual(response.context['watchlist'], Watchlist.objects.filter(user=self.user1))

    def test_index_GET(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)
        # should return index page
        self.assertTemplateUsed(response, 'auctions/index.html')
        # should return queryset with all Listings in db
        self.assertQuerysetEqual(response.context['listings'], Listing.objects.all())

    def test_create_GET(self):
        # log in user
        self.client.login(username='user1', password='pass')
        response = self.client.get(self.create_url)
        self.assertEquals(response.status_code, 200)
        # should return create page
        self.assertTemplateUsed(response, 'auctions/create.html')
        # should pass the NewListingForm as context
        self.assertIsInstance(response.context['form'], NewListingForm)

    # def test_create_POST

    def test_login_view_GET(self):
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")

    # def test_login_view_POST

    def test_logout_view_GET(self):
        # log in user
        self.client.login(username='user1', password='pass')
        response = self.client.get(self.logout_url)
        # default redirect status code is 302
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_register_GET(self):
        response = self.client.get(self.register_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/register.html")

    # def test_register_POST