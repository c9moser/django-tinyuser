RE_TRUE="^(1|[yY]|[yY][eE][sS]|[tT][rR][uU][eE]|[Oo][Nn])$" ; export RE_TRUE
RE_FALSE="^(0|[nN]|[nN][oO]|[fF][aA][lL][sS][eE]|[Oo][Ff][fF])$" ; export RE_FALSE

is_true() {
    if [ -n "$1" ] && echo "$1" | grep -E -q "$RE_TRUE"; then
        return 0
    else
        return 1
    fi
}

is_false() {
    if [ -n "$1" ] && echo "$1" | grep -E -q "$RE_FALSE"; then
        return 0
    else
        return 1
    fi
}

bval() {
    if is_true "$1"; then
        echo 1
    elif is_false "$1"; then
        echo 0
    elif [ -n "$1"]; then
        bval $1
    elif [ -z "$1" ]; then
        echo "invalid boolean value: '$1'" >&2
        return 1
    fi
}


if [ -f "$BASE_DIR/.env" ]; then
    echo "[INFO] Sourcing base environment file '$BASE_DIR/.env'"
    . "$BASE_DIR/.env"
fi

: ${PROJECT_ENV_FILE:=$BASE_DIR/django_project/env}
if [ -f "$PROJECT_ENV_FILE" ]; then
    echo "[INFO] Sourcing project environment file '$PROJECT_ENV_FILE'"
    . "$PROJECT_ENV_FILE"
else
    echo "[INFO] No project environment file found at '$PROJECT_ENV_FILE', skipping sourcing it"
fi
export PROJECT_ENV_FILE

: ${CONTAINERIZED:=0}
CONTAINERIZED=$(bval "$CONTAINERIZED", 0)
export CONTAINERIZED

if [ "$CONTAINERIZED" -eq 1 ]; then


else
    CONTAINERIZED=0

fi
if [ "$CONTAINERIZED" -eq 1 ]; then
    echo "[INFO] Running in containerized environment, setting CONTAINERIZED to 1"
    : ${ENV_FILE:="/config/settings.env"}
else
    echo "[INFO] Running in non-containerized environment, setting CONTAINERIZED to 0"
    : ${ENV_FILE:="$BASE_DIR/django_project/env"}
fi
if [ -f "$ENV_FILE" ]; then
    echo "[INFO] Sourcing environment file '$ENV_FILE'"
    . "$ENV_FILE"
else
    echo "[INFO] No environment file found at '$ENV_FILE', skipping sourcing it"
fi
export ENV_FILE

PYTHON_POETRY=$(bval "$PYTHON_POETRY", 0)
export PYTHON_POETRY

cd "$BASE_DIR" || exit 1
if [ $CONTAINERIZED -eq 1 ]; then

    : ${DATA_DIR:=/data}
    : ${RUN_DIR:=/run}
    : ${CONFIG_DIR:=/config}
    : ${MEDIA_ROOT:=/data/media}
    : ${STATIC_ROOT:=/data/static}
else
    : ${ENV_FILE:="$BASE_DIR/django_project/env"}
    : ${DATA_DIR:="$BASE_DIR/.data"}
    : ${RUN_DIR:="$BASE_DIR/.run"}
    : ${CONFIG_DIR:="$BASE_DIR/django_project/local_settings"}
    : ${MEDIA_ROOT:="$BASE_DIR/.data/media"}
    : ${STATIC_ROOT:="$BASE_DIR/.data/static"}
fi
export DATA_DIR
export RUN_DIR
export CONFIG_DIR
export MEDIA_ROOT
export STATIC_ROOT

