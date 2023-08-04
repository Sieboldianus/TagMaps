#!/bin/bash

################################################################################
#
# Shell script to make release
# 1. version and build package
# 2. upload to pypi
# 3. publish to VCS (Github releases)
#
################################################################################

# Exit as soon as a command fails
set -e

semantic-release -v version
twine upload dist/*
semantic-release -v publish