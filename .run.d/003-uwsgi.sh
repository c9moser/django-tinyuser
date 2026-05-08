if [ $CONTAINREIZED -eq 1 ]; then
    : ${UWSGI_INI:="/config/uwsgi.ini"}
else
    : ${UWSGI_INI:="$BASE_DIR/django_project/local_settings/uwsgi.ini"}
fi
export UWSGI_INI



uwsgi_mkconfig() {
    if [ -f "$UWSGI_INI" ]; then
        echo "[INFO] uWSGI configuration file already exists: $UWSGI_INI"
    else
        echo "[INFO] Creating default uWSGI configuration file at: $UWSGI_INI"
        if [ $CONTAINERIZED -eq 1 ]; then
            : ${UWSGI_ADDRESS:="0.0.0.0:$HTTP_PORT"}
        else
            : ${UWSGI_ADDRESS:="127.0.0.1:$HTTP_PORT"}
        fi
        cat > "$UWSGI_INI" <<EOL
[uwsgi]
chdir = $BASE_DIR
module = django_project.wsgi:application
master = true
processes = 4
socket = $UWSGI_ADDRESS
chmod-socket = 660
vacuum = true
EOL
    fi
}

uwsgi_runserver() {
    if [ -f "$UWSGI_INI" ]; then
        echo "[INFO] Starting uWSGI with configuration file: $UWSGI_INI"
        exec uwsgi --ini "$UWSGI_INI"
        exit $?
    else
        echo "[CRITICAL] uWSGI configuration file not found: $UWSGI_INI" >&2
        exit 1
    fi
}
