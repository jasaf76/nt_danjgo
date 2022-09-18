from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from datetime import datetime, timezone
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from .models import Auction, Bid, Collection, Withdrawal, Deposit, Contact, UserProfile, UserProfileAudit
from .forms import ImageUploadForm, ImageUploadForm1, ImageUploadForm4, ImageUploadForm2, ImageUploadForm3


# Main page
def index(request):
    collection_list = Collection.objects.all()

    # First get all auctions and resolve them
    auction_list = Auction.objects.all()
    for a in auction_list:
        a.resolve()
    # Get all active auctions, oldest first
    latest_auction_list = auction_list.filter(is_active=True).order_by('date_added')
    template = loader.get_template('auctions/index.html')
    context = {
        'auction_list': latest_auction_list,
        'collection_list': collection_list,
    }
    return HttpResponse(template.render(context, request))


def auctions(request):
    # Get all auctions, newest first
    auction_list = Auction.objects.order_by('-date_added')
    for a in auction_list:
        a.resolve()
    template = loader.get_template('auctions/index.html')
    context = {
        'title': "All auctions",
        'auction_list': auction_list,
    }
    return HttpResponse(template.render(context, request))


# Details on some auction
def detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.resolve()
    already_bid = False
    if request.user.is_authenticated:
        if auction.author == request.user:
            own_auction = True
            return render(request, 'auctions/detail.html', {'auction': auction, 'own_auction': own_auction})

        user_bid = Bid.objects.filter(bidder=request.user).filter(auction=auction).first()
        if user_bid:
            already_bid = True
            bid_amount = user_bid.amount
            return render(request, 'auctions/detail.html',
                          {'auction': auction, 'already_bid': already_bid, 'bid_amount': bid_amount})

    return render(request, 'auctions/detail.html', {'auction': auction, 'already_bid': already_bid})
    # try:
    #     auction = Auction.objects.get(pk=auction_id)
    # except Auction.DoesNotExist:
    #     raise Http404("Auction does not exist")
    # return render(request, 'auctions/detail.html', {'auction': auction})


# def results(request, auction_id):
#     response = "You're looking at the results of auction %s."
#     return HttpResponse(response % auction_id)

