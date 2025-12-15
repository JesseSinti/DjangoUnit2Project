from .models import *
def current_url(request):
    return {
        'current_path': request.path,
        'current_full_url': request.get_full_path(),
        'current_absolute_uri': request.build_absolute_uri(),
    }

def base_view(request):
    membership = OrganizationMembership.objects.get(
            user=request.user, 
        )
    
    if membership.role == "admin":
        status = 1
    elif membership.role == 'user':
        status = 2
    else: 
        status = 3
    print(status)

    return {
        'status' : status,
        'membership' : membership
    }
    
    