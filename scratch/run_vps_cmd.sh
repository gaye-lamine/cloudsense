#!/bin/bash
if [ -f .env ]; then
    get_env_var() {
        local var_name=$1
        local value=$(grep -E "^${var_name}=" .env | cut -d'=' -f2- | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        echo "$value"
    }
    VPS_PASSWORD=$(get_env_var "VPS_PASSWORD")
fi
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no root@72.60.213.116 "$@"
