# Contributing

Thank you for taking the time to contribute to this project! 

## For your first contribution

(Make sure you are on the Amazon VPN.)

```
isengard assume # select ml-proserve 
conda create -n <name> python=3.7
conda activate <name>
git clone codecommit::us-east-1://mlmax
pip3 install –r requirements.txt
pre-commit install # to install git hooks in your .git/ directory.
```

## For each contribution

```
git checkout -b <new-branch>
# Make some changes, add/commit them
git push origin <new-branch>
# Go to the console the console to create the PR and merge (delete branch after)
```
