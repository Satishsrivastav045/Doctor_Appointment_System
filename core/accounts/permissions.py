from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def has_role(user, role_name):
    return bool(
        user.is_authenticated
        and user.role
        and user.role.role_name == role_name
    )


def role_required(role_name, redirect_url="/login/"):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if has_role(request.user, role_name):
                return view_func(request, *args, **kwargs)

            messages.error(request, f"Only {role_name}s can access this page.")
            return redirect(redirect_url)

        return wrapper

    return decorator
