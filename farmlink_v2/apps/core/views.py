from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import ContactMessage


def about(request):
    return render(request, 'core/about.html')


@require_http_methods(['GET', 'POST'])
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()[:120]
        phone = request.POST.get('phone', '').strip()[:20]
        email = request.POST.get('email', '').strip()[:254]
        body = request.POST.get('message', '').strip()
        invalid_email = False
        if email:
            try:
                validate_email(email)
            except ValidationError:
                invalid_email = True
        if not name or not body or len(body) > 4000 or invalid_email:
            messages.error(request, 'Enter your name and a message (up to 4,000 characters).')
        else:
            ContactMessage.objects.create(name=name, phone=phone, email=email, message=body)
            messages.success(request, 'Thanks for reaching out. The FarmLink team will be in touch.')
            return redirect('core:contact')
    return render(request, 'core/contact.html')
