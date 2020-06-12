#!/bin/bash
#
# Execute as root: ./install_requirements.sh
#
apt update
apt install python3
apt install python3-pip
python3 -m pip install --upgrade pip
python3 -m pip install -U scikit-learn
python -m pip show scikit-learn
python -m pip freeze
python -c "import sklearn; sklearn.show_versions()"

mkdir treeData
mkdir treeModels
mkdir garden

# create random datasets
python create_dataset.py

# create a sample of trees
python dfedForest.py
