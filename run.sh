#!/bin/bash

qt_check="python -c \"import PyQt4\" &>/dev/null"
ephem_check="python -c \"import ephem\" &>/dev/null"
urllib_check="python -c \"import urllib\" &>/dev/null"
pathlib_check="python -c \"import pathlib\" &>/dev/null"
numpy_check="python -c \"import numpy\" &>/dev/null"
pyqtgraph_check="python -c \"import pyqtgraph\" &>/dev/null"
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

if ! eval $pathlib_check
then
    echo "pathlib needs to be installed"
    ((count++))
fi

if ! eval $numpy_check
then
    echo "numpy needs to be installed"
    ((count++))
fi

if ! eval $pyqtgraph_check
then
    echo "pyqtgraph needs to be installed"
    ((count++))
fi


if [ $count -eq 0 ]
then
    python ephem_track.py &
fi

