from django.contrib import admin
from .models import Auction, Collection, UserProfile, Withdrawal, Contact, Bid


class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'method', 'address', 'email', 'status')


class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'email', 'phone', 'message', 'user_id')
    list_filter = ('id', 'subject', 'email', 'user_id', 'message')
    list_display_links = ('id', 'subject')
    search_fields = ('subject', 'email', 'phone', 'message', 'user_id')
    list_per_page = 25


admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Collection)
admin.site.register(UserProfile)
admin.site.register(Withdrawal, WithdrawalAdmin)
admin.site.register(Contact, ContactAdmin)
