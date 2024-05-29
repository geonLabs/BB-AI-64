# BB-AI-64
BeagleBoneAI-64 ROS_Noetic Docker
![BB-AI-64](http://211.48.125.135:30000/obsidian/BB-AI-64/BB-AI-64_object_distance_measurement.png)

# Beaglebone AI-64 Image install
## Step1. Image Download
I have sd Card so download image sd version
1.  https://rcn-ee.com/rootfs/release/2023-10-07/bullseye-home-assistant-arm64/bbai64-debian-11.8-home-assistant-arm64-2023-10-07-8gb.img.xz <- download image
2.  https://www.balena.io/etcher/ <- download belena
3. If you have a large sd card of 16GB, run the code below.
```
#find the SD card device entry using lsblk (Eg: /dev/sdc)
#use the following commands to expand the filesystem
#Make sure you have write permission to SD card or run the commands as root

#Unmount the BOOT and rootfs partition before using parted tool
umount /dev/sdX1 # This X does not represent X but the location of your sd card.
umount /dev/sdX2

#Use parted tool to resize the rootfs partition to use
#the entire remaining space on the SD card
#You might require sudo permissions to execute these steps
parted -s /dev/sdX resizepart 2 '100%'
e2fsck -f /dev/sdX2
resize2fs /dev/sdX2

#replace /dev/sdX in above commands with SD card device entry
```
