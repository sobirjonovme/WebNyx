import inspect
from webob import Request, Response
from parse import parse


class WebNyxApp:
    def __init__(self):
        self.routes = dict()

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request.path)

        if handler is None:
            self.default_response(response)
            return response

        if inspect.isclass(handler):
            handler = getattr(handler(), request.method.lower(), None)
            if handler is None:
                response.text = "Method not allowed"
                return response

        handler(request, response, **kwargs)
        return response

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named

        # if no handler matched the request path, return None
        return None, None

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found!"

    def route(self, path):
        """
        This method is not a decorator, but it returns a decorator.
        It is called a decorator factory.
        """

        # check if the path already exists in the routes dict
        if path in self.routes:
            raise AssertionError(f"Route already exists: {path}")

        def wrapper(handler):
            # this is the actual decorator
            self.routes[path] = handler
            return handler

        # return the actual decorator
        return wrapper
