#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <remote-image ...>" >&2
    exit 1
fi

while [ $# -gt 0 ]; do
    remote_image="$1"
    shift
    echo "[INFO] Pushing image to remote: $remote_image"
    ifs_save="$IFS"
    IFS=$'\n'
    for img_conf in $(cat imagetab); do
        image_name="$(echo "$img_conf" | cut -d: -f1)"
        dockerfile_path="$(echo "$img_conf" | cut -d: -f2)"
        git_branch="$(echo "$img_conf" | cut -d: -f3)"
        tags="$(echo "$img_conf" | cut -d: -f4)"
        if [ -z "$image_name" ] || [ -z "$dockerfile_path" ] || [ -z "$git_branch" ] || [ -z "$tags" ]; then
            echo "[CRITICAL] Invalid image configuration: '$img_conf'! Each line must contain exactly 4 fields separated by colons." >&2
            exit 1
        fi
        for tag in $(echo "$tags" | tr ',' '\n'); do
            podman tag "$image_name" "$remote_image:$tag"
            podman push "$remote_image:$tag"
            if [ $? -ne 0 ]; then
                echo "[CRITICAL] Failed to push image '$image_name' with tag '$tag' to remote '$remote_image'!" >&2
                exit 1
            fi
        done
    done
done