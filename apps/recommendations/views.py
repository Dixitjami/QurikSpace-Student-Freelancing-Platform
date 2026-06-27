import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import RecommendationRequestForm
from .models import RecommendationRequest
from .services import recommend_freelancers


def recommendations_home(request):
    form = RecommendationRequestForm(request.POST or None)
    results = []
    recommendation_request = None

    if request.method == 'POST' and form.is_valid():
        recommendation_request = form.save(commit=False)
        if request.user.is_authenticated:
            recommendation_request.client = request.user
        recommendation_request.save()
        results = recommend_freelancers(recommendation_request)

    return render(request, 'recommendations/recommendations.html', {
        'form': form,
        'results': results,
        'recommendation_request': recommendation_request,
    })


@csrf_exempt
@require_POST
def recommendation_api(request):
    """
    JSON API for future frontend/mobile clients.

    It reuses the same service layer as the Django template view, keeping the AI
    ranking logic in one place and making the architecture easier to extend.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    form = RecommendationRequestForm(payload)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    recommendation_request = form.save(commit=False)
    if request.user.is_authenticated:
        recommendation_request.client = request.user
    recommendation_request.save()

    results = recommend_freelancers(recommendation_request)
    data = [{
        'freelancer_id': result.freelancer.id,
        'username': result.freelancer.username,
        'score': result.score,
        'skill_match': result.skill_match,
        'rating': result.rating,
        'completed_projects': result.completed_projects,
        'similar_projects': result.similar_projects,
        'budget_fit': result.budget_fit,
        'delivery_fit': result.delivery_fit,
        'average_delivery_time': result.average_delivery_time,
        'lowest_price': str(result.lowest_price) if result.lowest_price else None,
        'explanation': result.explanation,
    } for result in results]

    return JsonResponse({'results': data})

