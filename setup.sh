#/usr/bin/env bash -e

VENV=PATenv

if [ ! -d "$VENV" ]
then

    PYTHON=`which python3`

    if [ ! -f $PYTHON ]
    then
        echo "could not find python"
    fi
    virtualenv -p $PYTHON $VENV

fi

. $VENV/bin/activate

pip3 install -r requirements.txt

sudo chmod +x /var/lib/snips/skills/PAT/action-app_template.py