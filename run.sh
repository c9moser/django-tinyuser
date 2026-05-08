#!/bin/sh
self="$(realpath "$0")"
BASE_DIR="$(dirname "$self")"; epxort BASE_DIR

cd "$BASE_DIR"

: ${DEFAULT_VIRTUAL_ENV:="$BASE_DIR/.venv"}
: ${PYTHON_REQUIREMENTS:=$BASE_DIR/requirements.txt}

if [ -n "${PYTHON_REQUIREMENTS%%/*}" ]; then  # check if path is relative
	PYTHON_REQUIREMENTS="$BASE_DIR/$PYTHON_REQUIREMENTS"
fi
export PYTHON_REQUIREMENTS
echo "[INFO] PYTHON_REQUIREMENTS=$PYTHON_REQUIREMENTS"

: ${PYTHON_POETRY:=0}
if [ -n "$(echo ${PYTHON_POETRY} | grep -E '^(1|[yY][eE][sS]|[oO][nN]|[tT][rR][uU][eE])$')" ]; then
	if ! command -v poetry >/dev/null 2>&1; then
		echo "[CRITICAL] Poetry is not installed or not in PATH" >&2
		echo "Install it (for example: pip install poetry) and retry." >&2
		exit 1
	fi
fi

# initializing


IFS=$'\n'
for i in $(ls "$BASE_DIR/run.d/* | sort"); do
	if [ "${i##**.}" = "sh" ]; then
		. "$i" || exit $?
	elif [ -x "$i" ]; then
		echo "[INFO] Running initialization script: $i"
		"$i" || exit $?
	fi
done

if [ $# -eq 0 ]; then
	echo "[INFO] No command provided, defaulting to 'runserver'"
	runserver
	exit $?
fi

case "$1" in
	runserver)
		shift
		${HTTP_SERVER}_runserver "$@"
		exit $?
		;;

	# django management commands
	manage)
		shift
		manage "$@"
		exit $?
		;;
	makemigrations)
		shift
		makemigrations "$@"
		exit $?
		;;
	migrate)
		shift
		migrate "$@"
		exit $?
		;;
	collectstatic)
		shift
		collectstatic "$@"
		exit $?
		;;
	makemessages)
		shift
		makemessages "$@"
		exit $?
		;;
	compilemessages)
		shift
		compilemessages "$@"
		exit $?
		;;
	createsuperuser)
		shift
		createsuperuser "$@"
		exit $?
		;;

	# django runserver variants
	django-runserver)
		shift
		django_runserver "$@"
		exit $?
		;;
	django-runserver-plus)
		shift
		django-extensions_runserver "$@"
		exit $?
		;;
	django-extensions-runserver)
		shift
		django-extensions_runserver "$@"
		exit $?
		;;
	# Poetry commands
	poetry-install)
		shift
		poetry_install "$@"
		exit $?
		;;
	poetry-update)
		shift
		poetry_update "$@"
		exit $?
		;;
	poetry)
		shift
		poetry "$@"
		exit $?
		;;

    # Apache
	apache-runserver)
		shift
		apache_runserver "$@"
		exit $?
		;;
	apache-make-site)
		shift
		apache_make_site "$@"
		exit $?
		;;

	# Daphne
	daphne-runserver)
		shift
		daphne_runserver "$@"
		exit $?
		;;

	# uWSGI
	uwsgi-runserver)
		shift
		uwsgi_runserver "$@"
		exit $?
		;;
	uwsgi-make-ini)
		shift
		uwsgi_make_ini "$@"
		exit $?
		;;
	help)
		less << EOF
Usage: run.sh <command> [options] [args]

Available commands:
  runserver                Run the development server (default)
  manage <command>         Run a Django management command
  makemigrations           Create new migrations based on the changes detected to your models
  migrate                  Apply migrations to the database
  collectstatic            Collect static files into STATIC_ROOT
  makemessages             Create message files for translation
  compilemessages          Compile message files for translation
  createsuperuser          Create a new superuser

  django-runserver         Run the development server using Django's built-in runserver
  django-runserver-plus    Run the development server using django-extensions' runserver_plus
  django-extensions-runserver Run the development server using django-extensions' runserver_plus

  poetry-install           Install dependencies using Poetry
  poetry-update            Update dependencies using Poetry
  poetry                   Run a Poetry command

  apache-runserver         Run the application with Apache and mod_wsgi
  apache-make-site         Create an Apache site configuration for the application

  daphne-runserver         Run the application with Daphne ASGI server

  uwsgi-runserver          Run the application with uWSGI server
  uwsgi-make-ini           Create a uWSGI ini file for the application
EOF
		exit 0
		;;
	*)
		echo "[INFO] Running command: $*"
		exec "$@"
		exit $?
		;;
esac
