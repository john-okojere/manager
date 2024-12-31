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

class SectionBasedAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Apply only if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user's section is "arcade"
            if request.user.section.title() == "Arcade":
                # Allow access only to URLs starting with /arcade/
                if not request.path.startswith('/arcade/'):
                    return redirect('resturant_dashboard')
            if request.user.section.title() == "Resturant":
                # Allow access only to URLs starting with /resturant/
                if not request.path.startswith('/resturant/'):
                    return redirect('resturant_dashboard')
        return None