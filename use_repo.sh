# This script should be sourced before using this repo (for development).
# It creates the python virtualenv and using pip to populate it
# This only run to setup the development environment.
# Installation is handled by setup.py/disttools.

# Robust way of locating script folder
# from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
SOURCE=${BASH_SOURCE:-$0}

DIR="$( dirname "$SOURCE" )"
while [ -h "$SOURCE" ]
do 
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
  DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd )"
done
WDIR="$( pwd )"
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"


if type python27 > /dev/null 2>/dev/null ; then
    PYTHONEXEC=python27
else
    PYTHONEXEC=python
fi

# create virtualenv
VENV=$DIR/venv
if [ -d VENV ]; then
   # Virtual Env exists
   echo vitual environment $VENV exist
else
    virtualenv $VENV --python=$PYTHONEXEC --prompt "(d_py_sandbox)"
fi

source $VENV/bin/activate

# install robustus into virtualenv
pip install -U git+http://github.com/braincorp/robustus.git

# create folder for packages compilation cache
mkdir -p ~/.robustus_rc/wheelhouse

# initialize robustus venv with cache path 
robustus --cache ~/.robustus_rc/wheelhouse env $VENV

# install this folder in developer mode
echo "Running robustus with options '$ROBUSTUS_OPTIONS'"
robustus install -e . $ROBUSTUS_OPTIONS

# If you can not compile opencv on mac, there is a workaround to use brew opencv
# brew tap homebrew/science
# brew install opencv
# cp /usr/local/lib/python2.7/site-packages/cv* venv/lib/python2.7/site-packages/

