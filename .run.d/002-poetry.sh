# poetry.sh - Poetry support for run.sh

_ensure_poetry() {
    if ! command -v poetry >/dev/null 2>&1; then
        echo "[CRITICAL] Poetry is enabled but not found in PATH!" >&2
        echo "Install it (for example: pip install poetry) and retry." >&2
        exit 1
    fi
}

poetry() {
    _ensure_poetry
    local poetry_cmd="$(which poetry)"
    $poetry_cmd "$@"
    return $?
}

poetry_install() {
    _ensure_poetry
    poetry install "$@"
    return $?
}

poetry_update() {
    _ensure_poetry
    poetry update "$@"
    return $?
}
poetry_install() {
    _ensure_poetry
    if [ $# -eq 0 ]; then
        echo "[INFO] No command provided for poetry install, defaulting to 'install --no-interaction --all --no-root'"
        poetry install --no-interaction --all-groups --no-root
    else
        poetry install "$@"
    fi
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "[CRITICAL] Poetry install failed!" >&2
        exit $rc
    fi
    return 0
}
poetry_lock() {
    _ensure_poetry
    if [ $# -eq 0 ]; then
        echo "[INFO] No command provided for poetry lock, defaulting to 'lock --no-interaction --all'"
        poetry lock --no-interaction --all-groups
    else
        poetry lock "$@"
    fi
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "[CRITICAL] Poetry lock failed!" >&2
        exit $rc
    fi
    return 0
}

poetry_update() {
    _ensure_poetry
    if [ $# -eq 0 ]; then
        echo "[INFO] No command provided for poetry update, defaulting to 'update --no-interaction --all --no-root'"
        poetry update --no-interaction --all --no-root
    else
        poetry update "$@"
    fi
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "[CRITICAL] Poetry update failed!" >&2
        exit $rc
    fi
    return 0
}
