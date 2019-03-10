#!/bin/sh
set -e
# This entrypoint script:
#
# - Executes *inside* of the container upon start as --user [default root]
# - Notice that the container *starts* as --user [default root] but
#   *runs* as non-root user [scu]
#
echo "Entrypoint for stage ${SC_BUILD_TARGET} ..."
echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"



# expect input/output/log folders to be mounted
stat $INPUT_FOLDER &> /dev/null || \
        (echo "ERROR: You must mount '$INPUT_FOLDER' to deduce user and group ids" && exit 1) # FIXME: exit does not stop script
stat $OUTPUT_FOLDER &> /dev/null || \
    (echo "ERROR: You must mount '$OUTPUT_FOLDER' to deduce user and group ids" && exit 1) # FIXME: exit does not stop script
stat $LOG_FOLDER &> /dev/null || \
    (echo "ERROR: You must mount '$LOG_FOLDER' to deduce user and group ids" && exit 1) # FIXME: exit does not stop script

stat $INPUT_FOLDER &> /dev/null
if [[ $? -eq 0 ]]
then
    # NOTE: expects docker run ... -v /path/to/input/folder:$INPUT_FOLDER
    USERID=$(stat -c %u $INPUT_FOLDER)
    GROUPID=$(stat -c %g $INPUT_FOLDER)
    GROUPNAME=$(getent group ${GROUPID} | cut -d: -f1)

    if [[ $USERID -eq 0 ]]
    then
        addgroup scu root
    else
        # take host's credentials in myu
        if [[ -z "$GROUPNAME" ]]
        then
            GROUPNAME=myu
            addgroup -g $GROUPID $GROUPNAME
            # change group property of files already around
            find / -group 8004 -exec chgrp -h $GROUPNAME {} \;
        else
            addgroup scu $GROUPNAME
        fi

        deluser scu &> /dev/null
        adduser -u $USERID -G $GROUPNAME -D -s /bin/sh scu
        # change user property of files already around
        find / -user 8004 -exec chown -h scu {} \;
    fi
fi



{# TODO: Add option to add access to docker sockets or not #}
# Appends docker group if socket is mounted
DOCKER_MOUNT=/var/run/docker.sock

if [[ -e $DOCKER_MOUNT && stat $DOCKER_MOUNT &> /dev/null && $? -eq 0 ]]
then
    GROUPID=$(stat -c %g $DOCKER_MOUNT)
    {# sometimes the group docker already exists for some reason, so let's create one that has less chances of existing  #}
    GROUPNAME=scdocker

    addgroup -g $GROUPID $GROUPNAME &> /dev/null
    if [[ $? -gt 0 ]]
    then
        # if group already exists in container, then reuse name
        GROUPNAME=$(getent group ${GROUPID} | cut -d: -f1)
    fi
    addgroup scu $GROUPNAME
fi

echo "Starting $@ ..."
su-exec scu "$@"
