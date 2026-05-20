Configuration
=============

CSS_FRAMEWORK
--------------
    The CSS framework to use for styling the templates. Supported values are 'bootstrap',
    'tailwindcss' or 'custom'.

    Default is 'bootstrap'.

USE_POSTGRESQL_SCHEMAS
----------------------
    Whether to use PostgreSQL-specific features in the database schema. If set to True, the
    schema will include PostgreSQL-specific fields and indexes for better performance. If set to
    False, the schema will be more generic and compatible with a wider range of databases.

    Default is False.

POSTGRESQL_AUTH_SCHEMA
----------------------
    Sets the authentication schema for PostgreSQL databases. If set to 'public', the authentication
    schema will be set to 'public'. If set to 'tinyuser', the authentication schema will be set to 'tinyuser'.

    Default is 'public'.

    **Note:** This setting is only relevant if `USE_POSTGRESQL_SCHEMAS` is set to True.

TINYUSER_EXTERNAL_MANAGED
-------------------------
    If set to True, the `TinyUser` model will be considered as externally managed,
    and the app will not attempt to create or modify the database schema for it.
    This is useful if you are using a custom user model that extends `TinyUser`
    and you want to manage the database schema yourself.

    Default is False.

AUTH_EXTERNAL_MANAGED
---------------------
    If set to True, the authentication models (e.g., `Friendship`, `allauth` models, `django.contrib.auth` models, etc.)
    will be considered as externally managed,
    and the app will not attempt to create or modify the database schema for them.
    This is useful if you want to manage the database schema for these models yourself.

    Default is False.