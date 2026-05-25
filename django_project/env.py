# vim: syn=python ts=4 sts=4 sw=4 smartindent expandtab

from pathlib import Path
from environ import Env
from .env_files import CONFIG_ENV_FILES, ENV_FILES

BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_SETTINGS_DIR = BASE_DIR / "django_project" / "local_settings"

ENV = Env(
        DEBUG=(bool, False),
        BASE_TEMPLATE=(str, ""),
        ALLOWED_HOSTS=(list, ['*']),  # allow all hosts by default, override in production  # noqa: E501
        DJANGO_SETTINGS_MODULE=(str, "django_project.settings"),
        DJANGO_DATA_DIR=(str, str(BASE_DIR / ".data")),
        DJANGO_ADMIN_URL=(str, "admin/"),
        CONFIG_ENV_FILES=(list, []),
        CONTAINER_DATA_DIR=(str, "/data"),
        CONTAINERIZED=(bool, False),
        DATABASE_CONFIG_METHOD=(str, "url"),
        DATABASE_URL=(str, f"sqlite:///{BASE_DIR}/.data/db.sqlite3"),
        ENV_FILES=(list, []),
        MEDIA_URL=(str, "media/"),
        MEDIA_ROOT=(str, str(BASE_DIR / ".data" / "media")),
        MYSQL_DB = (str, "django"),
        MYSQL_USER = (str, "django"),
        MYSQL_PASSWORD = (str, "django"),
        MYSQL_HOST = (str, "localhost"),
        MYSQL_PORT = (str, "3306"),
        POSTGRES_DB = (str, "django"),
        POSTGRES_USER = (str, "django"),
        POSTGRES_PASSWORD = (str, "django"),
        POSTGRES_HOST = (str, "localhost"),
        POSTGRES_PORT = (str, "5432"),
        SECRET_KEY=(str, "django-insecure-j#05f7jxku!2oy7(nzim=zl15c50_(=2nkfl*mtp28$+ubt(rl"),  # noqa: E501
        SECRET_KEY_FALLBACKS=(list, []),  # noqa: E501
        SQLITE_DB_NAME=(str, str(BASE_DIR / ".data" / "db.sqlite3")),
        STATIC_URL=(str, "static/"),
        STATIC_ROOT=(str, str(BASE_DIR / ".data" / "static")),
        VENV_DIR=(str, str(BASE_DIR / ".venv")),
        CSS_FRAMEWORK=(str, "bootstrap"),
        USE_POSTGRES_SCHEMAS=(bool, False),
        DJANGO_POSTGRES_SCHEMA=(str, "public"),
        POSTGRES_SCHEMA=(str, "public"),
        TINYUSER_SHOW_INDEX_PAGE=(bool, False),
        EMAIL_BACKEND=(str, "django.core.mail.backends.smtp.EmailBackend"),
        EMAIL_HOST=(str, "localhost"),
        EMAIL_PORT=(int, 25),
        EMAIL_USE_TLS=(bool, False),
        EMAIL_USE_SSL=(bool, False),
        EMAIL_HOST_USER=(str, ""),
        EMAIL_HOST_PASSWORD=(str, ""),
        DEFAULT_FROM_EMAIL=(str, "Django Webmaster <webmaster@localhost>"),
        EMAIL_SUBJECT_PREFIX=(str, "[Django] "),
        ADMINS=(list, []),  # noqa: E501
        ADMIN_EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
        ADMIN_EMAIL_HOST=(str, "localhost"),
        ADMIN_EMAIL_PORT=(int, 25),
        ADMIN_EMAIL_USE_TLS=(bool, False),
        ADMIN_EMAIL_USE_SSL=(bool, False),
        ADMIN_EMAIL_HOST_USER=(str, ""),
        ADMIN_EMAIL_HOST_PASSWORD=(str, ""),
        ADMIN_DEFAULT_FROM_EMAIL=(str, "Django Admin <admin@localhost>"),
        ADMIN_EMAIL_SUBJECT_PREFIX=(str, "[Django Admin] "),
        MANAGERS=(list, []),  # noqa: E501
        MANAGER_EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
        MANAGER_EMAIL_HOST=(str, "localhost"),
        MANAGER_EMAIL_PORT=(int, 25),
        MANAGER_EMAIL_USE_TLS=(bool, False),
        MANAGER_EMAIL_USE_SSL=(bool, False),
        MANAGER_EMAIL_HOST_USER=(str, ""),
        MANAGER_EMAIL_HOST_PASSWORD=(str, ""),
        MANAGER_DEFAULT_FROM_EMAIL=(str, "Django Manager <manager@localhost>"),
        MANAGER_EMAIL_SUBJECT_PREFIX=(str, "[Django Manager] "),
)

CONTAINERIZED = ENV("CONTAINERIZED")



for env_file in (Path(i).resolve() for i in CONFIG_ENV_FILES):
    if env_file.is_file():
        ENV.read_env(env_file)

if CONTAINERIZED:
    env_file = Path("/etc/django.env")
    if env_file.is_file():
        ENV.read_env(env_file)
    env_file = Path(ENV("CONTAINER_DATA_DIR")) / ".env"
    if env_file.is_file():
        ENV.read_env(env_file)
    DATADIR = Path(ENV("CONTAINER_DATA_DIR")).resolve()
    env_file = DATADIR / "dotenv"
    if env_file.is_file():
        ENV.read_env(env_file)

LOCAL_ENV_DIR = BASE_DIR / "django_project" / "local_settings"
env_file = LOCAL_ENV_DIR / 'env.local'
if env_file.is_file():
    ENV.read_env(env_file)

for env_file in (Path(i).resolve() for i in ENV.list("ENV_FILES")):
    if env_file.is_file():
        ENV.read_env(env_file)

del env_file
