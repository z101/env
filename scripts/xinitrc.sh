#!/bin/sh

setxkbmap -layout us,ru -variant -option grp:caps_toggle
feh --bg-fill /home/z101/.wp.jpg

#xcompmgr &

while true; do
	/home/z101/.dwmstatus
	sleep 1
done &

#while true; do
	dwm 2> /home/z101/.dwm.log
#done
