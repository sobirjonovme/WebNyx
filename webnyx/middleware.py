

class BaseMiddleware:
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass
