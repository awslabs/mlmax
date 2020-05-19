# mlmax-python

Add a short description here!


## Description

A longer description of your project goes here...

## Installation
```bash
cd mlmax
```
### Data Version Control
```bash
# https://dvc.org/
pip install dvc
# opt out dvc analytics
dvc config core.analytics false
# sync data from remote s3://mlmax-data-repo
# make sure your aws-cli has permission to access
dvc pull
```

### Pre-commit
```bash
# it is a good idea to create and activate a virtualenv here
pip install pre-commit
pre-commit install
# another good idea is update the hooks to the latest version
pre-commit autoupdate
pre-commit run --all-files
```

### mlmax
```bash
pip install -e .
```
### Documentation
```bash
python setup.py docs
```
### Unit Testing
```bash
python setup.py test
```

### Build Distribution
```bash
# source
python setup.py sdist
# binary
python setup.py bdist
# wheel (recommended)
python setup.py bdist_wheel
```


## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.

```bash
putup mlmax-python -p mlmax -l apache --markdown --dsproject --pre-commit
```
