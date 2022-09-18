from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime, timezone
from math import ceil
from django.db.models.signals import post_save
from django.dispatch import receiver

# Auction duration in minutes
AUCTION_DURATION = 3600


class Auction(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    author_2 = models.CharField(max_length=300, blank=True, null=True, )
    title = models.CharField(max_length=300)
    desc = models.CharField(max_length=2000, blank=True)
    image = models.ImageField(upload_to='auction_images/', blank=True, default='auction_images/default/default.svg')
    min_value = models.IntegerField()
    date_added = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    quantity = models.IntegerField()
    winner = models.ForeignKey(User, on_delete=models.SET("(deleted)"),
                               blank=True,
                               null=True,
                               related_name="auction_winner",
                               related_query_name="auction_winner")
    final_value = models.IntegerField(blank=True, null=True)

    def resolve(self):
        if self.is_active:
            # If expired
            if self.has_expired():
                # Define winner
                highest_bid = Bid.objects.filter(auction=self).order_by('-amount').order_by('date').first()
                if highest_bid:
                    self.winner = highest_bid.bidder
                    self.final_value = highest_bid.amount
                self.is_active = False
                self.save()

    # Helper function that determines if the auction has expired
    def has_expired(self):
        now = datetime.now(timezone.utc)
        expiration = self.date_added + timedelta(minutes=AUCTION_DURATION)
        if now > expiration:
            return True
        else:
            return False

    # Returns the ceiling of remaining_time in minutes
    @property
    def remaining_minutes(self):
        if self.is_active:
            now = datetime.now(timezone.utc)
            expiration = self.date_added + timedelta(minutes=AUCTION_DURATION)
            minutes_remaining = ceil((expiration - now).total_seconds() / 60)
            return (minutes_remaining)
        else:
            return (0)

    def __str__(self):
        return self.title


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    amount = models.IntegerField()
    # is_cancelled = models.BooleanField(default=False)
    date = models.DateTimeField('when the bid was made')


# User Profile table holds some user info specific to this betting app

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_balance = models.IntegerField(
        default=1000,
        help_text='The user\'s current balance. Every time the user settles up, the current balance is reset to zero.')
    overall_earnings = models.IntegerField(
        default=0, help_text='The user\'s overall earnings since joining.')
    get_prop_bids_emails = models.BooleanField(default=True)
    get_accepted_bids_emails = models.BooleanField(default=True)
    last_payment = models.DateTimeField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='photos/profile', null=True, blank=True, default='auction_images/default/default.svg')
    about_me = models.TextField(max_length=1000, blank=True, null=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    messenger = models.CharField(max_length=255, null=True, blank=True)
    whatsapp = models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'

    verbose_name_plural = 'User Profiles'


# hook user profile to user table, so that it's created when a user is created
#

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


# User Profile Audit creates an audit trail each time a user's winnings
# are updated due to an accepted bet being closed.

class UserProfileAudit(models.Model):
    user = models.ForeignKey(User, related_name='user_profile_user', on_delete=models.DO_NOTHING)
    accepted_bid = models.ForeignKey(Bid, on_delete=models.DO_NOTHING)
    original_current_balance = models.IntegerField()
    new_current_balance = models.IntegerField()
    original_overall_winnings = models.IntegerField()
    new_overall_winnings = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile Audit'

    verbose_name_plural = 'User Profile Audits'


class Collection(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    likes = models.CharField(max_length=10, blank=True,
                             default=1346)
    quantity = models.IntegerField()
    date_added = models.DateTimeField()
    image_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    image_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    image_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    image_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)

    def __str__(self):
        return self.title


class Contact(models.Model):
    subject = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    contact_date = models.DateTimeField(default=datetime.now, blank=True)
    user_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.subject


class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    email = models.EmailField()
    deposited_on = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.id, self.user)


class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    method = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    deposited_on = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.id, self.user)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.id, self.email)

    def total_cost(self):
        return sum([ li.cost() for li in self.lineitem_set.all() ] )
