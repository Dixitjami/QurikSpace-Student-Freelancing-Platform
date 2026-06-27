from django.shortcuts import render
from apps.payments.models import Transaction
from apps.payments.models import Wallet
# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.gigs.models import GigTier
from .models import Order


@login_required
def create_order(request, tier_id):
    if request.user.user_type != 'client':
        return redirect('dashboard')

    tier = get_object_or_404(GigTier, id=tier_id)
    gig = tier.gig

    order = Order.objects.create(
        gig=gig,
        tier=tier,
        client=request.user,
        seller=gig.seller,
        price=tier.price
    )

    # Simulate escrow hold
    Transaction.objects.create(
    user=request.user,
    order=order,
    amount=order.price,
    transaction_type='escrow_hold'
    )

    return redirect('order_detail', order.id)

from django.shortcuts import render


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/order_detail.html', {'order': order})


from django.http import HttpResponseForbidden


@login_required
def accept_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.user != order.seller:
        return HttpResponseForbidden("Only seller can accept this order.")

    if order.status != 'pending':
        return redirect('order_detail', pk=pk)

    order.status = 'in_progress'
    order.save()

    return redirect('order_detail', pk=pk)


@login_required
def deliver_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.user != order.seller:
        return HttpResponseForbidden("Only seller can deliver this order.")

    if order.status != 'in_progress':
        return redirect('order_detail', pk=pk)

    order.status = 'delivered'
    order.save()

    return redirect('order_detail', pk=pk)


@login_required
def approve_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.user != order.client:
        return HttpResponseForbidden("Only client can approve this order.")

    if order.status != 'delivered':
        return redirect('order_detail', pk=pk)

    order.status = 'completed'
    order.save()

    # Commission Logic (10%)
    commission_rate = 0.10
    commission = order.price * commission_rate
    seller_amount = order.price - commission

# Get seller wallet
    seller_wallet = Wallet.objects.get(user=order.seller)

# Credit seller
    seller_wallet.balance += seller_amount
    seller_wallet.save()

# Record transactions
    Transaction.objects.create(
    user=order.seller,
    order=order,
    amount=seller_amount,
    transaction_type='release'
)

    Transaction.objects.create(
    user=order.seller,
    order=order,
    amount=commission,
    transaction_type='commission'
)

    return redirect('order_detail', pk=pk)


@login_required
def my_orders(request):
    if request.user.user_type == 'student':
        # Freelancer sees orders where they are seller
        orders = Order.objects.filter(seller=request.user)
    else:
        # Client sees orders they placed
        orders = Order.objects.filter(client=request.user)

    return render(request, 'orders/my_orders.html', {
        'orders': orders
    })