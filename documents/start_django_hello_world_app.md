# Start a Django Hello World App

---

## Setup

``` sh
cd <PROJECT>/analysis.epa.gov.tw/website
```

### 1. Virtualenv

```sh
python3.6 -m venv venv3.6
source venv3.6/bin/active
```

### 2. Install Package

``` sh
pip install -r requirements.txt
```

### 3. Create a Superuser for your Django devlopment

``` sh
python3 mange.py createsuperuser
```

### 4. Start Django

``` sh
python3 manage.py runserver
```



## Start new HelloWorld APP

### 1. Create a new django app

``` sh
python3 manage.py startapp hello_world
```

Please name your app's as short as possible, one world is perfect, two words is fine. Short app name will benefit when you developing.

### 2. Modify `main/urls.py`

Open `main/urls.py`, add your app's urls into `urlpatterns`:

```python
urlpatterns = [
	path("hello/", include("hello_world.urls")),
	...
]
```

* `"hello/"` is sub-url your app will use
* `include("hello_world.urls")` to include your app's `urls.py`

### 3. Register your app to project

Open `main/settings.py` , add yours config into `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
	"hello_world.apps.HelloWorldConfig",
	...
]
```

You can open hello_world/apps.py to find out config class name.

### 4. Edit your views.py

Open `hello_world/views.py`

```python
# -*- coding: utf-8 -*-
from django.shortcuts import render

def index(request):
    return render(request, 'hello_world/index.html')
```

### 5. Edit your hello world HTML template file

Create a new file `hello_world/templates/hello_world/hello.html `:

* There is another `hello_world` under `templates`, that is used for preventing import confliction
  * The first template search path is `main/templates/`
  * Your apps template is second priority. (here, `hello_world/templates/`)
  * If you create a html template `hello_world/templates/index.html` which confict with main `index.html` template, yours will never be loaded.

``` html
{% extends 'index.html' %}

{% load static %}

{% block css %}
<link href="{% static "hello_world/css/hello.css" %}" rel="stylesheet">
{% endblock %}


{% block javascript %}
<script src="{% static "hello_world/js/hello.js" %}"></script>
{% endblock %}


{% block content %}
<p id="yk_hello">
Hello YKK
</p>


{% if user.is_authenticated %}
    <p>Welcome, {{ user.get_username }}. Thanks for logging in.</p>
{% else %}
    <p>Welcome, new user. Please log in.</p>
{% endif %}


{% endblock %}
```

* Always `{% extends 'index.html' %}`, which is our main HTML template.
* Don't forget to add `{% load static %} for css/js/image loading
* Use `{% block css %}` to load your css files
* Use  `{% block javascript %}` to load you javascript files
* Put you content under  `{% block content %}`

Please check `main/templates/index.html`, which is our main HTML template. Your css and javascript blocks will be appended to main `index.html`, and your content block will replace the content block.

### 6. Add your app to side-menu

Open `main/tempaltes/index.html`

``` html
            <ul class="nav metismenu" id="side-menu">
                ...
                <li>
                    <a href="/hello/"><i class="fa fa-th-large"></i> <span class="nav-label">Hello view</span> </a>
                </li>
            </ul>
```

* Add your app under `<ul class="nav metismenu" id="side-menu">`
* Your app's name in `span`
* Your app's url in `<a href="/hello/">` , where `/hello` is defined in `main/urls.py`

### 7. edit your urls.py

```Python
from django.urls import path
from . import views

urlpatterns = [
	path("", views.index, name='hello_world'),
]
```



## Test Your App

http://127.0.0.1:8000/hello

