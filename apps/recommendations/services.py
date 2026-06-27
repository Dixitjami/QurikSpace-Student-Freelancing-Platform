import math
import re
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal

from django.db.models import Avg, Count, Min, Q

from apps.accounts.models import CustomUser
from apps.orders.models import Order
from apps.reviews.models import Review


STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'in',
    'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'with', 'you',
    'your', 'we', 'will', 'need', 'needs', 'project', 'work',
}


@dataclass
class RecommendationResult:
    freelancer: CustomUser
    score: float
    skill_match: float
    rating: float
    completed_projects: int
    similar_projects: int
    budget_fit: bool
    delivery_fit: bool
    average_delivery_time: int | None
    lowest_price: Decimal | None
    explanation: list[str]


def tokenize(text):
    """Normalize project/profile text into useful NLP tokens for TF-IDF."""
    words = re.findall(r'[a-z0-9+#.]+', (text or '').lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 1]


def cosine_similarity(vector_a, vector_b):
    """Measures semantic closeness between project requirements and freelancer profiles."""
    common_terms = set(vector_a) & set(vector_b)
    numerator = sum(vector_a[term] * vector_b[term] for term in common_terms)
    norm_a = math.sqrt(sum(value * value for value in vector_a.values()))
    norm_b = math.sqrt(sum(value * value for value in vector_b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return numerator / (norm_a * norm_b)


def build_tfidf_vectors(documents):
    """
    Converts text documents into TF-IDF vectors.

    TF-IDF gives higher importance to meaningful rare terms such as "django",
    "figma", or "payment gateway" and lower importance to common repeated terms.
    """
    tokenized_documents = [tokenize(document) for document in documents]
    document_count = len(tokenized_documents)
    document_frequency = Counter()

    for tokens in tokenized_documents:
        document_frequency.update(set(tokens))

    vectors = []
    for tokens in tokenized_documents:
        term_frequency = Counter(tokens)
        total_terms = len(tokens) or 1
        vector = {}
        for term, count in term_frequency.items():
            tf = count / total_terms
            idf = math.log((document_count + 1) / (document_frequency[term] + 1)) + 1
            vector[term] = tf * idf
        vectors.append(vector)

    return vectors


def project_text_from_request(request_obj):
    return ' '.join([
        request_obj.project_title,
        request_obj.project_description,
        request_obj.required_skills,
    ])


def freelancer_profile_text(freelancer):
    profile = getattr(freelancer, 'studentprofile', None)
    gigs = freelancer.gigs.filter(is_active=True).prefetch_related('tiers')
    portfolio_items = freelancer.portfolio_items.all()

    parts = [
        freelancer.username,
        getattr(profile, 'bio', ''),
        getattr(profile, 'skills', ''),
        getattr(profile, 'experience_level', ''),
        getattr(profile, 'field_of_study', ''),
    ]
    parts.extend([gig.title for gig in gigs])
    parts.extend([gig.description for gig in gigs])
    parts.extend([item.title for item in portfolio_items])
    parts.extend([item.description for item in portfolio_items])
    return ' '.join(filter(None, parts))


def skill_overlap_score(required_skills, freelancer):
    required = set(tokenize(required_skills.replace(',', ' ')))
    profile = getattr(freelancer, 'studentprofile', None)
    freelancer_skills = set(tokenize(getattr(profile, 'skills', '').replace(',', ' ')))
    if not required:
        return 0.0
    return len(required & freelancer_skills) / len(required)


def get_average_delivery_time(freelancer):
    average_time = freelancer.gigs.filter(is_active=True).aggregate(
        avg=Avg('delivery_time')
    )['avg']
    return round(average_time) if average_time else None


def recommend_freelancers(request_obj, limit=10):
    """
    Main AI recommendation pipeline.

    1. Build a requirement document from the client brief.
    2. Build one document for each freelancer from profile, gigs, and portfolio.
    3. Use TF-IDF + cosine similarity for semantic search.
    4. Blend semantic score with ratings, similar work, pricing, and delivery fit.
    5. Return explainable ranked results for the client.
    """
    freelancers = list(
        CustomUser.objects.filter(user_type='student')
        .select_related('studentprofile')
        .prefetch_related('gigs__tiers', 'portfolio_items')
    )
    if not freelancers:
        return []

    project_text = project_text_from_request(request_obj)
    freelancer_documents = [freelancer_profile_text(freelancer) for freelancer in freelancers]
    vectors = build_tfidf_vectors([project_text] + freelancer_documents)
    project_vector = vectors[0]
    freelancer_vectors = vectors[1:]

    results = []
    for freelancer, vector in zip(freelancers, freelancer_vectors):
        semantic_score = cosine_similarity(project_vector, vector)
        overlap_score = skill_overlap_score(request_obj.required_skills, freelancer)
        skill_match = min(1.0, (semantic_score * 0.65) + (overlap_score * 0.35))

        rating = Review.objects.filter(seller=freelancer).aggregate(avg=Avg('rating'))['avg'] or 0
        completed_projects = Order.objects.filter(
            seller=freelancer,
            status='completed'
        ).count()
        similar_projects = Order.objects.filter(
            seller=freelancer,
            status='completed'
        ).filter(
            Q(gig__title__icontains=request_obj.project_title) |
            Q(gig__description__icontains=request_obj.required_skills.split(',')[0].strip())
        ).count()

        lowest_price = freelancer.gigs.filter(is_active=True).aggregate(
            min_price=Min('tiers__price')
        )['min_price']
        budget_fit = bool(lowest_price and lowest_price <= request_obj.budget)

        average_delivery_time = get_average_delivery_time(freelancer)
        delivery_fit = bool(
            average_delivery_time and average_delivery_time <= request_obj.delivery_deadline
        )

        rating_score = float(rating) / 5
        completed_score = min(completed_projects / 10, 1)
        similar_score = min(similar_projects / 5, 1)
        budget_score = 1 if budget_fit else 0
        delivery_score = 1 if delivery_fit else 0

        final_score = (
            skill_match * 45 +
            rating_score * 20 +
            completed_score * 12 +
            similar_score * 10 +
            budget_score * 8 +
            delivery_score * 5
        )

        explanation = [
            f'{round(skill_match * 100)}% skill match',
            f'completed {completed_projects} projects',
            f'completed {similar_projects} similar projects',
            'fits client budget' if budget_fit else 'above or missing budget data',
            f'average delivery time: {average_delivery_time} days' if average_delivery_time else 'delivery data not available',
        ]

        results.append(RecommendationResult(
            freelancer=freelancer,
            score=round(final_score, 2),
            skill_match=round(skill_match * 100, 1),
            rating=round(float(rating), 1),
            completed_projects=completed_projects,
            similar_projects=similar_projects,
            budget_fit=budget_fit,
            delivery_fit=delivery_fit,
            average_delivery_time=average_delivery_time,
            lowest_price=lowest_price,
            explanation=explanation,
        ))

    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

