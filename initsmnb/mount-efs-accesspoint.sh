#!/bin/bash

# Prerequisite:
# - EFS access point has been configured.
# - Notebook has to be in the same VPC as EFS. EFS access point will handle the owner/permission.

echo Mount EFS access point onto Sagemaker home directory
echo Usage: ${BASH_SOURCE[0]} "efs_file_id,efs_accesspoint_id,mount_path ..."
echo "       where mount_path is always under /home/ec2-user/mnt/"
echo

# Install efs utitlity
sudo yum install -y amazon-efs-utils

# For complete list of mount options, see:
# - https://docs.aws.amazon.com/efs/latest/ug/mount-fs-auto-mount-onreboot.html
# - https://docs.aws.amazon.com/efs/latest/ug/mounting-fs-mount-cmd-general.html
EFS_OPTS='defaults,nofail,_netdev,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport'

mount_efs(){
    local EFS_FILE_ID="$1"
    local EFS_ACCESSPOINT_ID="$2"
    local MOUNT_POINT="/home/ec2-user/mnt/$3"

    if [[ ${EFS_FILE_ID} == "" ]] || [[ ${EFS_ACCESSPOINT_ID} == "" ]] || [[ ${MOUNT_POINT} == "" ]]; then
        echo "Error: Missing arguments"
        exit 1
    fi

    echo "EFS_FILE_ID:" ${EFS_FILE_ID}
    echo "EFS_ACCESSPOINT_ID:" ${EFS_ACCESSPOINT_ID}
    echo "MOUNT_POINT:" ${MOUNT_POINT}
    echo

    mkdir -p ${MOUNT_POINT}
    sudo mount -t efs -o "$EFS_OPTS,tls,accesspoint=${EFS_ACCESSPOINT_ID}" ${EFS_FILE_ID}: ${MOUNT_POINT} --verbose
}

for mnt_spec in "$@"; do
    mount_efs $(echo ${mnt_spec} | tr , ' ')
done

echo "Done"
