from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class Redirect404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if the response status code is 404
        if response.status_code == 404:
            # Redirect to the dashboard page
            return redirect('arcade_dashboard')
        return response
