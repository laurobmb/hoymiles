# Hoymiles Solar

[![Docker Repository on Quay](https://quay.io/repository/lagomes/hoymiles_notifications/status "Docker Repository on Quay")](https://quay.io/repository/lagomes/hoymiles_notifications)

## Define variables

    export USUARIO='<usuario hoymiles>
    export SENHA='<senha hoymiles>'
    export CHAT_ID='<chat ID>'
    export TOKEN='<token botfather>'
    export DEBUG='<valor de 0 para desativado e 1 para ativado>'

## Build Container

    buildah bud --layers true -f Dockerfile -t quay.io/lagomes/hoymiles:v1

## Run Container

    podman run -it --name notifications --rm \
       -e USUARIO='<usuario hoymiles> \
       -e SENHA='<senha hoymiles>' \
       -e CHAT_ID='<chat ID>' \
       -e TOKEN='<token botfather>' \
       -e DEBUG='<valor de 0 para desativado e 1 para ativado>' \
       -e STATUS_COLETA_LOCAL=True \
       quay.io/lagomes/hoymiles:v1

# References

* [bot API telegram](https://core.telegram.org/bots)
* [Lib python](https://python-telegram-bot.org/)