if [ $CONTAINERIZED -eq 1 ]; then
    echo "[INFO] Running in containerized environment, checking data and configuration directories"

    # data directory
    if [ ! -d "$DATA_DIR" ]; then
        echo "[INFO] Data directory '$DATA_DIR' does not exist, creating it..."
        mkdir -p "$DATA_DIR" || { echo "[CRITICAL] Failed to create data directory '$DATA_DIR'!" >&2; exit 1; }
    fi
    if [ ! -f "$DATA_DIR/.htaccess" ]; then
        echo "[INFO] $DATA_DIR/.htaccess file does not exist, creating it..."
        cp "$BASE_DIR/httpd/datadir.htaccess" "$DATA_DIR/.htaccess" || { echo "[CRITICAL] Failed to create $DATA_DIR/.htaccess file!" >&2; exit 1; }
    fi

    # media and static directories
    if [ ! -d "$MEDIA_ROOT" ]; then
        mkdir -p "$MEDIA_ROOT" || { echo "[CRITICAL] Failed to create MEDIA_ROOT directory '$MEDIA_ROOT'!" >&2; exit 1; }
    fi
    if [ ! -f "$MEDIA_ROOT/.htaccess" ]; then
        echo "[INFO] $MEDIA_ROOT/.htaccess file does not exist, creating it..."
        cp "$BASE_DIR/httpd/media.htaccess" "$MEDIA_ROOT/.htaccess" || { echo "[CRITICAL] Failed to create $MEDIA_ROOT/.htaccess file!" >&2; exit 1; }
    fi
    if [ ! -d "$STATIC_ROOT" ]; then
        mkdir -p "$STATIC_ROOT" || { echo "[CRITICAL] Failed to create STATIC_ROOT directory '$STATIC_ROOT'!" >&2; exit 1; }
    fi
    if [ ! -f "$STATIC_ROOT/.htaccess" ]; then
        echo "[INFO] $STATIC_ROOT/.htaccess file does not exist, creating it..."
        cp "$BASE_DIR/httpd/static.htaccess" "$STATIC_ROOT/.htaccess" || { echo "[CRITICAL] Failed to create $STATIC_ROOT/.htaccess file!" >&2; exit 1; }
    fi

    # run directory
    if [ ! -d "$RUN_DIR" ]; then
        echo "[INFO] Run directory '$RUN_DIR' does not exist, creating it..."
        mkdir -p "$RUN_DIR" || { echo "[CRITICAL] Failed to create run directory '$RUN_DIR'!" >&2; exit 1; }
    fi
    if [ ! -d "$RUN_DIR/logs" ]; then
        echo "[INFO] $RUN_DIR/logs directory does not exist, creating it..."
        mkdir -p "$RUN_DIR/logs" || { echo "[CRITICAL] Failed to create $RUN_DIR/logs directory!" >&2; exit 1; }
    fi

    # config directory
    if [ ! -d "$CONFIG_DIR" ]; then
        echo "[INFO] Config directory '$CONFIG_DIR' does not exist, creating it..."
        mkdir -p "$CONFIG_DIR" || { echo "[CRITICAL] Failed to create config directory '$CONFIG_DIR'!" >&2; exit 1; }
    fi
    if [ ! -d "$CONFIG_DIR/sites-available" ]; then
        echo "[INFO] $CONFIG_DIR/sites-available directory does not exist, creating it..."
        mkdir -p "$CONFIG_DIR/sites-available" || { echo "[CRITICAL] Failed to create $CONFIG_DIR/sites-available directory!" >&2; exit 1; }
    fi
    if [ ! -d "$CONFIG_DIR/sites-enabled" ]; then
        echo "[INFO] $CONFIG_DIR/sites-enabled directory does not exist, creating it..."
        mkdir -p "$CONFIG_DIR/sites-enabled" || { echo "[CRITICAL] Failed to create $CONFIG_DIR/sites-enabled directory!" >&2; exit 1; }
    fi

    : ${SSL_CERTIFICATE_FILE:=/etc/ssl/certs/ssl-cert-snakeoil.pem}
    : ${SSL_CERTIFICATE_KEY_FILE:=/etc/ssl/private/ssl-cert-snakeoil.key}
    : ${SSL_CA_CERTIFICATE_FILE:=""}
else
    if [ ! -d "$DATA_DIR" ]; then
        echo "[WARNING] Data directory '$DATA_DIR' does not exist! Creating it..." >&2
        mkdir -p "$DATA_DIR" || { echo "[CRITICAL] Failed to create data directory '$DATA_DIR'!" >&2; exit 1; }
    fi
    if [ ! -d "$CONFIG_DIR" ]; then
        echo "[WARNING] Config directory '$CONFIG_DIR' does not exist! Creating it..." >&2
        mkdir -p "$CONFIG_DIR" || { echo "[CRITICAL] Failed to create config directory '$CONFIG_DIR'!" >&2; exit 1; }
    fi
    if [ ! -d "$MEDIA_ROOT" ]; then
        echo "[WARNING] MEDIA_ROOT directory '$MEDIA_ROOT' does not exist! Creating it..." >&2
        mkdir -p "$MEDIA_ROOT" || { echo "[CRITICAL] Failed to create MEDIA_ROOT directory '$MEDIA_ROOT'!" >&2; exit 1; }
    fi
    if [ ! -d "$STATIC_ROOT" ]; then
        echo "[WARNING] STATIC_ROOT directory '$STATIC_ROOT' does not exist! Creating it..." >&2
        mkdir -p "$STATIC_ROOT" || { echo "[CRITICAL] Failed to create STATIC_ROOT directory '$STATIC_ROOT'!" >&2; exit 1; }
    fi
    if [ ! -f $STATIC_ROOT/.htaccess ]; then
        echo "[INFO] $STATIC_ROOT/.htaccess file does not exist, creating it..."
        cp "$BASE_DIR/httpd/static.htaccess" "$STATIC_ROOT/.htaccess" || { echo "[CRITICAL] Failed to create $STATIC_ROOT/.htaccess file!" >&2; exit 1; }
    fi
    if [ ! -f $MEDIA_ROOT/.htaccess ]; then
        echo "[INFO] $MEDIA_ROOT/.htaccess file does not exist, creating it..."
        cp "$BASE_DIR/httpd/media.htaccess" "$MEDIA_ROOT/.htaccess" || { echo "[CRITICAL] Failed to create $MEDIA_ROOT/.htaccess file!" >&2; exit 1; }
    fi
    if [ ! -d "$RUN_DIR" ]; then
        echo "[CRITICAL] Run directory '$RUN_DIR' does not exist!" >&2
        exit 1
    fi

    : ${SSL_CERTIFICATE_FILE:="/etc/ssl/certs/ssl-cert-snakeoil.pem"}
    : ${SSL_CERTIFICATE_KEY_FILE:="/etc/ssl/private/ssl-cert-snakeoil.key"}
    : ${SSL_CA_CERTIFICATE_FILE:=""}
    echo "[INFO] Running in containerized environment, setting PYTHON_REQUIREMENTS to /app/requirements.txt"
