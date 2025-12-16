from .models import *
def current_url(request):
    return {
        'current_path': request.path,
        'current_full_url': request.get_full_path(),
        'current_absolute_uri': request.build_absolute_uri(),
    }


def base_view(request):
    
    if not request.user.is_authenticated:
        return {}

    
    membership = OrganizationMembership.objects.filter(user=request.user).first()

    
    if not membership:
        return {}
    
    if membership.role == "admin":
        status = 1
    elif membership.role == 'user':
        status = 2
    else: 
        status = 3

    return {
        'status': status,
        'membership': membership
    }
    