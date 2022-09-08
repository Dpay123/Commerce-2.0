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

    def test_create_POST_valid(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # test form data
        response = self.client.post(self.create_url, {
            'item': 'Test Item',
            'starting_bid': 1.00,
            'seller': self.user1.id
        })
        # valid form data should be saved as object
        self.assertTrue(Listing.objects.filter(item='Test Item').exists())
        # valid form data should redirect to index
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_create_POST_invalid(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # test invalid form data
        response = self.client.post(self.create_url, {
            'item': 'Test Item',
            'starting_bid': -1
        })
        # should return to create page
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/create.html")

    def test_listing_POST_not_logged_in(self):
        response = self.client.post(self.listing_url, {})
        # should return to listing page with error message
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/listing.html")
        self.assertEquals(response.context['error'], "You must be logged in")

    def test_listing_POST_close(self):
        # log in user
        self.client.login(username='user1', password='pass')
        # test close auction functionality
        response = self.client.post(self.listing_url, {
            'button': "Close"
        })
        # test listing closed
        self.assertTrue(Listing.objects.get(pk=0).closed)
        # successful close should redirect back to listing page
        self.assertRedirects(response, self.listing_url, status_code=302)
    

    # def test_listing_POST_add_to_watchlist

    # def test_listing_POST_remove_from_watchlist

    # def test_listing_POST_valid_comment

    # def test_listing_POST_invalid_comment

    # def test_listing_POST_valid_bid

    # def test_listing_POST_invalid_bid

    def test_login_view_GET(self):
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")

    def test_login_view_POST_valid_user(self):
        response = self.client.post(self.login_url, {
            'username': self.user1,
            'password': 'pass'
        })
        # check valid login
        self.assertTrue(self.user1.is_authenticated)
        # valid login should redirect to index page
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_login_view_POST_invalid_user(self):
        response = self.client.post(self.login_url, {
            'username': 'invalid',
            'password': 'invalid'
        })
        # invalid login should return the login page
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")
        self.assertEquals(response.context['message'], "Invalid username and/or password.")

    def test_login_view_POST_invalid_password(self):
        response = self.client.post(self.login_url, {
            'username': self.user1,
            'password': 'invalid'
        })
        # invalid login should return the login page
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")
        self.assertEquals(response.context['message'], "Invalid username and/or password.")

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

    def test_register_POST_valid(self):
        response = self.client.post(self.register_url, {
            'username': 'user3',
            'email': 'email@email.com',
            'password': 'pass',
            'confirmation': 'pass'
        })
        user = User.objects.get(username='user3')
        # check valid registration
        self.assertTrue(user.is_active)
        # check valid login
        self.assertTrue(user.is_authenticated)
        # valid login should redirect to index page
        self.assertRedirects(response, self.index_url, status_code=302)

    def test_register_POST_invalid_pass_confirmation(self):
        response = self.client.post(self.register_url, {
            'username': 'user3',
            'email': 'email@email.com',
            'password': 'pass',
            'confirmation': 'not pass'
        })
        # check user was not created
        self.assertEquals(len(User.objects.filter(username='user3')), 0)
        # invalid registration should return register page with error
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/register.html")
        self.assertEquals(response.context['message'], "Passwords must match.")

    def test_register_POST_username_taken(self):
            response = self.client.post(self.register_url, {
                'username': 'user1',
                'email': 'notsaved@email.com',
                'password': 'pass',
                'confirmation': 'pass'
            })
            # username taken = Integrity Error, returns register page with error message
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, "auctions/register.html")
            self.assertEquals(response.context['message'], "Username already taken.")