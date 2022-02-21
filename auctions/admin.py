from django.contrib import admin
from .models import *

# Register your models here.

class ActiveListingsAdmin(admin.ModelAdmin):
    list_display=('id', 'lot_name', 'lot_author', 'date_created', 'is_closed')
    list_display_links=('lot_name',)
    search_fields=('lot_name', 'lot_discription')
   

class BetAdmin(admin.ModelAdmin):
    list_display=('last_bet_user', 'bet_item', 'bet_price')
    list_display_links=('last_bet_user',)
    search_fields=('last_bet_user', 'bet_item')
    

admin.site.register(User)
admin.site.register(ActiveListings, ActiveListingsAdmin)
admin.site.register(Bet, BetAdmin)
admin.site.register(Comments)


