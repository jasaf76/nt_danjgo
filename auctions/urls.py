from django.urls import path

from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('myauctions/', views.my_auctions, name='my_auctions'),
    # Example: /auctions/
    path('', views.auctions, name='auctions'),
    # Example: /auctions/5/
    path('<int:auction_id>/', views.detail, name='detail'),
    # Example: /auctions/5/results/
    # path('<int:auction_id>/results/', views.results, name='results'),
    # Example: /auctions/5/bid/
    path('<int:auction_id>/bid/', views.bid, name='bid'),
    path('my_bids/', views.my_bids, name="my_bids"),
    path('marketplace/', views.marketplace, name="marketplace"),
    path('collections/', views.collections, name="collections"),
    path('add_collection/', views.add_collection, name="add_collection"),
    path('contact/', views.contact, name="contact"),
    path('creators/', views.creators, name="creators"),
    path('deposit/', views.deposit, name="deposit"),
    path('withdraw/', views.withdraw, name="withdraw"),
    # path('process-payment/', views.process_payment, name='process_payment'),
]
