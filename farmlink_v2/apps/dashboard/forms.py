from django import forms
from apps.catalog.models import Product


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleImageField, self).clean(file, initial) for file in files]


class ProductForm(forms.ModelForm):
    images = MultipleImageField(required=False, label='Product photos')

    class Meta:
        model = Product
        fields = ('category', 'name', 'description', 'price_per_kg', 'quantity_available', 'unit', 'condition', 'is_negotiable', 'region', 'city', 'status')
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}
