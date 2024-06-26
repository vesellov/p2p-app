#!/bin/bash
SCRIPT_PATH="${BASH_SOURCE[0]}";

if([ -h "${SCRIPT_PATH}" ]) then
  while([ -h "${SCRIPT_PATH}" ]) do SCRIPT_PATH=`readlink "${SCRIPT_PATH}"`; done
fi
SCRIPT_PATH="$(dirname ${SCRIPT_PATH})"

# Get absolute path for SCRIPT_PATH
ABS_SCRIPT_PATH=$(cd "${SCRIPT_PATH}" && pwd)

# activate the virtualenv
pushd "${SCRIPT_PATH}/venv/bin" 1>/dev/null 2>/dev/null
# must be in current directory
source activate

# setup the environment to not mess with the system
export DYLD_FALLBACK_LIBRARY_PATH="${SCRIPT_PATH}/../lib:$DYLD_FALLBACK_LIBRARY_PATH"
export LD_PRELOAD_PATH="${SCRIPT_PATH}/../lib"
BUNDLE_ID=$(osascript -e 'id of app "../../../../"')
# We are not allowed to edit anything within the .app for security reasons.
export KIVY_HOME="~/Library/Application Support/$BUNDLE_ID"
export PYTHONHOME="${ABS_SCRIPT_PATH}/python3"


# if an app is available, use it
if [ -f "${SCRIPT_PATH}/yourapp" ] || [ -h "${SCRIPT_PATH}/yourapp" ]; then
  "${SCRIPT_PATH}/yourapp"
  exit 0
elif [ -d "${SCRIPT_PATH}/yourapp" ]; then
  cd "${SCRIPT_PATH}/yourapp"
  if [ -f "main.so" ]; then
      exec "python" -c "import main"
    exit 1
  fi
    if [ -f "main.pyo" ] || [ -f "main.opt-2.pyc" ]; then
      exec "python" -OO -m main "$@"
      exit 1
    else
      exec "python" -m main "$@"
      exit 1
    fi

# default drag & drop support
elif [ $# -ne 0 ]; then
  exec "python" "$@"

# start a python shell, only if we didn't double-clicked
elif [ "$SHLVL" -gt 1 ]; then
  exec "python"
fi
