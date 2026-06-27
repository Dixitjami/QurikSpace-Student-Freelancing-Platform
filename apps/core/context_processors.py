from apps.gigs.models import Category


def service_categories(request):
    if not request.user.is_authenticated or request.user.user_type != 'client':
        return {}

    return {
        'header_categories': Category.objects.filter(
            parent__isnull=True
        ).prefetch_related('subcategories')
    }
