from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Gig, GigTier
from .forms import GigForm


# -------------------------------
# Create Gig (Freelancer Only)
# -------------------------------
@login_required
def create_gig(request):
    if request.user.user_type != 'student':
        return redirect('dashboard')

    if request.method == 'POST':
        form = GigForm(request.POST)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.seller = request.user
            gig.save()

            # Create Basic Tier
            GigTier.objects.create(
                gig=gig,
                tier_name='basic',
                price=form.cleaned_data['basic_price'],
                description=form.cleaned_data['basic_description']
            )

            # Create Standard Tier
            GigTier.objects.create(
                gig=gig,
                tier_name='standard',
                price=form.cleaned_data['standard_price'],
                description=form.cleaned_data['standard_description']
            )

            # Create Premium Tier
            GigTier.objects.create(
                gig=gig,
                tier_name='premium',
                price=form.cleaned_data['premium_price'],
                description=form.cleaned_data['premium_description']
            )

            return redirect('gig_detail', pk=gig.id)
    else:
        form = GigForm()

    return render(request, 'gigs/create_gig.html', {'form': form})


# -------------------------------
# Gig List (Public)
# -------------------------------

from django.db.models import Avg, Q
from apps.reviews.models import Review


def gig_list(request):
    gigs = Gig.objects.filter(is_active=True)
    selected_category_id = request.GET.get("category")
    search_query = request.GET.get("q", "").strip()

    if selected_category_id:
        gigs = gigs.filter(
            Q(category_id=selected_category_id) |
            Q(category__parent_id=selected_category_id)
        )

    if search_query:
        gigs = gigs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(category__parent__name__icontains=search_query) |
            Q(seller__username__icontains=search_query)
        )

    gig_data = []

    for gig in gigs:
        reviews = Review.objects.filter(seller=gig.seller)
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        total_reviews = reviews.count()

        lowest_price = gig.tiers.order_by('price').first()

        gig_data.append({
            'gig': gig,
            'average_rating': avg_rating or 0,
            'total_reviews': total_reviews,
            'starting_price': lowest_price.price if lowest_price else 0
        })

    # Featured gigs (top 3 rated)
    featured_gigs = sorted(
        gig_data,
        key=lambda x: x['average_rating'],
        reverse=True
    )[:3]

    return render(request, 'gigs/gig_list.html', {
        'gig_data': gig_data,
        'featured_gigs': featured_gigs,
        'categories': Category.objects.filter(parent__isnull=True).prefetch_related("subcategories"),
        'selected_category_id': selected_category_id,
        'search_query': search_query,
    })
# -------------------------------
# Gig Detail
# -------------------------------

from django.db.models import Avg
from apps.reviews.models import Review


def gig_detail(request, pk):
    gig = get_object_or_404(Gig, pk=pk)
    tiers = gig.tiers.all()

    reviews = Review.objects.filter(seller=gig.seller)

    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    total_reviews = reviews.count()

    return render(request, 'gigs/gig_detail.html', {
        'gig': gig,
        'tiers': tiers,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
    })


# -------------------------------
# Edit Gig (Seller Only)
# -------------------------------
@login_required
def edit_gig(request, pk):
    gig = get_object_or_404(Gig, pk=pk)

    if request.user != gig.seller:
        return redirect('dashboard')

    tiers = gig.tiers.all()

    if request.method == 'POST':
        form = GigForm(request.POST, instance=gig)
        if form.is_valid():
            gig = form.save()

            # Update tiers
            tiers_dict = {tier.tier_name: tier for tier in tiers}

            tiers_dict['basic'].price = form.cleaned_data['basic_price']
            tiers_dict['basic'].description = form.cleaned_data['basic_description']
            tiers_dict['basic'].save()

            tiers_dict['standard'].price = form.cleaned_data['standard_price']
            tiers_dict['standard'].description = form.cleaned_data['standard_description']
            tiers_dict['standard'].save()

            tiers_dict['premium'].price = form.cleaned_data['premium_price']
            tiers_dict['premium'].description = form.cleaned_data['premium_description']
            tiers_dict['premium'].save()

            return redirect('gig_detail', pk=gig.id)
    else:
        # Pre-fill tier data
        tiers_dict = {tier.tier_name: tier for tier in tiers}

        initial_data = {
            'basic_price': tiers_dict['basic'].price,
            'basic_description': tiers_dict['basic'].description,
            'standard_price': tiers_dict['standard'].price,
            'standard_description': tiers_dict['standard'].description,
            'premium_price': tiers_dict['premium'].price,
            'premium_description': tiers_dict['premium'].description,
        }

        form = GigForm(instance=gig, initial=initial_data)

    return render(request, 'gigs/edit_gig.html', {'form': form, 'gig': gig})


# -------------------------------
# Delete Gig (Soft Delete)
# -------------------------------
@login_required
def delete_gig(request, pk):
    gig = get_object_or_404(Gig, pk=pk)

    if request.user != gig.seller:
        return redirect('dashboard')

    gig.is_active = False
    gig.save()

    return redirect('dashboard')
