#!/bin/bash
vdisk="/dev/vdb /dev/vdc"
vpart="/dev/vdb1 /dev/vdc1"
for i in $vdisk;
do
echo "n
p
1


w
"|sudo fdisk $i;
done
for j in $vpart;
do
#sleep 2s
echo "y
"|sudo mkfs.ext4 $j;
done
sudo mkdir /data
sudo mount /dev/vdc1 /data
echo "/dev/vdc1        /data    auto    defaults,nofail     0       2" | sudo tee -a /etc/fstab
