#!/bin/bash

try_append() {
    local key="$1"
    local value="$2"
    local msg="$3"

    HAS_KEY=$(grep "^$key" ~/.jupyter/jupyter_notebook_config.py | wc -l)

    if [[ $HAS_KEY > 0 ]]; then
        echo "Skip adding $key because it already exists in $HOME/.jupyter/jupyter_notebook_config.py"
        return 1
    fi

    echo "$key = $value" >> ~/.jupyter/jupyter_notebook_config.py
    echo $msg
}


try_append \
    c.NotebookApp.terminado_settings \
    "{'shell_command': ['/bin/bash', '-l']}" \
    "Changed shell to /bin/bash"

try_append \
    c.EnvironmentKernelSpecManager.conda_env_dirs \
    "['/home/ec2-user/anaconda3/envs', '/home/ec2-user/SageMaker/envs']" \
    "Register additional prefixes for conda environments"

echo 'To enforce the change to jupyter config: sudo initctl restart jupyter-server --no-wait'
echo 'then refresh your browser'
