#!/usr/bin/env sh

set -o errexit
set -o nounset

# Initializing global variables and functions:
: "${DJANGO_ENV:=development}"

pyclean () {
  # Cleaning cache:
  find . \
  | grep -E '(__pycache__|\.hypothesis|\.perm|\.cache|\.static|\.py[cod]$)' \
  | xargs rm -rf
}

run_ci () {
  echo '[ci started]'
  set -x  # we want to print commands during the CI process.

  # Running tests:
  pytest --dead-fixtures
  pytest

  set +x
  echo '[ci finished]'
}

# Remove any cache before the script:
pyclean

# Clean everything up:
trap pyclean EXIT INT TERM

# Run the CI process:
run_ci
