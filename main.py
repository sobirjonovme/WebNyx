from app import WebNyxApp


app = WebNyxApp()


# Below codes is the same as below code
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
