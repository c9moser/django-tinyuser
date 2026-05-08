#!/bin/sh

self="$(realpath "$0")"
BASE_DIR="$(dirname "$self")"
: ${USER_CONFIG_DIR:=~/.config/$USER}
: ${PODMAN_BUILD_CONFIG_DIR="$USER_CONFIG_DIR/podman/build"}

cd "$BASE_DIR"

VERSION="0.1.0"
IMAGE_NAME="django-project"
TAGS="dev,dev-trixie,main"

# Format:
# image_name:remote-image-name:dockerfile_path:tag1(,tag2,...):git-branch,

IMAGETAB="$(cat << EOF
django-project-dev-trixie:dockerfiles/Dockerfile.dev.trixie:main
django-project-dev-trixie-py313:dockerfiles/Dockerfile.dev.py313-trixie:main
django-project-dev-trixie-py314:dockerfiles/Dockerfile.dev.py314-trixie:main
EOF
)"

if [ -f "$PODMAN_BUILD_CONFIG_DIR/django-project.remotes" ]; then
    echo "[INFO] Sourcing image configuration from '$PODMAN_BUILD_CONFIG_DIR/imagestab.conf'"
    . "$PODMAN_BUILD_CONFIG_DIR/imagestab.conf"
else
    echo "[INFO] No image configuration file found at '$PODMAN_BUILD_CONFIG_DIR/imagestab.conf', using default configuration"
fi

ifs_save="$IFS"
IFS=$'\n'
for i in $(cat imagetab); do
    image_name="$(echo "$i" | cut -d: -f1)"
    dockerfile_path="$(echo "$i" | cut -d: -f2)"
    git_branch="$(echo "$i" | cut -d: -f3)"
    if [ -z "$image_name" ] || [ -z "$dockerfile_path" ] || [ -z "$git_branch" ]; then
        echo "[CRITICAL] Invalid image configuration: '$i'! Each line must contain exactly 3 fields separated by colons." >&2
        exit 1
    fi
    podman build -t "$image_name" -f "$dockerfile_path" --build-arg GIT_BRANCH="$git_branch" .
    if [ $? -ne 0 ]; then
        echo "[CRITICAL] Failed to build image '$image_name' from Dockerfile '$dockerfile_path' with git branch '$git_branch'!" >&2
        exit 1
    fi
done
IFS="$ifs_save"