from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Wallet, Transaction


@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    total_earned = (
        transactions.filter(transaction_type='release').aggregate(total=Sum('amount'))['total'] or 0
    )
    pending_amount = (
        transactions.filter(transaction_type='escrow_hold').aggregate(total=Sum('amount'))['total'] or 0
    )
    total_commission = (
        transactions.filter(transaction_type='commission').aggregate(total=Sum('amount'))['total'] or 0
    )

    return render(request, 'payments/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
        'total_earned': total_earned,
        'pending_amount': pending_amount,
        'total_commission': total_commission,
    })
