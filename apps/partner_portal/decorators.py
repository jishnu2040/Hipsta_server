from functools import wraps
from rest_framework.response import Response


def subsctiption_required(view_func):
    @wraps(view_func)
    def  wrapper(request, *args, **kwargs):
        partner = getattr(request.user, 'partner_profile', None)
        subscription = getattr(partner, 'subscription', None)
        if not subscription or subscription.status != 'active':
            return Response({'error': 'Subscription required'}, status=403) 
        return view_func(request, *args, **kwargs)
    return wrapper