# Bid on some auction
@login_required(login_url='login')
def bid(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.resolve()
    bid = Bid.objects.filter(bidder=request.user).filter(auction=auction).first()

    if not auction.is_active:
        return render(request, 'auctions/detail.html', {
            'auction': auction,
            'error_message': "The auction has expired.",
        })

    try:
        bid_amount = request.POST['amount']
        # Prevent user from entering an empty or invalid bid
        if not bid_amount or int(bid_amount) < auction.min_value:
            raise (KeyError)
        if not bid:
            # Create new Bid object if it does not exist
            bid = Bid()
            bid.auction = auction
            bid.bidder = request.user
        bid.amount = bid_amount
        bid.date = datetime.now(timezone.utc)
    except (KeyError):
        # Redisplay the auction details.
        return render(request, 'auctions/detail.html', {
            'auction': auction,
            'error_message': "Invalid bid amount.",
        })
    else:
        bid.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        # return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        return render(request, 'auctions/my_bids.html')

        # TODO redirect to my bids
        # template = loader.get_template('auctions/my_bids.html')
        # context = {
        #     'my_bids_list': my_bids_list,
        # }
        # return HttpResponse(template.render(context, request))

        # return HttpResponse(f"You just bid {bid_amount} on auction {auction_id}.")


# Create auction
@login_required(login_url='login')
def create(request):
    submit_button = request.POST.get('submit_button')
    if submit_button:
        try:
            title = request.POST['title']
            min_value = request.POST['min_value']
            if not title or not min_value:
                raise (KeyError)
        except (KeyError):
            # Redisplay the create auction page with an error message.
            return render(request, 'auctions/create.html', {
                'error_message': "Please fill the required fields.",
            })
        else:
            # Create new Bid object
            auction = Auction()
            auction.author = request.user
            auction.title = title
            auction.min_value = min_value
            auction.desc = request.POST['description']
            auction.quantity = request.POST['quantity']
            auction.author_2 = request.POST['author_2']
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data['image']
                auction.image = image
            # auction.date_added = datetime.utcnow()
            auction.date_added = datetime.now(timezone.utc)
            auction.save()
            # return HttpResponseRedirect(reverse('auctions:detail', args=(auction.id,)))
            return HttpResponseRedirect('/')
    else:
        return render(request, 'auctions/create.html')


@login_required(login_url='login')
def my_auctions(request):
    # Get all auctions by user, sorted by date
    my_auctions_list = Auction.objects.all().filter(author=request.user).order_by('-date_added')
    for a in my_auctions_list:
        a.resolve()
    template = loader.get_template('auctions/my_auctions.html')
    context = {
        'my_auctions_list': my_auctions_list,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login')
def my_bids(request):
    # Get all bids by user, sorted by date
    my_bids_list = Bid.objects.all().filter(bidder=request.user)
    for b in my_bids_list:
        b.auction.resolve()

    template = loader.get_template('auctions/my_bids.html')
    context = {
        'my_bids_list': my_bids_list,
    }
    return HttpResponse(template.render(context, request))


def marketplace(request):
    # First get all auctions and resolve them
    auction_list = Auction.objects.all()
    for a in auction_list:
        a.resolve()
    # Get all active auctions, oldest first
    latest_auction_list = auction_list.filter(is_active=True).order_by('date_added')

    context = {
        'auction_list': latest_auction_list,
    }
    return render(request, 'auctions/marketplace.html', context)


def collections(request):
    collection_list = Collection.objects.all()

    context = {
        'collection_list': collection_list,
    }
    return render(request, 'auctions/collections.html', context)


def add_collection(request):
    add_collections = request.POST.get('add_collections')
    if add_collections:
        try:
            title = request.POST['title']
            quantity = request.POST['quantity']
            if not title or not quantity:
                raise (KeyError)
        except (KeyError):
            # Redisplay the create auction page with an error message.
            return render(request, 'auctions/add_collection.html', {
                'error_message': "Please fill the required fields.",
            })
        else:
            # Create new Bid object
            collection = Collection()
            collection.author = request.user
            collection.title = title
            collection.quantity = quantity

            form = ImageUploadForm1(request.POST, request.FILES)
            if form.is_valid():
                image_main = form.cleaned_data['image_main']
                collection.image_main = image_main

            f = ImageUploadForm2(request.POST, request.FILES)
            if f.is_valid():
                image_1 = f.cleaned_data['image_1']
                collection.image_1 = image_1

            fo = ImageUploadForm3(request.POST, request.FILES)
            if fo.is_valid():
                image_2 = fo.cleaned_data['image_2']
                collection.image_2 = image_2

            forn = ImageUploadForm4(request.POST, request.FILES)
            if forn.is_valid():
                image_3 = forn.cleaned_data['image_3']
                collection.image_3 = image_3

            # auction.date_added = datetime.utcnow()
            collection.date_added = datetime.now(timezone.utc)
            collection.save()
            # return HttpResponseRedirect(reverse('auctions:detail', args=(auction.id,)))
            return HttpResponseRedirect(reverse('auctions:add_collection', args=()))
    else:
        return render(request, 'auctions/add_collection.html')


def contact(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        user_id = request.POST['user_id']

        if request.user.is_authenticated:
            user_id = request.user.id

        contact = Contact(subject=subject, email=email, phone=phone, message=message, user_id=user_id)
        contact.save()
    return render(request, 'auctions/contact.html')


def creators(request):
    return render(request, 'auctions/creators.html')


"""
def set_prop_bid(request):
    if request.method == 'GET' and 'id' in request.GET:
        bid_id = request.GET['id']

        # make sure betId is an int
        try:
            int(bid_id)
            is_int = True

        except ValueError:
            is_int = False

            # get the prop bid
            # make sure bid exists
            try:
                prop_bid = Bid.objects.get(id=bid_id)
            except Bid.DoesNotExist:
                prop_bid = None

            # make sure bet exists and won_bet is null
            if prop_bid is None:

                # update winnings for the winner and loser, including the audit table
                # get all accepted bets and loop them
                bider_profile = UserProfile.objects.get(user=prop_bid.user)
                wager = prop_bid.prop_wager
                accepted_bids = Bid.objects.filter(
                    accepted_prop=prop_bet)

                for bid in accepted_bids:
                    # get the proposee's user profile
                    proposee_profile = UserProfile.objects.get(
                        user=bet.accepted_user)

                    # if proposer won, proposee lost
                    if status == 'Win':
                        # update proposer
                        proposer_orig_balance = proposer_profile.current_balance
                        proposer_orig_winnings = proposer_profile.overall_winnings
                        proposer_profile.current_balance += wager
                        proposer_profile.overall_winnings += wager
                        proposer_profile.save()

                        # update audit for proposer
                        proposer_profile_audit = UserProfileAudit(
                            user=prop_bet.user,
                            admin_user=current_admin_user,
                            accepted_bet=bet,
                            original_current_balance=proposer_orig_balance,
                            new_current_balance=proposer_profile.current_balance,
                            original_overall_winnings=proposer_orig_winnings,
                            new_overall_winnings=proposer_profile.overall_winnings)
                        proposer_profile_audit.save()
"""


@login_required(login_url='login')
def deposit(request):
    if request.method == 'POST':
        email = request.POST['email']
        amount = request.POST['amount']
        user_id = request.POST['user_id']

        if request.user.is_authenticated:
            user_id = request.user.id

        deposit = Deposit(amount=amount, email=email, user_id=user_id)
        deposit.save()
    return render(request, 'auctions/deposit.html')


def withdraw(request):
    if request.method == 'POST':
        method = request.POST['method']
        email = request.POST['email']
        amount = request.POST['amount']
        address = request.POST['address']
        user_id = request.POST['user_id']

        if request.user.is_authenticated:
            user_id = request.user.id

        withdraw = Withdrawal(method=method, amount=amount, email=email, user_id=user_id, address=address)
        withdraw.save()
    return render(request, 'auctions/withdraw.html')
