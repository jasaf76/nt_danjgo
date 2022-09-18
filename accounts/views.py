from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from auctions.models import UserProfile
from accounts.forms import UserProfileForm
from auctions.models import Auction, Collection


def register(request):
    if request.method == 'POST':
        # Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if passwords match
        if password == password2:
            # Check username
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('register')
                else:
                    # Looks good
                    user = User.objects.create_user(username=username, password=password, email=email,
                                                    first_name=first_name, last_name=last_name)
                    # Login after register
                    # auth.login(request, user)
                    # messages.success(request, 'You are now logged in')
                    # return redirect('index')
                    user.save()
                    messages.success(request, 'You are now registered and can log in')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')


@login_required(login_url='login')
def dashboard(request):
    auctions = Auction.objects.order_by('-date_added').filter(author_id=request.user.id)
    collections = Collection.objects.order_by('-date_added').filter(author_id=request.user.id)

    context = {
        'auctions': auctions,
        'collections': collections
    }
    return render(request, 'accounts/dashboard.html', context)


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('/')


#@login_required(login_url='/login/')
def profile(request):
    # get the current user
    current_user = User.objects.get(id=request.user.id)

    # get the current user profile
    current_user_profile = UserProfile.objects.get(user=current_user)

    # all the form stuff
    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST)
        if user_profile_form.is_valid():
            # save data for current user / user profile
            current_user.first_name = user_profile_form.cleaned_data['first_name']
            current_user.last_name = user_profile_form.cleaned_data['last_name']
            current_user_profile.get_prop_bid_emails = user_profile_form.cleaned_data[
                'get_prop_bid_emails']
            current_user_profile.get_accepted_bid_emails = user_profile_form.cleaned_data[
                'get_accepted_bid_emails']
            current_user.save(update_fields=['first_name', 'last_name'])
            current_user_profile.save(
                update_fields=[
                    'get_prop_bid_emails',
                    'get_accepted_bid_emails'])

            messages.success(request, 'Profile saved successfully.')
            return HttpResponseRedirect("/profile")
    else:
        user_profile_form = UserProfileForm(
            initial={
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'email': current_user.email,
                'get_prop_bid_emails': current_user_profile.get_prop_bid_emails,
                'get_accepted_bid_emails': current_user_profile.get_accepted_bid_emails})

    # total_won_bets = get_total_wins(current_user)
    # total_loss_bets = get_total_losses(current_user)
    # total_tie_bets = get_total_ties(current_user)

    return render(request, 'base_profile.html',
                  """{'user_profile_form': user_profile_form,
                   'total_won_bets': total_won_bets,
                   'total_tie_bets': total_tie_bets,
                   'total_loss_bets': total_loss_bets}""")


