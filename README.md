# Django TinyUser

**Neither the app nor the documentation is finished yet, but I wanted to publish the project anyway, because I need it for my projects and I want to share it with others. If you want to contribute to the project, feel free to open a pull request or an issue.**

*Django TinyUser* is a small user authentication app for django.

This project is distributed under the [*0BSD*-License](./LICENSE.django-tinyuser.md).

It uses *[django-allauth](https://docs.allauth.org/en/latest/)* as backend and
overloads the templates for *Bootstrap* and *Tailwind CSS*.


It is ment to be used by projects that need a small user authentication for for
their projects and don't want to implmenent their own. It is used by my
projects and docker images for basic user authentication using *django-allauth*.


## Installation

Add *TinyUser* to your project using poetry

```sh
poetry add https+git://codeberg.org/c9moser/django-tinyuser.git
```


## Usage

### Configuration of your project

```python
from django_tinyuser.global_templates.tailwindcss import PATH as TINYUSER_GLOBAL_TEMPLATES
...
# Register allauth and django_tinyuser
APPS = [
    ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount', # if you want to use social auth
    # add the providers you want to use, e.g. 'allauth.socialaccount.providers.google',
    'django_tinyuser',
    ...
]
```

If you use *Bootstrap*, you can add overloads to your TEMPLATES. The overloads are located in
the global_templates folder of django_tinyuser. You can add them to your TEMPLATES like
this is and they will be used instead of the default templates of django-allauth.

Note that you have to add the path to the overloads before the default templates of django-allauth,
otherwise they will not be used.

And don't forget to add the context processors for *django-allauth*, and *django-tinyuser*
otherwise the templates will not work.

```python
from django_tinyuser.global_templates.bootstrap import PATH as TINYUSER_GLOBAL_TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Add Bootstrap overloads to TEMPLATES
        'DIRS': [TINYUSER_GLOBAL_TEMPLATES],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_tinyuser.context_processors.tinyuser'
                ...
            ],
        },
    },
...
]
```

If you use *Tailwind CSS*, you can add the overloads to your TEMPLATES like this is and they will be used instead of the default templates of django-allauth.
```python
from django_tinyuser.global_templates.tailwindcss import PATH as TINYUSER_GLOBAL_TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Add Tailwind CSS overloads to TEMPLATES
        'DIRS': [TINYUSER_GLOBAL_TEMPLATES],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_tinyuser.context_processors.tinyuser'
                ...
            ],
        },
    },
...
]
```
You also need to set the `CSS_FRAMEWORK` option in your settings.py to the css framework you use,
otherwise the templates will not work.

```python
CSS_FRAMEWORK = 'bootstrap' # if you use Bootstrap
# or
CSS_FRAMEWORK = 'tailwindcss' # if you use Tailwind CSS
# or
CSS_FRAMEWORK = 'custom' # if you use custom templates
```

And you need to set the `AUTH_USER_MODEL` to `django_tinyuser.TinyUser` in your settings.py or
to an overloaded model if you have customized the user model.

```python
AUTH_USER_MODEL = 'django_tinyuser.TinyUser'
```

Then add the urls of *django-allauth* to your urls.py

```python
from django.urls import path, include
urlpatterns = [
    ...
    path('accounts/', include('allauth.urls')),
    ...
]
```

Finally run the migrations to create the required tables for *django-tinyuser*.

```bash
    python manage.py migrate django_tinyuser
```


## Configuration options to be added to your settings.py
### CSS\_FRAMEWORK

One of the following values:

+ *bootstrap* - if you use Bootstrap (partially implemented, but not tested yet)
+ *tailwindcss* - if you use Tailwind CSS (not implemented yet)
+ *custom* - custom template (you need to overload all
    templates yourself and add the path to your TEMPLATES)

Note that the default value is 'bootstrap', so if you use Bootstrap, you don't need to set this option.

**If you use Tailwind CSS, you need to set this option to 'tailwindcss', otherwise the templates will not work.**
