#!/bin/bash

read -p "Install debian package? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo dpkg -i ~/dev/python3-craftisan*.deb
fi

read -p "Install icons? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    dir="$HOME/dev/craftisan/img"
    sudo cp $dir/craftisan.png /usr/share/linuxcnc
    sudo cp -r $dir/Craftisan /usr/share/icons
fi

read -p "Install configuration file in home dir? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    dir="$HOME/dev/craftisan"
    dest=$HOME/.craftisan.ini
    sudo cp $dir/craftisan.ini $dest
fi