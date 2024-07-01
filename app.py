import os
import inspect
import requests
import wsgiadapter
from webob import Request, Response
from parse import parse
from jinja2 import Environment, FileSystemLoader


class WebNyxApp:
    def __init__(self, templates_dir="templates"):
        self.routes = dict()

        self.template_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )

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
                response.status_code = 405
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

