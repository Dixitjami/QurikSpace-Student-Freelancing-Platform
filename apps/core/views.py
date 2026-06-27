from django.shortcuts import render
from django.db.models import Avg
from apps.gigs.models import Category, Gig
from apps.reviews.models import Review


def home(request):
    gigs = Gig.objects.filter(is_active=True)

    gig_data = []

    for gig in gigs:
        reviews = Review.objects.filter(seller=gig.seller)
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

        lowest_price = gig.tiers.order_by('price').first()

        gig_data.append({
            'gig': gig,
            'average_rating': avg_rating or 0,
            'starting_price': lowest_price.price if lowest_price else 0
        })

    # Get Top 3 rated gigs
    featured_gigs = sorted(
        gig_data,
        key=lambda x: x['average_rating'],
        reverse=True
    )[:3]

    return render(request, 'home.html', {
        'featured_gigs': featured_gigs,
        'categories': Category.objects.filter(parent__isnull=True).prefetch_related("subcategories"),
    })
