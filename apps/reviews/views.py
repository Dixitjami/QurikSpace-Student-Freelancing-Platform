from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.orders.models import Order
from .models import Review
from .forms import ReviewForm


@login_required
def create_review(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # Only client can review
    if request.user != order.client:
        return HttpResponseForbidden("Only client can leave review.")

    # Order must be completed
    if order.status != 'completed':
        return redirect('order_detail', pk=order.id)

    # Prevent duplicate review
    if hasattr(order, 'review'):
        return redirect('order_detail', pk=order.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.reviewer = request.user
            review.seller = order.seller
            review.save()
            return redirect('order_detail', pk=order.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/create_review.html', {
        'form': form,
        'order': order
    })