from django.core.exceptions import PermissionDenied

def author_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.type == 'author':
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapped_view