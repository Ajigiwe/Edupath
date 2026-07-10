from functools import wraps
from django.shortcuts import redirect

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if request.user.is_authenticated:
            return redirect('home')
        return redirect('login')
    return _wrapped_view
