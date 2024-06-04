#####################################
 Contributing to Django Tenant Users
#####################################

Thank you for considering contributing to Django Tenant Users! This
document outlines some guidelines to follow when contributing to the
project.

*****************
 Code of Conduct
*****************

We are committed to fostering a welcoming and inclusive community.

*****************
 Getting Started
*****************

#. Fork the repository on GitHub.

#. Clone your forked repository to your local machine:

   .. code:: bash

      git clone https://github.com/your-username/django-tenant-users.git

#. Install Poetry if you haven't already:

   .. code:: bash

      pip install poetry

#. Install the project dependencies using Poetry:

   .. code:: bash

      poetry install

****************
 Making Changes
****************

#. Checkout a new branch for your feature/bugfix:

   .. code:: bash

      git checkout -b feature/your-feature-name

#. Make your changes and ensure that the code passes all tests:

   .. code:: bash

      poetry run pytest

#. Format the code using black and isort. It's important to run isort
   first and then black:

   .. code:: bash

      pip install isort black

      isort .
      black .

#. Format the documentation using rstfmt:

   .. code:: bash

      pip install rstfmt

      poetry run rstfmt docs

#. Commit your changes with a descriptive commit message:

   .. code:: bash

      git commit -am "Add feature: Your feature description"

#. Push your branch to your forked repository:

   .. code:: bash

      git push origin feature/your-feature-name

#. Open a pull request on GitHub. Please provide a clear description of
   the changes you've made.

************
 Code Style
************

We follow the PEP 8 style guide for Python code. Please ensure that your
code adheres to these guidelines.

***************
 Documentation
***************

If you're adding a new feature, please update the documentation
accordingly. Documentation changes should be made in the `docs/`
directory.

*******
 Tests
*******

Ensure that your code has appropriate test coverage. Write tests for new
features and ensure that existing tests pass.

***********************
 Questions and Support
***********************

If you have questions or need support, feel free to open an issue on
GitHub.

Thank you for contributing to Django Tenant Users!
