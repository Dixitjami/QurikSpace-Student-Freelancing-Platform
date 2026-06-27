'''
from django import forms
from .models import Gig, Category


class GigForm(forms.ModelForm):

    # ===== BASIC TIER =====
    basic_price = forms.DecimalField(
        label="Basic Price",
        widget=forms.NumberInput(attrs={
            'class': 'w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400',
            'placeholder': 'Enter basic price'
        })
    )

    basic_description = forms.CharField(
        label="Basic Description",
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400',
            'rows': 3,
            'placeholder': 'Describe what is included in Basic package'
        })
    )

    # ===== STANDARD TIER =====
    standard_price = forms.DecimalField(
        label="Standard Price",
        widget=forms.NumberInput(attrs={
            'class': 'w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400',
            'placeholder': 'Enter standard price'
        })
    )

    standard_description = forms.CharField(
        label="Standard Description",
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400',
            'rows': 3,
            'placeholder': 'Describe what is included in Standard package'
        })
    )

    # ===== PREMIUM TIER =====
    premium_price = forms.DecimalField(
        label="Premium Price",
        widget=forms.NumberInput(attrs={
            'class': 'w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400',
            'placeholder': 'Enter premium price'
        })
    )

    premium_description = forms.CharField(
        label="Premium Description",
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400',
            'rows': 3,
            'placeholder': 'Describe what is included in Premium package'
        })
    )

    class Meta:
        model = Gig
        fields = ['title', 'description']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-400',
                'placeholder': 'I will build a professional Django website'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-400',
                'rows': 5,
                'placeholder': 'Explain your service in detail...'
            }),
        }
        '''
from django import forms
from .models import Gig, Category


class SubCategorySelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        category = getattr(value, "instance", None)
        if category:
            option["attrs"]["data-parent"] = category.parent_id
        elif value:
            try:
                category = self.choices.queryset.get(pk=value)
                option["attrs"]["data-parent"] = category.parent_id
            except (AttributeError, Category.DoesNotExist, ValueError):
                pass
        return option


class GigForm(forms.ModelForm):
    main_category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        empty_label="Select category",
        widget=forms.Select(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-teal-500'
        })
    )

    # ===== BASIC =====
    basic_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500'
        })
    )

    basic_delivery = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500'
        })
    )

    basic_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500',
            'rows': 3
        })
    )

    # ===== STANDARD =====
    standard_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500'
        })
    )

    standard_delivery = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500'
        })
    )

    standard_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500',
            'rows': 3
        })
    )

    # ===== PREMIUM =====
    premium_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500'
        })
    )

    premium_delivery = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500'
        })
    )

    premium_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-teal-500',
            'rows': 3
        })
    )

    class Meta:
        model = Gig
        fields = ['title', 'description', 'category', 'delivery_time']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-teal-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-slate-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-teal-500',
                'rows': 5
            }),
            'category': SubCategorySelect(attrs={
                'class': 'w-full border border-slate-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-teal-500'
            }),
            'delivery_time': forms.NumberInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-teal-500',
                'min': 1
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['main_category'].queryset = Category.objects.filter(
            parent__isnull=True
        ).order_by('name')

        category_field = self.fields['category']
        category_field.label = "Sub Category"
        category_field.queryset = Category.objects.filter(
            parent__isnull=False
        ).select_related('parent').order_by('parent__name', 'name')
        category_field.empty_label = "Select sub category"
        category_field.label_from_instance = lambda obj: obj.name

        if self.instance and self.instance.pk and self.instance.category:
            self.fields['main_category'].initial = self.instance.category.parent

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category and category.parent_id is None:
            raise forms.ValidationError("Please select a sub category, not a main category.")
        return category

    def clean(self):
        cleaned_data = super().clean()
        main_category = cleaned_data.get('main_category')
        sub_category = cleaned_data.get('category')

        if main_category and sub_category and sub_category.parent_id != main_category.id:
            self.add_error('category', "Please select a sub category from the selected category.")

        return cleaned_data
