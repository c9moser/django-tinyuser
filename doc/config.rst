Configuration
=============

BASE_TEMPLATE
-------------
    The base template to extend for all templates in the app.
    This should be a string representing the path to the base template, e.g., 'base.html'.
    The default value is 'django_tinyuser/{CSS_FRAMEWORK}/base.html'.

    **Note:** This setting might be overridden by the `TINYUSER_BASE_TEMPLATE` variable.

TINYUSER_BASE_TEMPLATE
----------------------
    The base template to extend for all templates in the app. This setting takes precedence
    over `BASE_TEMPLATE` if both are defined. This allows you to set a global base template
    for all tinyuser templates without having to modify the `BASE_TEMPLATE` setting.

    Default is None, which means that `BASE_TEMPLATE` will be used as the base template for
    all tinyuser templates.

CSS_FRAMEWORK
--------------
    The CSS framework to use for styling the templates. Supported values are 'bootstrap',
    'tailwindcss' or 'custom'.

    Default is `'bootstrap'`.

    **Note:** If you set this to 'custom', you will need to provide your own templates that
    extend the base template and include the necessary CSS classes for styling.

    **Note:** Tailwind CSS is currently not supported, but will be added in a future release.

USE_POSTGRESQL_SCHEMAS
----------------------
    Whether to use PostgreSQL-specific features in the database schema. If set to True, the
    schema will include PostgreSQL-specific fields and indexes for better performance. If set to
    False, the schema will be more generic and compatible with a wider range of databases.

    Default is `False`.

POSTGRESQL_AUTH_SCHEMA
----------------------
    Sets the authentication schema for PostgreSQL databases. If set to 'public', the authentication
    schema will be set to 'public'. If set to 'tinyuser', the authentication schema will be set to 'tinyuser'.

    Default is `'public'`.

    **Note:** This setting is only relevant if `USE_POSTGRESQL_SCHEMAS` is set to True.

TINYUSER_EXTERNAL_MANAGED
-------------------------
    If set to True, the `TinyUser` model will be considered as externally managed,
    and the app will not attempt to create or modify the database schema for it.
    This is useful if you are using a custom user model that extends `TinyUser`
    and you want to manage the database schema yourself.

    Default is `False`.

AUTH_EXTERNAL_MANAGED
---------------------
    If set to True, the authentication models (e.g., `Friendship`, `allauth` models,
    `django.contrib.auth` models, etc.) will be considered as externally managed, and
    the app will not attempt to create or modify the database schema for them. This is
    useful if you want to manage the database schema for these models yourself.

    Default is `False`.
