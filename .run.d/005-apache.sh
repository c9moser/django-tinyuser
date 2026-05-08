if [ $CONTAINERIZED -eq 1 ]; then
    : ${APACHE_SITES_AVAILABLE:="/config/apache/sites-available"}
    : ${APACHE_SITES_ENABLED:="/config/apache/sites-enabled"}
else
    : ${APACHE_SITES_AVAILABLE:="/etc/apache2/sites-available"}
    : ${APACHE_SITES_ENABLED:="/etc/apache2/sites-enabled"}
fi
export APACHE_SITES_AVAILABLE APACHE_SITES_ENABLED

apache_mkconfig() {
    local config=$APACHE_SITES_AVAILABLE/000-django_project.conf
    if [ $APACHE_INSECURE_REDIRECT -eq 1 ]; then
        envsubst $BASE_DIR/httpd/000-app.insecure-redirect.conf > $config
    else
        envsubst < "$BASE_DIR/httpd/000-app.template.conf" > $config
    fi
    if [ $HTTP_SSL_ENABLED -eq 1 ]; then
        echo "" >> $config
        echo "" >> $config
        envsubst < "$BASE_DIR/httpd/000-app.ssl.template.conf" >> $config
    fi
    if [ $CONTAINERIZED -eq 1 ]; then
        ln -s $config $APACHE_SITES_ENABLED/000-django_project.conf
}

apache_runserver() {
    _apache_pids=""

    # Start Apache in the foreground and capture its PID so that we can manage it properly.
    # This allows us to handle signals properly and ensure that Apache is stopped gracefully when the script exits.
    # We will also set up a trap to catch termination signals and stop Apache gracefully.
    #
    # This approach allows us to hook up an ASGI server (like uWSGI) in front of Apache, and ensure that both processes are managed correctly.
    apachectl -D FOREGROUND start &
    _apache_pids=$!

    trap "echo '[INFO] Stopping Apache...'; kill -TERM $_apache_pids; wait $_apache_pids" EXIT
    wait $_apache_pids

    exit $?
}