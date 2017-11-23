# PiDashCam Installation Instructions

# Hardware

- Raspberry Pi (I used a model 3)
- UPSPico (optional)
- PiCamera
- Adafruit Ultimate GPS
- Two momentary push buttons
- Two LEDs
- Two 10k 1/2 Watt resistors
- Connecting wire
- Case to suit

Connect up hardware as per the diagram

# Base Software Installation
Note: All instructions assume you are using a Mac.
- Start by burning a copy of Raspbian Jessie Lite to an SD card using Etcher (see instructions here)
At completion, you will have the first partition of the SD card mounted as /Volumes/boot/ 1
- In a Terminal session

```
bash$ touch /Volumes/boot\ 1/ssh
bash$ nano /Volumes/boot/wpa_supplicant.conf
network={
    ssid="your WiFi"
    psk="your password"
    key_mgmt=WPA-PSK
}
cmd-S, cmd-X
```
- In Finder, eject the SD card and insert in Pi
- Power up and find IP address of Pi
- Use ssh to log in to the dashcam using the name "pi" and the password "raspberry"
4. immediately change the user password using the command

```
passwd
```

- Use sudo `raspi-config` to
    - change the hostname (e.g. to dashcam)
    - expand the file system (on the Advanced menu)
    - enable Camera and I2C (on the Interfaces menu)

# Update the distribution
```
sudo apt-get update
sudo apt-get dist-upgrade
```
# Install and configure the UPS PIco Software (if used)

Follow the installation guide for the UPSPIco to install its software and configure it appropriately.
- Install the daemons
- Enable the RTC
- Update firmware (if needed)
## Install the daemons
```
sudo apt-get install git python-rpi.gpio python-dev python-serial python-smbus python-jinja2 python-xmltodict python-psutil python-pip
```
(Take note of the line-wrapping above, it should all be on one line)

```
sudo git clone  https://github.com/modmypi/PiModules
cd PiModules/code/python/package
sudo python setup.py install
cd ../upspico/picofssd
sudo python setup.py install
sudo systemctl enable picofssd.service
sudo systemctl start picofssd.service
```
## install the RTC
1. install the i2c tools
```
sudo apt-get -y install i2c-tools
```
1. edit the following file
```
sudo nano /etc/modules
```
ensure the following items are in the file
```
i2c-bcm2708
12c-dev
rtc-ds1307
```

1. Edit the boot config file
```
sudo nano /boot/config.txt
```
and add the following:
```
enable_uart=1
dtoverlay=i2c-rtc,ds1307
```
1. edit the rc.local file
```
sudo nano /etc/rc.local
```
and add the following before `exit 0`
```
sleep 4; hwclock -s&
```
1. reboot the system
```
sudo reboot
```
1. remove the `fake-hwclock` which interferes with the RTC `hwclock`
```
sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
```
1. run
```
sudo nano /lib/udev/hwclock-set
```
and comment out these three lines
```
#if [ -e /run/systemd/system]; then
#exit 0
#fi
```
1. run `date` to verify the time is correct
1. run
```
sudo hwclock -w
sudo hwclock -r
```

# Install and configure the GPS

I use the gpsd system daemon to connect to the GPS on the Pi's serial port. Out of the box, the Pi uses the built-in serial port as a console, so this does need to be disabled. Proceed as follows (this for the Pi 3 only)
1. edit `/boot/cmdline.txt` to remove references to the serial console
```
sudo nano /boot/cmdline.txt
```
remove any references to `console=serial0,115200`, `console=ttyAMA0,115200`, `console=serial0,115200` or `kbdboc=ttyAMA0,115200`

1. Stop bluetooth using the serial port (Pi3 only). Edi the file /boot/config.txt
```sudo nano /boot/config.txt
```
and add the following:
```
dtoverlay=pi3-disable-bt
```
1. run
```
sudo systemctl disable hciuart
sudo systemctl stop hciuart
```

1. install the daemon and client packages
```
bash$ sudo apt update
bash$ sudo apt install gpsd gpsd-clients python-gps
```
1. Edit the file /etc/gps/gpsd
```
sudo nano /etc/default/gpsd
```
and replace the line
```
DEVICES=""
```
with
```
DEVICES=/dev/ttyAMA0"
```
and the line
```
GPSD_OPTIONS=""
```
with
```
GPSD_OPTIONS="-F /var/run/gpsd.sock"
```
1. Reboot, and it should all work. If you have the GPS connected correctly and it has a lock, then you should get real-time status by running the commend.
```
cgps -s
```

# Install PiDashCam
1. install the python libraries
```
$ sudo apt install python python-picamera python-gps python-rpi.gpio python-pip
$ sudo pip install keyboard
```
2. clone the git package from github
```
$ git clone https://www/github.com/garethhowell/pidashcam
```
# Run PiDashCam
I recommend that you do this "on the bench" to begin with until you are sure everything is working.
```
cd PiDashCam/Code
$ sudo python pidashcam.py
```
# Install Resilio Sync
Resilio Sync is a personal P2P environment that uses the BitTorrent protocol. It's very similar in concept to Dropbox or OneDrive but the files stay totally within your control: there's no cloud element. More details on
I use resilio sync to move the videos from the Pi to a Mac in the house.
1. Install the resilio sync package on your PC or Mac using the intructions on (https://www.resilio.com/)
2. Create a folder on the Mac that will contain the videos and set it up in Resilio Sync to sync.
3. Install the package on the Pi
```
echo "deb http://linux-packages.resilio.com/resilio-sync/deb resilio-sync non-free" | sudo tee /etc/apt/sources.list.d/resilio-sync.list
wget -qO - https://linux-packages.resilio.com/resilio-sync/key.asc | sudo apt-key add -
curl -LO https://linux-packages.resilio.com/resilio-sync/key.asc && sudo apt-key add ./key.asc
sudo dpkg --add-architecture armhf
sudo apt-get update
```
In `/etc/apt/sources.list` change the line as follows:
```
deb [arch=armhf] http://linux-packages.resilio.com/resilio-sync/deb resilio-sync non-free
```
1. Install the package
```
sudo apt-get update
sudo apt-get install resilio-sync
```
2. Enable the package
```
sudo systemctl enable resilio-sync
sudo systemctl start resilio-sync
```
You should now be able to open `http://<ip address>:8888` and see the resilio admin interface
3. Create the sync connection
- On the PC/Mac, create a sync folder to receive the Videos and use the Resilio client to make it one and of a sync connection.
- copy the Sync key for the folder
- In the web browser, create
