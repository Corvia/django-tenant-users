rm -rf dist
rm -rf django_tenant_users.egg-info
find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf
