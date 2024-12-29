from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout


class RoleBasedLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Apply only if the user is authenticated
        if request.user.is_authenticated:
            if not (request.user.role == "Manager" or request.user.is_staff or request.user.level >= 3):
                logout(request)
                return redirect('login')
        return None

class Redirect404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Apply only if the user is authenticated
        if request.user.is_authenticated:
            # Check if the response status code is 404
            if response.status_code == 404:
                # Redirect to the dashboard page
                if request.user.section.title() == "Arcade":
                    return redirect('arcade_dashboard')
                if request.user.section.title() == "Resturant":
                    return redirect('resturant_dashboard')
        return response
