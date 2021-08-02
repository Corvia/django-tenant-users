import nox
from nox_poetry import session

# Nox configuration
nox.options.reuse_existing_virtualenvs = True

PYTHON_VERSIONS = ('3.6', '3.7', '3.8', '3.9')
DJANGO_VERSIONS = ('2.2', '3.1', '3.2')


def poetry_install(session, package) -> None:
    """Helper method to install dependency packages."""
    session.run(
        'poetry',
        'run',
        'pip',
        'install',
        '--upgrade',
        package,
        external=True,
    )


@session()
def clean(session):
    """Clean session at start."""
    session.run_always('coverage', 'erase', external=True)


@session(python=PYTHON_VERSIONS)
@nox.parametrize('django', DJANGO_VERSIONS)
def test_django_tenants(session, django):
    """Run tests with django-tentants."""
    session.run_always('poetry', 'install', external=True)
    poetry_install(session, 'pip')
    poetry_install(session, 'django~={0}'.format(django))
    poetry_install(session, 'django-tenants')
    session.run(
        'poetry',
        'run',
        'pytest',
        '--ds=test_django_tenants.test_django_tenants.settings',
        '--ignore=test_tenant_schemas',
        external=True,
    )


@session(python=PYTHON_VERSIONS)
@nox.parametrize('django', '2.2')
def test_django_tenant_schemas(session, django):
    """Run tests with django-tentants."""
    session.run_always('poetry', 'install', external=True)
    poetry_install(session, 'pip')
    poetry_install(session, 'django~={0}'.format(django))
    poetry_install(session, 'django-tenant-schemas')
    session.run(
        'poetry',
        'run',
        'pytest',
        '--ds=test_tenant_schemas.test_tenant_schemas.settings',
        '--ignore=test_django_tenants',
        external=True,
    )


@session()
def coverage_report(session):
    """Run coverage reporting."""
    session.run_always('coverage', 'report', '--fail-under=75', external=True)
