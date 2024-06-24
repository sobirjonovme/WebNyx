from webob import Request, Response


class WebNyxApp:
    def __init__(self):
        self.routes = dict()

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()

        handler = self.find_handler(request.path)

        if handler is None:
            self.default_response(response)
        else:
            handler(request, response)

        return response

    def find_handler(self, path):
        return self.routes.get(path, None)

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found!"

    def route(self, path):
        """
        This method is not a decorator, but it returns a decorator.
        It is called a decorator factory.
        """
        def wrapper(handler):
            # this is the actual decorator
            self.routes[path] = handler
            return handler

        # return the actual decorator
        return wrapper
