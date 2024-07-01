from app import WebNyxApp


app = WebNyxApp()


# Below code is the same as following handler registering codes
"""
decorator = app.route("/about")
home = decorator(home)
"""


@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"


@app.route("/about")
def about(request, response):
    response.text = "Hello from the ABOUT page"


@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}!"


@app.route("/books")
class Books:
    def get(self, request, response):
        response.text = "Books page"

    def post(self, request, response):
        response.text = "Endpoint to create a book"


def new_handler(request, response):
    response.text = "It is new handler"


app.add_handler("/new-handler", new_handler)


@app.route("/template")
def template_handler(request, response):
    context = {"title": "Best title", "body": "It is html rendered page"}
    response.body = app.template(
        "test_template.html",
        context=context
    )


def on_handler(request, response, exc):
    response.text = "Something bad happened"


app.add_exception_handler(on_handler)


@app.route("/exception")
def exception_throwing_handler(request, response):
    raise AttributeError("some exception")
