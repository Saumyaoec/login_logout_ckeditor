from functools import update_wrapper
from django.http import Http404


class authenticated_or_404(object):
    def __init__(self, func):
        self.func = func
        update_wrapper(self, func)

    def __call__(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404
        return self.func(request, *args, **kwargs)