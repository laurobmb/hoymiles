# Tests

## Define variables

    export USUARIO='<usuario hoymiles>
    export SENHA='<senha hoymiles>'
    export CHAT_ID='<chat ID>'
    export TOKEN='<token botfather>'
    export DEBUG='<valor de 0 para desativado e 1 para ativado>'

## Build Container

    buildah bud -f Dockerfile -t quay.io/lagomes/hoymiles:refatoranfo_v1

## Run Container

    podman run -it --name notifications --rm \
       -e USUARIO='<usuario hoymiles> \
       -e SENHA='<senha hoymiles>' \
       -e CHAT_ID='<chat ID>' \
       -e TOKEN='<token botfather>' \
       -e DEBUG='<valor de 0 para desativado e 1 para ativado>' \
       quay.io/lagomes/hoymiles:v1
