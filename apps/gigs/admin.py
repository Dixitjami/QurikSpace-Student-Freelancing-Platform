from django.contrib import admin

# Register your models here.

from .models import Category, Gig, GigTier, MainCategory, SubCategory


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    fields = ("name",)
    list_display = ("name", "subcategory_count")
    search_fields = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=True)

    def subcategory_count(self, obj):
        return obj.subcategories.count()

    subcategory_count.short_description = "Sub categories"

    def save_model(self, request, obj, form, change):
        obj.parent = None
        super().save_model(request, obj, form, change)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    fields = ("name", "parent")
    list_display = ("name", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "parent__name")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Category.objects.filter(parent__isnull=True).order_by("name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Gig)
admin.site.register(GigTier)
