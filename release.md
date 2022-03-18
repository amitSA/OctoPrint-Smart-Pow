### Release Process
rm -r dist/ # maybe this is ooptional ?

python setup.py sdist

twine upload dist/*
