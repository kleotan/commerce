from django.test import Client, TestCase
from .models import *
from django.db.models import Max

# Create your tests here.
class AuctionsTestCase(TestCase):

    def setUp(self):
        user1=User.objects.create(username='wow', password='12345')
        user2=User.objects.create(username='ben', password='23456')
        lot1=ActiveListings.objects.create(lot_name='new item1', lot_description='description', lot_author=user1, price=505, start_bet=550, is_closed=False)
        lot2=ActiveListings.objects.create(lot_name='new item2', lot_description='description2', lot_author=user1, price=250, is_closed=False)
        
        Bet.objects.create(bet_item=lot1, bet_price=550, last_bet_user=user2)
        Bet.objects.create(bet_item=lot1, bet_price=450, last_bet_user=user2)
        Bet.objects.create(bet_item=lot1, bet_price=550, last_bet_user=user1)
    
    def test_lots_count(self):
        lots = ActiveListings.objects.all()
        self.assertEqual(lots.count(), 2)


    def test_equal_prices(self):
        item=ActiveListings.objects.get(pk=1)
        u=User.objects.get(pk=2)
        b=Bet.objects.get(bet_item=item, bet_price=550, last_bet_user=u)
        self.assertTrue(item.equal_fields(1))

    
    def test_bet_price(self):
        item=ActiveListings.objects.get(pk=1)
        u=User.objects.get(pk=2)
        b=Bet.objects.get(bet_item=item, bet_price=550, last_bet_user=u)
        self.assertTrue(b.is_valid_price(1))


    def test_bet_price_invalid(self):
        item=ActiveListings.objects.get(pk=1)
        u=User.objects.get(pk=2)
        b=Bet.objects.get(bet_item=item, bet_price=450, last_bet_user=u)
        self.assertFalse(b.is_valid_price(1))

    
    def test_index(self):
          # Налаштувати client для надсилання запитів
        c = Client()
        # надіслати запит до index та отримати відповідь
        response=c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['goods'].count(), 2)
    
    def test_valid_lot_page(self):
        item=ActiveListings.objects.get(lot_name='new item1')

        c=Client()
        response=c.get(f"/lot/{item.id}")
        self.assertEqual(response.status_code, 200)

    
    def test_invalid_lot_page(self):
        max_id=ActiveListings.objects.all().aggregate(Max("id"))["id__max"]
        
        c=Client()
        response=c.get(f"/lot/{max_id+1}")
        self.assertEqual(response.status_code, 404)