fi
export SSL_CERTIFICATE_FILE
export SSL_CERTIFICATE_KEY_FILE
export SSL_CA_CERTIFICATE_FILE

# ########################################################################### #
# Configure virtual environment
# ########################################################################### #
if [ -z "$VIRTUAL_ENV" ]; then
	venv_targets="$(echo -en "$BASE_DIR/.venv\n$BASE_DIR/venv\n$(dirname "$BASE_DIR")/.venv\n$(dirname "$BASE_DIR")/venv")"

	if [ "$CONTAINERIZED" ]; then
		venv_targets=$(echo -en "/venv\n$venv_targets")
	fi
	if [ -n "$( echo "$PYTHON_POETRY" | grep -E "$RE_TRUE" )" ]; then
		venv_targets=$(echo -en "$(poetry env info -p 2>/dev/null)\n$venv_targets")
	fi

	ifs_save="$IFS"
	IFS=$'\n'
	for i in $venv_targets; do
		if [ -d "$i" ]; then
			VIRTUAL_ENV="$i"
		fi
	done
	IFS="$ifs_save"

	if [ -z "$VIRTUAL_ENV" ]; then
		VIRTUAL_ENV="$DEFAULT_VIRTUAL_ENV"
	fi
fi
export VIRTUAL_ENV

# ########################################################################### #
# Configure Poetry
# ########################################################################### #
if [ $PYTHON_POETRY -eq 1 ]; then
    if command -v poetry >/dev/null 2>&1; then
        echo "[INFO] Poetry is enabled and found in PATH, using it for Python dependency management"
    else
        echo "[CRITICAL] Poetry is enabled but not found in PATH!" >&2
        echo "Install it (for example: pip install poetry) and retry." >&2
        exit 1
    fi
fi

# ########################################################################### #
# SSL and HTTP Configuration
# ########################################################################### #

: ${SSL_ENABLED:=0}
if [ -n "$( echo "$SSL_ENABLED" | grep -E "$RE_TRUE" )" ]; then
    SSL_ENABLED=1
    : ${HTTP_SERVER:='django-extensions'}
else
    SSL_ENABLED=0
    : ${HTTP_SERVER:='django'}
fi
export SSL_ENABLED

: ${HTTP_PORT:=80}
: ${HTTPS_PORT:=443}
export HTTP_PORT
export HTTPS_PORT

: ${HTTP_SERVER:='django'}
export HTTP_SERVER

if [ -n "$( echo "$CONTAINERIZED" | grep -E "$RE_TRUE" )" ]; then
    : ${HTTP_SSL:=0}
    : ${HTTP_INSECURE:=1}
    : ${HTTP_INSECURE_REDIRECT:=0}
else
    : ${HTTP_SSL:=0}
    : ${HTTP_INSECURE:=1}
    : ${HTTP_INSECURE_REDIRECT:=0}
    : ${HTTP_ENABLED:=0}
fi
export HTTP_SSL
export HTTP_INSECURE
export HTTP_INSECURE_REDIRECT
export HTTP_ENABLED

# ########################################################################### #
# Poetry and Python Configuration
# ########################################################################### #

if [ $PYTHON_POETRY -eq 1 ]; then
    python="poetry run python"
    if ! command -v poetry >/dev/null 2>&1; then
        echo "[CRITICAL] Poetry is enabled but not found in PATH!" >&2
        echo "Install it (for example: pip install poetry) and retry." >&2
        exit 1
    fi
else
    if [ -f "$VIRTUAL_ENV/bin/activate" ]; then
        . "$VIRTUAL_ENV/bin/activate"
    fi
    python="python"
    if ! command -v python >/dev/null 2>&1; then
        echo "[CRITICAL] Python is not installed or not in PATH!" >&2
        exit 1
fi
