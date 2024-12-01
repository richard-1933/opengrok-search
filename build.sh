#!/bin/zsh

cd /Users/shihxuancheng/Projects/python/opengrok-search

# Build the Python package
python -m build

# Uninstall the existing opengrok-search package and reinstall it from the newly built wheel file
pip uninstall -y opengrok-search && pipenv uninstall opengrok-search && pipenv install dist/*.whl