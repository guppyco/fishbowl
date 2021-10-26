#! /bin/bash

LOGFILE="/webapps/guppy/logs/runjobs.log"
LOGDIR=$(dirname $LOGFILE)
# shellcheck disable=SC1091
source /webapps/guppy/bin/activate
# shellcheck disable=SC1091
source /webapps/guppy/bin/postactivate

# Setup Sentry logging via https://blog.sentry.io/2017/11/28/sentry-bash
[ -z "$SENTRY_DSN" ] && echo "SENTRY_DSN must be set." && exit 1
eval "$(/usr/local/bin/sentry-cli bash-hook)"

cd /webapps/guppy || exit 1
test -d "$LOGDIR" || mkdir -p "$LOGDIR"

# Sends stderr and stdout to logfile, appending if logfile exists.
# See https://unix.stackexchange.com/a/159514/129503
# for logging operators.
python /webapps/guppy/guppy/manage.py runjobs "$1" >> $LOGFILE 2>&1
