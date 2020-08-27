#!/bin/bash

echo "Change ipython color scheme on something.__class__ from dark blue (nearly invisible) to a more sane color."

mkdir -p /home/ec2-user/.ipython/profile_default/

cat << EOF >> /home/ec2-user/.ipython/profile_default/ipython_config.py
c.TerminalInteractiveShell.highlight_matching_brackets = True

from pygments.token import Name

c.TerminalInteractiveShell.highlighting_style_overrides = {
    Name.Variable: "#B8860B",
}
EOF


echo "Add ipython keybindings when connecting from OSX"
IPYTHON_STARTUP_DIR=.ipython/profile_default/startup
IPYTHON_STARTUP_CFG=${IPYTHON_STARTUP_DIR}/01-osx-jupyterlab-keys.py
[[ ! -f /home/ec2-user/SageMaker/${IPYTHON_STARTUP_CFG} ]] && \
    curl --create-dirs -sfL \
        -o /home/ec2-user/SageMaker/${IPYTHON_STARTUP_CFG} \
        https://raw.githubusercontent.com/verdimrc/linuxcfg/master/${IPYTHON_STARTUP_CFG}
mkdir -p /home/ec2-user/${IPYTHON_STARTUP_DIR}
ln -s \
    /home/ec2-user/SageMaker/${IPYTHON_STARTUP_CFG} \
    /home/ec2-user/${IPYTHON_STARTUP_CFG}
