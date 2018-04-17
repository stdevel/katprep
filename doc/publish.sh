#!/bin/sh
make html && mv build/html/ ../docs
cp .nojekyll _config.yml ../docs
rm -Rf build
