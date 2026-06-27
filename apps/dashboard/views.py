from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import Portfolio
from apps.gigs.models import Gig
from apps.orders.models import Order
from apps.payments.models import Transaction, Wallet
from apps.reviews.models import Review
from apps.messaging.models import Conversation, Message


# ðŸ” Dashboard Redirect Based on Role
@login_required
def dashboard_redirect(request):
    if request.user.user_type == 'student':
        return redirect('student_dashboard')
    elif request.user.user_type == 'client':
        return redirect('client_dashboard')
    else:
        return redirect('home')


# ðŸ‘¨â€ðŸ’» STUDENT (FREELANCER) DASHBOARD
@login_required
def student_dashboard(request):
    user = request.user
    dashboard_tab = request.GET.get('tab', 'overview')
    allowed_tabs = {
        'overview',
        'orders',
        'messages',
        'profile',
        'reviews',
        'wallet',
        'deadlines',
        'performance',
        'gigs',
    }
    if dashboard_tab not in allowed_tabs:
        dashboard_tab = 'overview'

    gigs_count = Gig.objects.filter(seller=user).count()
    my_gigs = Gig.objects.filter(seller=user).order_by('-created_at')
    orders_count = Order.objects.filter(seller=user).count()

    wallet, _ = Wallet.objects.get_or_create(user=user)

    reviews = Review.objects.filter(seller=user)
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    status_labels = ['Pending', 'In Progress', 'Delivered', 'Completed', 'Cancelled']
    order_status_counts = [
        Order.objects.filter(seller=user, status='pending').count(),
        Order.objects.filter(seller=user, status='in_progress').count(),
        Order.objects.filter(seller=user, status='delivered').count(),
        Order.objects.filter(seller=user, status='completed').count(),
        Order.objects.filter(seller=user, status='cancelled').count(),
    ]
    earnings_by_month_qs = (
        Transaction.objects
        .filter(user=user, transaction_type='release')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    earnings_month_labels = [
        item['month'].strftime('%b %Y') for item in earnings_by_month_qs if item['month']
    ]
    earnings_month_values = [float(item['total']) for item in earnings_by_month_qs]
    recent_orders = (
        Order.objects
        .filter(seller=user)
        .select_related('client', 'gig', 'tier')
        .order_by('-created_at')[:5]
    )
    recent_reviews = (
        reviews
        .select_related('reviewer', 'order', 'order__gig')
        .order_by('-created_at')[:4]
    )
    recent_transactions = (
        Transaction.objects
        .filter(user=user)
        .select_related('order', 'order__gig')
        .order_by('-created_at')[:5]
    )
    recent_messages = (
        Message.objects
        .filter(conversation__freelancer=user)
        .exclude(sender=user)
        .select_related('sender', 'conversation')
        .order_by('-timestamp')[:5]
    )
    unread_messages_count = Message.objects.filter(
        conversation__freelancer=user,
        is_seen=False,
    ).exclude(sender=user).count()
    portfolio_count = Portfolio.objects.filter(freelancer=user).count()
    gig_performance = (
        Gig.objects
        .filter(seller=user)
        .annotate(
            total_orders=Count('order'),
            completed_orders=Count('order', filter=Q(order__status='completed')),
            total_revenue=Sum('order__price', filter=Q(order__status='completed')),
        )
        .order_by('-total_orders', '-created_at')[:5]
    )

    now = timezone.now()
    active_orders = (
        Order.objects
        .filter(seller=user, status__in=['pending', 'in_progress'])
        .select_related('client', 'gig')
        .order_by('created_at')
    )
    deadline_alerts = []
    for order in active_orders:
        due_at = order.created_at + timedelta(days=order.gig.delivery_time or 0)
        days_left = (due_at.date() - now.date()).days
        if days_left <= 2:
            deadline_alerts.append({
                'order': order,
                'due_at': due_at,
                'days_left': days_left,
                'is_overdue': days_left < 0,
            })
        if len(deadline_alerts) == 5:
            break

    profile = getattr(user, 'studentprofile', None)
    profile_checks = []
    if profile:
        profile_checks = [
            ('Profile photo', bool(user.profile_image)),
            ('Bio', bool(profile.bio)),
            ('Skills', bool(profile.skills)),
            ('Education', bool(profile.university and profile.degree and profile.field_of_study)),
            ('Resume', bool(profile.resume)),
            ('Verification documents', bool(profile.student_id_card and profile.enrollment_proof)),
            ('Portfolio item', portfolio_count > 0),
            ('Published gig', gigs_count > 0),
        ]
    completed_profile_items = sum(1 for _, is_complete in profile_checks if is_complete)
    profile_completion = round((completed_profile_items / len(profile_checks)) * 100) if profile_checks else 0
    missing_profile_items = [label for label, is_complete in profile_checks if not is_complete][:4]

    return render(request, 'dashboard/student_dashboard.html', {
        'gigs_count': gigs_count,
        'my_gigs': my_gigs,
        'orders_count': orders_count,
        'wallet_balance': wallet.balance,
        'avg_rating': round(avg_rating, 1),
        'status_labels': status_labels,
        'order_status_counts': order_status_counts,
        'earnings_month_labels': earnings_month_labels,
        'earnings_month_values': earnings_month_values,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'recent_transactions': recent_transactions,
        'recent_messages': recent_messages,
        'unread_messages_count': unread_messages_count,
        'deadline_alerts': deadline_alerts,
        'profile_completion': profile_completion,
        'missing_profile_items': missing_profile_items,
        'portfolio_count': portfolio_count,
        'gig_performance': gig_performance,
        'dashboard_tab': dashboard_tab,
    })


# ðŸ§‘â€ðŸ’¼ CLIENT DASHBOARD
@login_required
def client_dashboard(request):
    user = request.user

    total_spent = Order.objects.filter(client=user).aggregate(
        total=Sum('price')
    )['total'] or 0

    messages_count = Conversation.objects.filter(client=user).count()
    active_orders_count = Order.objects.filter(
        client=user,
        status__in=['pending', 'in_progress', 'delivered'],
    ).count()
    recent_orders = (
        Order.objects
        .filter(client=user)
        .select_related('seller', 'gig', 'tier')
        .order_by('-created_at')[:5]
    )
    status_labels = ['Pending', 'In Progress', 'Delivered', 'Completed', 'Cancelled']
    order_status_counts = [
        Order.objects.filter(client=user, status='pending').count(),
        Order.objects.filter(client=user, status='in_progress').count(),
        Order.objects.filter(client=user, status='delivered').count(),
        Order.objects.filter(client=user, status='completed').count(),
        Order.objects.filter(client=user, status='cancelled').count(),
    ]
    spending_by_month_qs = list(
        Order.objects
        .filter(client=user)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('price'))
        .order_by('month')
    )
    spending_month_labels = [
        item['month'].strftime('%b %Y') for item in spending_by_month_qs if item['month']
    ]
    spending_month_values = [float(item['total']) for item in spending_by_month_qs]
    if not spending_month_values and float(total_spent) > 0:
        spending_month_labels = [timezone.now().strftime('%b %Y')]
        spending_month_values = [float(total_spent)]

    return render(request, 'dashboard/client_dashboard.html', {
        'total_spent': total_spent,
        'messages_count': messages_count,
        'active_orders_count': active_orders_count,
        'recent_orders': recent_orders,
        'status_labels': status_labels,
        'order_status_counts': order_status_counts,
        'spending_month_labels': spending_month_labels,
        'spending_month_values': spending_month_values,
    })
