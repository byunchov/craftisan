#!/bin/bash

read -p "Install build deps? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo apt install dpkg-dev devscripts build-essential lintian dh-python python3-build pybuild-plugin-pyproject python3-poetry
fi

changelog=$HOME/dev/craftisan/debian/changelog
version=$(grep "\bversion\b" pyproject.toml | grep -Po '\d+\.\d+\.\d+')
if [ -f "$file" ] ; then
    dch -a --distribution unstable --package craftisan --newversion $version Development Release.
else
    dch --create --distribution unstable --package craftisan --newversion $version Development Release.
fi

# dpkg-buildpackage -b -uc
debuild -ePATH  -b -uc -us

read -p "Install built package? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo dpkg -i ~/dev/python3-craftisan*.deb
fi
