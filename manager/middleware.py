from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout

class RoleBasedLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not (request.user.is_authenticated and (request.user.role == "Manager" or request.user.is_staff or request.user.level >= 3)):
            logout(request)
            return redirect('login')

class Redirect404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if the response status code is 404
        if response.status_code == 404:
            # Redirect to the dashboard page
            return redirect('arcade_dashboard')
        return response
