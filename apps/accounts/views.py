from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        error_message = "Invalid username or password."

    return render(request, 'accounts/login.html', {
        'error_message': error_message
    })


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    if request.user.user_type == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('client_dashboard')
    



from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from apps.accounts.models import CustomUser
from apps.reviews.models import Review
from apps.gigs.models import Gig
from apps.orders.models import Order


def freelancer_profile(request, user_id):
    profile_user = get_object_or_404(
        CustomUser,
        id=user_id,
        user_type='student'
    )

    profile = profile_user.studentprofile

    # Reviews
    reviews = Review.objects.filter(seller=profile_user)
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    total_reviews = reviews.count()

    # Portfolio
    portfolio_projects = profile_user.portfolio_items.all()

    # Gigs
    gigs = Gig.objects.filter(seller=profile_user, is_active=True)
    gigs_count = gigs.count()

    # Completed Orders
    completed_orders = Order.objects.filter(
        seller=profile_user,
        status='completed'
    ).count()

    # Skills list
    skills = [
        skill.strip()
        for skill in profile.skills.split(',')
    ] if profile.skills else []

    return render(request, 'accounts/freelancer_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
        'portfolio_projects': portfolio_projects,
        'gigs': gigs,
        'gigs_count': gigs_count,
        'completed_orders': completed_orders,
        'skills': skills,
    })


from .models import Portfolio
from .forms import PortfolioForm


@login_required
def add_portfolio(request):
    if request.user.user_type != 'student':
        return redirect('dashboard')

    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.freelancer = request.user
            portfolio.save()
            return redirect('freelancer_profile', user_id=request.user.id)
    else:
        form = PortfolioForm()

    return render(request, 'accounts/add_portfolio.html', {'form': form})


from .forms import ClientProfileEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required


@login_required
def edit_profile(request):
    if request.user.user_type != 'student':
        return redirect('dashboard')

    profile = request.user.studentprofile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()

            # Save profile image separately
            if request.FILES.get('profile_image'):
                request.user.profile_image = request.FILES['profile_image']
                request.user.save()

            return redirect('freelancer_profile', user_id=request.user.id)

    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'form': form
    })


@login_required
def client_profile(request, user_id):
    profile_user = get_object_or_404(
        CustomUser,
        id=user_id,
        user_type='client'
    )
    profile = profile_user.clientprofile

    return render(request, 'accounts/client_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
    })


@login_required
def edit_client_profile(request):
    if request.user.user_type != 'client':
        return redirect('dashboard')

    profile = request.user.clientprofile

    if request.method == 'POST':
        form = ClientProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            if request.FILES.get('profile_image'):
                request.user.profile_image = request.FILES['profile_image']
                request.user.save()

            return redirect('client_profile', user_id=request.user.id)
    else:
        form = ClientProfileEditForm(instance=profile)

    return render(request, 'accounts/edit_client_profile.html', {
        'form': form
    })
