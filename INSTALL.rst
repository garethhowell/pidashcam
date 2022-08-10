PiDashCam Installation Instructions
===================================

Hardware
========

*  Raspberry Pi (I used a model 3)
*  UPSPico (optional)
*  PiCamera
*  Adafruit Ultimate GPS
*  Two momentary push buttons
*  One LED
*  One 1k 1/2 Watt resistor
*  Connecting wire
*  Case to suit

Connect up hardware as per the diagram

Base Software Installation
==========================

Note: All instructions assume you are using a Mac. 1. Start by burning a
copy of Raspbian Jessie Lite to an SD card using Etcher (see
instructions here) At completion, you will have the first partition of
the SD card mounted as /Volumes/boot/ 1 1. In a Terminal session::

    $ touch /Volumes/boot\ 1/ssh

Create the file ``/Volumes/boot/wpa_supplicant.conf`` with the contents::

    network={
        ssid="your WiFi"
        psk="your password"
        key_mgmt=WPA-PSK
    }

1. In Finder, eject the SD card and insert in Pi
2. Power up and find IP address of Pi
3. Use ssh to log in to the dashcam using the name “pi” and the password
   “raspberry”
4. immediately change the user password using the command ``passwd``

5. Use ``sudo raspi-config`` to

   -  change the hostname (e.g. to dashcam)
   -  expand the file system (on the Advanced menu)
   -  enable Camera and I2C (on the Interfaces menu)

6. Update the distribution with::

    sudo apt-get update && sudo apt-get dist-upgrade

7. Reboot

Install and configure the UPS PIco Software (if used)
=====================================================

Follow *`the installation guide for the
UPSPIco <https://github.com/modmypi/PiModules/wiki/UPS-PIco-Installation>`__*
to install its software and configure it appropriately.

Install and configure the GPS
=============================

I use the gpsd system daemon to connect to the GPS on the Pi’s serial
port. Out of the box, the Pi uses the built-in serial port as a console,
so this does need to be disabled. Proceed as follows (this for the Pi 3
only)

1. edit ``/boot/cmdline.txt`` to remove references to the serial console.
  Remove any references to

    ``console=serial0,115200``,

    ``console=ttyAMA0,115200``,

    ``console=serial0,115200`` or

    ``kbdboc=ttyAMA0,115200``

2. Stop bluetooth using the serial port (Pi3 only). Edit the file
   ``/boot/config.txt`` and add the following::

       dtoverlay=pi3-disable-bt

3. run::

   $ sudo systemctl disable hciuart
   $ sudo systemctl stop hciuart

3. install the daemon and client packages::

   $ sudo apt update
   $ sudo apt install gpsd gpsd-clients python-gps

4. Edit the file ``/etc/gps/gpsd`` and replace the line

    ``DEVICES=""`` with

    ``DEVICES=/dev/ttyAMA0"`` and the line

    ``GPSD_OPTIONS=""`` with

    ``GPSD_OPTIONS="-F /var/run/gpsd.sock"``
5. Reboot, and it should all work. If you have the GPS connected
   correctly and it has a lock, then you should get real-time status by
   running the command ``cgps -s``

Install PiDashCam
=================

1. install the required python libraries::

    $ sudo apt install python python-picamera python-gps python-rpi.gpio python-pip
    $ sudo pip install keyboard

2. clone the git package from github::

    $ git clone https://www/github.com/garethhowell/pidashcam
3. Install the package::

     $ cd PiDashCam/code/scripts
     $ sudo pip install .

Run PiDashCam
=============

I recommend that you run pidashcam in the foreground to begin
with until you are sure everything is working.

1. To see the options::

     $ sudo /usr/local/bin/pi-dashcam -h

Most options have sensible defaults.

2. To run in the foreground::

     $ sudo /usr/local/sbin/pidashcam <options>

Log entries go to STDOUT

3. All configuration variables can be set in ``/etc/default/pidashcam``.

   This file is only used when ``pidashcam`` is running under ``systemd``

4. When you are happy::

     $ sudo systemctl enable pidashcam.service
     $ sudo systemctl start pidashcam

pidashcam will start automatically at boot.

5. You can view log files with::

     $ sudo journalctl -u pidashcam

6. You can stop pidashcam with::

     $ sudo systemctl stop pidashcam

Install Resilio Sync
====================

Resilio Sync is a personal P2P environment that uses the BitTorrent protocol.
It’s very similar in concept to Dropbox or OneDrive
but the files stay totally within your control:
there’s no cloud element.

More details on how I use resilio sync to move the videos from the Pi to a Mac in the house.

1. Before following the install guide linked to in the next step, you
   need to install a module that is missing from the jessie-lite
   distribution. If you don’t, you won’t be able to run resilio-sync in
   user mode.::

   $ sudo apt-get install libpam-systemd

2. Install the resilio sync package on your PC or Mac using the
   instructions on *`the Resilio Sync
   website <https://help.resilio.com/hc/en-us/articles/206178924-Installing-Sync-package-on-Linux>`__*.
   Remember to follow the instructions to run resilio-sync in user mode
   so you can sync folders in your home directory.

   Before you run ``systemctl --user enable resilio-sync``, proceed as
   follows:

   edit ``/etc/resilio-sync/user_config.json`` and change the line:

   ``"listen" : "127.0.0.1:8888"`` to read

   ``"listen" : "0.0.0.0:8889"`` and then run::

      $ systemctl --user enable resilio-sync
      $ systemctl --user start resilio-sync

6. Open http:<ip-address>:8889 You will need to create an admin user
   login.
7. Create the sync connection

   -  On the Mac, create a sync folder to receive the Videos and use the
      Resilio client to make it one and of a sync connection.
   -  copy the Sync key for the folder
   -  In the web browser, create the equivalent sync connection so that
      the folder ``/home/pi/PiDashCam/Videos`` syncs with your Mac.
