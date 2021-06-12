# badge-deployment

The badge deployer will run on a RPIE and auto-deploy bootloader/firmware/app in sequence to a connected badge.

## RPIE config

### udev rule for badge
add the file `/etc/udev/rules.d/10-con.rules` with
```udev
ACTION=="add", SUBSYSTEM=="block", ATTRS{product}=="*Badge*", SYMLINK+="badge", RUN+="/usr/bin/python3 /home/pi/deployer.py $devnode"
ACTION=="add", SUBSYSTEM=="tty", ATTRS{product}=="*Badge*", SYMLINK+="badge_serial"
```

### Avoid auto-mount in rpie

set mount_removable `/etc/xdg/pcmanfm/LXDE-pi/pcmanfm.conf`
```
mount_removable=0
```
#### reload pcmanfm conf:
    killall pcmanfm
    pcmanfm --desktop --profile lubuntu --display :0 &
'''
