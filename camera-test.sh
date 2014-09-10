#!/bin/bash

MPLAYER=mplayer2
INVENTORY=../../sr/git/inventory

if [ "$1" == "" ]; then
  echo "Please pass the video device webcams appear at as an argument."
  exit
fi

marker_info=

while true; do
  count=0
  condition=working
  while [ "$marker_info" = "" ]; do
    rm *.png # clean up

    "$MPLAYER" -vo png -frames 5 tv:// -tv device="$1"

    rm 0000000{1,2,3,4}.png

    marker_info="$(./marker_info 00000005.png)"
    let count++
    if [ "$count" = 10 ]; then
      echo "Ten tries and no markers, this one is probably broken."
      condition=broken
      break
    fi
  done

  if [ "$count" != 10 ]; then
    echo "$marker_info"
    display 00000005.png
    read -p "OK? (y/N)" ok
    if [ "${ok:0:1}" != "y" ] && [ "${ok:0:1}" != "Y" ]; then
      condition=broken
    fi
  fi
  ./inventory-checker.py "$1" "$INVENTORY" "$condition"
  echo "PLEASE REMOVE WEBCAM"
  while [ -e "$1" ]; do
    sleep 0.1
  done
  echo "PLEASE INSERT NEXT WEBCAM"
  while ! [ -e "$1" ]; do
    sleep 0.1
  done

done
