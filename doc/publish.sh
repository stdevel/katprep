#!/bin/sh
rm -Rf ../docs
make html && mv build/html ../docs
cp .nojekyll ../docs
rm -Rf build
