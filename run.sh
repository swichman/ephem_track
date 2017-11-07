#!/bin/bash

qt_check="python -c \"import PyQt4\" &>/dev/null"
ephem_check="python -c \"import ephem\" &>/dev/null"
urllib_check="python -c \"import urllib\" &>/dev/null"
count=0

if ! eval $qt_check
then
    echo "PyQT4 module needs to be installed"
    ((count++))
fi

if ! eval $ephem_check
then
    echo "ephem module needs to be installed"
    ((count++))
fi

if ! eval $urllib_check
then
    echo "urllib needs to be installed"
    ((count++))
fi

if [ $count -eq 0 ]
then
    python main.py &
fi

