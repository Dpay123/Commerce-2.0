from django.test import SimpleTestCase
from django.urls import reverse, resolve
from auctions.views import *

class TestUrls(SimpleTestCase):

    def test_index_url_resolves(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login_view)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, logout_view)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, register)

    def test_create_url_resolves(self):
        url = reverse('create')
        self.assertEquals(resolve(url).func, create)

    def test_listing_url_resolves(self):
        url = reverse('listing', args=[1])
        self.assertEquals(resolve(url).func, listing)

    def test_watchlist_url_resolves(self):
        url = reverse('watchlist')
        self.assertEquals(resolve(url).func, watchlist)

    def test_categories_url_resolves(self):
        url = reverse('categories')
        self.assertEquals(resolve(url).func, categories)

    def test_search_category_url_resolves(self):
        url = reverse('search category', args=['some category'])
        self.assertEquals(resolve(url).func, search_category)