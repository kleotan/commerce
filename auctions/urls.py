from django.urls import path
from auctions import models
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("lot/<int:post_pk>", views.get_post, name="lot"),
    path("<int:user_id>/watchlist", views.watchlist, name="watchlist"),
    path("category", views.cats, name="cats"),
    path("category/<int:cat_pk>", views.get_category, name="category"),
    path("<int:item_id>/add_watchlist", views.add_Watchlist, name="add_watchlist"),
    path("<int:item_id>/del_watchlist", views.del_Watchlist, name="del_watchlist"),
    path("add_auction", views.add_auction, name="add_auction"),
    path("edit_post/<int:post_pk>", views.edit_post, name="edit_post"),
    path("bet_list", views.bet_list, name="bet_list"),
    path("<int:user_id>/my_auctions", views.my_auctions, name="my_auctions"),
    path("<int:item_id>/closed", views.closed, name="closed")   
  ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)