Installing django-tinyuser
==========================

Add django-tinyuser to your project using pip and the Git repository:

.. code-block:: bash

    # Clone the repository and enter the project directory
    git clone https://codeberg.org/c9moser/django-tinyuser.git
    cd django-tinyuser
    # Install the package and its dependencies
    pip install -r requirements.txt
    pip install -e .

Or, if you prefer to install directly from the Git repository without cloning and using poetry,
which is recommended for managing dependencies in Python projects, you can run the following command:

.. code-block:: bash

    poetry add git+https://codeberg.org/c9moser/django-tinyuser.git


Then, add ``django_tinyuser`` to your ``INSTALLED_APPS`` in your Django settings:

.. code-block:: python

    INSTALLED_APPS = [
         ...
         'allauth',
         'allauth.account',
         ... # other allauth apps you use
         'django_tinyuser',
         ...
    ]

You also need to add the following authentication backends to your settings:

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        ...
        # default Django authentication backend, required for admin
        # and other auth features
        'django.contrib.auth.backends.ModelBackend',
        # for django-allauth, required for authentication and account management
        'allauth.account.auth_backends.AuthenticationBackend',
        ... # other authentication backends you may use
    )

Additionally, make sure to include the necessary context processors for django-allauth
and django-tinyuser with templates overrides in your settings:

.. code-block:: python

    from django_tinyuser.global_templates.bootstrap import PATH as TINYUSER_TEMPLATES_PATH

    TEMPLATES = [
        {
            ... # other template settings
            # add the path to the bootstrap templates for django-tinyuser ensure that this
            # path is included before any other template directories to allow for overrides
             'DIRS': [TINYUSER_TEMPLATES_PATH, ...],
            ...
            'OPTIONS': {
                'context_processors': [
                    ... # other context processors
                    'django.template.context_processors.request',  # required by allauth
                    'django_tinyuser.context_processors.tinyuser', # for django-tinyuser
                    ... # other context processors

                ],
            },
        },
    ]

.. TODO:: Add instructions for customizing templates and static files, and for configuring settings like LOGIN_URL, LOGOUT_URL, etc.

Finally, run the migrations to create the necessary database tables:

.. code-block:: bash

    python manage.py migrate django_tinyuser
