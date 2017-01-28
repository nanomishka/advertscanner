#!/bin/bash

source config/default_watcher.sh
declare -a services=(
    'cian'
    'avito'
)

for service in "${services[@]}"
do
    service_script=${service}.py
    if ps aux | grep "[${service_script::1}]${service_script:1}"; then
        echo ${service}" is running"
    else
        nohup ${python_path} ${service_script} > output/nohup.log 2> output/nohup.log &
        echo $(date +'%Y/%m/%d %H:%M:%S')': start '${service} >> output/watcher.log
   fi
done