import pytest

BASE_URL = "http://testserver"


def add_routes_to_app(app):
    @app.route("/home")
    def home(request, response):
        response.text = "Hello from the HOME page"

    @app.route("/about")
    def about(request, response):
        response.text = "Hello from the ABOUT page"

    return home, about


def add_parametrized_route(app):
    @app.route("/hello/{name}")
    def greeting(request, response, name):
        response.text = f"Hello, {name}"

    return greeting


def add_class_based_routes(app):
    @app.route("/books")
    class Books:
        def get(self, request, response):
            response.text = "Books page"

        def post(self, request, response):
            response.text = "Endpoint to create a book"
            response.status_code = 201


def test_route_adding(app):
    home, about = add_routes_to_app(app)

    assert app.routes == {"/home": home, "/about": about}


def test_duplicate_route_throws_exception(app):
    add_routes_to_app(app)

    with pytest.raises(AssertionError):
        @app.route("/home")
        def home2(request, response):
            response.text = "Hello from the HOME page"


def test_requests_can_be_sent_by_test_client(app, test_client):
    add_routes_to_app(app)

    response = test_client.get(f"{BASE_URL}/home")
    assert response.status_code == 200
    assert response.text == "Hello from the HOME page"

    response = test_client.get(f"{BASE_URL}/about")
    assert response.status_code == 200
    assert response.text == "Hello from the ABOUT page"


def test_parametrized_routes(app, test_client):
    add_parametrized_route(app)

    assert test_client.get(f"{BASE_URL}/hello/web-nyx").text == "Hello, web-nyx"
    assert test_client.get(f"{BASE_URL}/hello/Dili").text == "Hello, Dili"
    assert test_client.get(f"{BASE_URL}/hello/Umar").text == "Hello, Umar"


def test_default_response(app, test_client):
    add_routes_to_app(app)

    response = test_client.get(f"{BASE_URL}/doesnotexist")
    assert response.status_code == 404
    # see WebNyxApp.default_response method for the response text
    assert response.text == "Not found!"


def test_class_based_routes(app, test_client):
    add_class_based_routes(app)

    response = test_client.get(f"{BASE_URL}/books")
    assert response.status_code == 200
    assert response.text == "Books page"

    response = test_client.post(f"{BASE_URL}/books")
    assert response.status_code == 201
    assert response.text == "Endpoint to create a book"


def test_class_based_routes_not_allowed(app, test_client):
    add_class_based_routes(app)

    response = test_client.put(f"{BASE_URL}/books")
    # see WebNyxApp.handle_request method for the response status code and text
    assert response.status_code == 405
    assert response.text == "Method not allowed"


def test_route_alternative_adding_handler(app, test_client):
    def new_handler(request, response):
        response.text = "It is new handler"

    app.add_handler("/new-handler", new_handler)

    response = test_client.get(f"{BASE_URL}/new-handler")
    assert response.status_code == 200
    assert response.text == "It is new handler"


def test_template_handler(app, test_client):
    @app.route("/test-template")
    def template_handler(request, response):
        context = {"title": "Best title", "body": "Best body"}
        response.body = app.template(
            "test_template.html",
            context=context
        )

    response = test_client.get(f"{BASE_URL}/test-template")

    assert "Best title" in response.text
    assert "Best body" in response.text
    assert "text/html" in response.headers["Content-Type"]
