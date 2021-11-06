# hoymilessolar

### Run command

    podman run -it --rm \
        -e usuario='your username' \
        -e senha='your password' \
        -e link='https://global.hoymiles.com/platform/login' \
        --name hoymiles \
        quay.io/lagomes/hoymiles:latest
