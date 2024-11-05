from django.utils.deprecation import MiddlewareMixin

class CustomCORSHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Set custom CORS headers
        if request.method == "OPTIONS":
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with"
            response["Access-Control-Allow-Origin"] = "http://localhost:5173" 
        return response
