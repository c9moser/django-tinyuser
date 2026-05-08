
django_runserver() {
    if [ $# -eq 0 ]; then
        if [ "$CONTAINERIZED" -eq 1 ]; then
            local addr="0.0.0.0:$HTTP_PORT"
        else
            local addr="127.0.0.1:$HTTP_PORT"
        fi
        exec $python manage.py runserver "$addr"
    else
        exec $python manage.py runserver "$@"
    fi
    return $?
}

django-extensions_runserver() {
    if [ $# -eq 0 ]; then
        if [ "$CONTAINERIZED" -eq 1 ]; then
            local addr="0.0.0.0:$HTTP_PORT"
        else
            local addr="127.0.0.1:$HTTP_PORT"
        fi
        exec $python manage.py runserver_plus "$addr"
    else
        exec $python manage.py runserver_plus "$@"
    fi
}

manage() {
    $python manage.py "$@"
    return $?
}

migrate() {
    manage migrate "$@"
    return $?
}

makemigrations() {
    manage makemigrations "$@"
    return $?
}

collectstatic() {
    manage collectstatic --noinput
    return $?
}

makemessages() {
    manage makemessages "$@"
    return $?
}

compilemessages() {
    manage compilemessages "$@"
    return $?
}
