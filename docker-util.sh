#!/bin/sh


usage() {
    echo "Usage:"
    echo "$0 build [service]  - build docker images"
    echo "$0 start            - start services defined in docker-util.conf"
    echo "$0 stop             - stop all services"
    echo "$0 clean-network    - remove networks with name epa-*"
    echo "$0 clean-volume     - remove volumes with name epa-*"
}


build_docker_image() {
    echo "Build docker images using docker-compose build ... "

    # FIXME: need to build epa-package_py first, this is workaround
    docker-compose -f epa-package_py/docker-compose.yml build $@

    compose_files=$(find ./ -name docker-compose.yml)
    for f in $compose_files
    do
        enabled=$(cat $f | yq read - x-cameo.build.enable)
        if $enabled
        then
            docker-compose -f $f build $@
        fi
    done

    # FIXME: nginx dev build, this is workaround
    docker-compose -f analysis.epa.gov.tw/docker-compose.yml \
                   -f analysis.epa.gov.tw/docker-compose.override.yml \
        build $@
}


_get_enabled_stack() {
    compose_files=$(find . -name docker-compose.yml)
    for f in $compose_files
    do
        enabled=$(cat $f | yq read - x-cameo.deploy.enable)
        priority=$(cat $f | yq read - x-cameo.deploy.priority)
        if $enabled
        then
            echo "$priority:$f"
        fi
    done | sort -n $@
}


start_services() {
    DEPLOY=${1:-"staging"}
    echo "Start stack for [[ ${DEPLOY} ]] ..."
    echo

    stacks=$(_get_enabled_stack)
    for line in $stacks
    do
        compose_file=$(echo $line | cut -f 2 -d ":")
        stack_name=$(cat $compose_file | yq read - x-cameo.deploy.stack_name)
        echo "Starting ${stack_name}"
        if [ $DEPLOY = "dev" ]
        then
            d=$(dirname $compose_file)
            f=$(basename -s .yml $compose_file)
            dev_file="$d/$f.override.yml"
            docker stack deploy -c $compose_file -c $dev_file $stack_name
        else
            docker stack deploy -c $compose_file $stack_name
        fi
        echo
    done
}


stop_services() {
    DEPLOY=${1:-"staging"}
    echo "Stop stack for [[ ${DEPLOY} ]] ..."
    echo

    stacks=$(_get_enabled_stack -r)
    for line in $stacks
    do
        compose_file=$(echo $line | cut -f 2 -d ":")
        stack_name=$(cat $compose_file | yq read - x-cameo.deploy.stack_name)
        echo "Stoping ${stack_name}"
        docker stack rm $stack_name
        echo
    done
}


clean_network() {
    # only remove network with name starts with epa-*
    for network in $(docker network ls --format {{.Name}} | grep -e '^epa-*')
    do
        docker network rm ${network}
    done
}


clean_volume() {
    # only remove volume with name starts with epa-*
    for volume in $(docker volume ls --format {{.Name}} | grep -e '^epa-*')
    do
        docker volume rm ${volume}
    done
}


key="$1"

case $key in
build)
    shift
    build_docker_image $@
    exit
    ;;
start)
    shift
    start_services $@
    exit
    ;;
stop)
    shift
    stop_services
    exit
    ;;
clean-network)
    clean_network
    exit
    ;;
clean-volume)
    clean_volume
    exit
    ;;
*)    # unknown option
    usage
    exit 1
    ;;
esac

usage
