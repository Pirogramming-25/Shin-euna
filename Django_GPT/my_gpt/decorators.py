from functools import wraps
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.urls import reverse

def model_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            query = urlencode({"next": request.get_full_path(), "required": "1"})
            return redirect(f"{reverse('login')}?{query}")
        return view_func(request, *args, **kwargs)
    return wrapper
