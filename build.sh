./clean.sh
python setup.py sdist
twine upload dist/*
pip install --no-cache-dir django-tenant-users --upgrade
