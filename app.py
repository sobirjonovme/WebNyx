import os
import inspect
import requests
import wsgiadapter
from webob import Request, Response
from parse import parse
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise


class WebNyxApp:
    def __init__(self, templates_dir="templates", static_dir="static"):
        self.routes = dict()

        self.template_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )

        self.exception_handler = None

        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

        self.middlewares = list()

    def __call__(self, environ, start_response):
        return self.whitenoise(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)

        # run middlewares before handling the request
        self.middleware_process_request(request)

        # handle the request
        response = self.handle_request(request)

        # run middlewares after handling the request
        self.middleware_process_response(request, response)

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
                response.status_code = 405
                response.text = "Method not allowed"
                return response

        try:
            handler(request, response, **kwargs)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            self.exception_handler(request, response, e)

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

    def add_handler(self, path, handler):
        # check if the path already exists in the routes dict
        if path in self.routes:
            raise AssertionError(f"Route already exists: {path}")

        self.routes[path] = handler

    def route(self, path):
        """
        This method is not a decorator, but it returns a decorator.
        It is called a decorator factory.
        """

        def wrapper(handler):
            # this function is the actual decorator
            self.add_handler(path, handler)
            return handler

        # return the actual decorator
        return wrapper

    def test_session(self):
        """
        This method is not a test, but it is called by a test.
        """
        session = requests.Session()
        session.mount(prefix="http://testserver", adapter=wsgiadapter.WSGIAdapter(self))
        return session

    def template(self, template_name, context: dict = None):
        if context is None:
            context = {}

        template = self.template_env.get_template(template_name)
        rendered_html = template.render(**context).encode()

        return rendered_html

    def add_exception_handler(self, handler):
        self.exception_handler = handler

    def add_middleware(self, middleware):
        self.middlewares.append(middleware)

    def middleware_process_request(self, request):
        for middleware_cls in self.middlewares[::-1]:
            middleware = middleware_cls()
            middleware.process_request(request)

    def middleware_process_response(self, request, response):
        for middleware_cls in self.middlewares:
            middleware = middleware_cls()
            middleware.process_response(request, response)
