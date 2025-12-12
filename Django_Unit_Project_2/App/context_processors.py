def current_url(request):
    return {
        'current_path': request.path,
        'current_full_url': request.get_full_path(),
        'current_absolute_uri': request.build_absolute_uri(),
    }
