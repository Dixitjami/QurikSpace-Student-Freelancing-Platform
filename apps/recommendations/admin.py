from django.contrib import admin

from .models import RecommendationRequest


@admin.register(RecommendationRequest)
class RecommendationRequestAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'client', 'budget', 'delivery_deadline', 'created_at')
    search_fields = ('project_title', 'project_description', 'required_skills')
    list_filter = ('created_at',)

