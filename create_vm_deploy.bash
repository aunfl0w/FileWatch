#!/bin/bash
passin=password
echo This script requires requires virtualbox, qemu-utils, whois, cloud-image-utils, wget
echo If you are running kvm see the notes in this script on how to unload kvm modules

## unloaded kvm so virtualbox can load
#sudo modprobe -r kvm_amd kvm_intel
#sudo service virtualbox stop
#sudo service virtualbox start

# see https://cloud-images.ubuntu.com/releases/ for versions
ubuntuversion="24.04"
imagetype="img"
releases_url="https://cloud-images.ubuntu.com/releases/${ubuntuversion}/release/"
img_url="${releases_url}/ubuntu-${ubuntuversion}-server-cloudimg-amd64.${imagetype}"

## download a cloud image to run, and convert it to virtualbox 'vdi' format
# and resize
#
img_dist="${img_url##*/}"
img_raw="${img_dist%.img}.raw"
my_disk1="ubuntu-${ubuntuversion}-cloud-virtualbox.vdi"

if [[ ! -e tmp/ ]]
then 
	mkdir tmp/
fi
pushd tmp
if [[ ! -e "$img_dist" ]]
then
	wget $img_url -O "$img_dist"
fi

if [[ ! -e "$img_raw" ]]
then
	qemu-img convert -O raw "${img_dist}" "${img_raw}"
fi

vboxmanage convertfromraw "$img_raw" "$my_disk1"
VBoxManage modifyhd "$my_disk1" --resize $((1024*10))

## Name the iso file for the cloud-config data
seed_iso="my-seed.iso"

## create meta-data file 
cat > meta-data <<EOF
instance-id: filewatch
local-hostname: filewatch
EOF

## Generate a hashed password for the /etc/passwd file
password=$(echo $passin | mkpasswd -m sha-512 -s)
ssh-keygen -f filewatch -t ed25519 -C filewatch@filewatch <<< y
ssh_pub_key=$(cat filewatch.pub)


## create user-data file 
seed_iso="my-seed.iso"
cat > user-data <<EOF
#cloud-config

timezone: America/New_York
locale: en_US.UTF-8

users:
  - name: filewatch
    gecos: filewatch
    shell: /bin/bash
    lock_passwd: false
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - $ssh_pub_key

EOF


## create cloud-init config iso
cloud-localds "$seed_iso" user-data meta-data

## create a virtual machine using vboxmanage
#

vmname="filewatch-${ubuntuversion}-1"

vboxmanage createvm --name "$vmname" --register

vboxmanage modifyvm "$vmname" --nested-hw-virt on \
	--cpus 2

vboxmanage modifyvm "$vmname" --recording on \
       	--recording-file filewatch.webm \
	--recording-max-time=60 \
       	--recording-video-fps=15

vboxmanage modifyvm "$vmname" \
   --memory 1024 --boot1 disk --acpi on \
   --nic1 nat \
   --nat-pf1 "ssh,tcp,,2222,,22" \
   --nat-pf1 "app,tcp,,5443,,5443" \
   --mac-address1=0800277CA4F6




# Add storage controlers
vboxmanage storagectl "$vmname" --name "SATA"  --add sata --controller IntelAhci --portcount 5
vboxmanage storagectl "$vmname" --name "IDE"  --add ide --controller PIIX4

# Add root disk and iso
vboxmanage storageattach "$vmname" --storagectl "SATA" --port 0 --device 0 --type hdd --medium $my_disk1
vboxmanage storageattach "$vmname" --storagectl "IDE" --port 1 --device 0 --type dvddrive --medium $seed_iso
vboxmanage modifyvm "$vmname" --boot1 disk --boot2 dvd --boot3 none --boot4 none

## start up the VM 
vboxmanage startvm "$vmname" --type headless
ssh-keygen -f ~/.ssh/known_hosts -R '[localhost]:2222' &>/dev/null

echo Waiting for VM to be ready
while true
do
	name=$(ssh  -o StrictHostKeyChecking=no filewatch@localhost -p 2222 -i filewatch "hostname" 2>/dev/null)
	[[ $name == "filewatch" ]] && break
	sleep 1
	echo checking again...
done	
sleep 2

#port forward mailcatcher with ssh 
ssh  -o StrictHostKeyChecking=no filewatch@localhost -p 2222 -i ./filewatch -L 127.0.0.1:1080:127.0.0.1:1080 -N &

popd
echo Deploying application in $vmname
echo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
ansible-playbook -v build_and_run.yaml -i inventory.cloud-init

xdg-open https://127.0.0.1:5443/  2>/dev/null
xdg-open http://127.0.0.1:1080/ 2>/dev/null 

pushd tmp


echo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
echo login with "ssh  -o StrictHostKeyChecking=no filewatch@localhost -p 2222 -i ./tmp/filewatch"
echo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 

while true; do
    read -p "Do you want to delete the $vmname vm: [y/n] " yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) popd; exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

vboxmanage controlvm "$vmname" poweroff

# just wait a while for vm to stop
sleep 10

## cleanup
vboxmanage storageattach "$vmname" \
   --storagectl "SATA" --port 0 --device 0 --medium none
vboxmanage storageattach "$vmname" \
   --storagectl "IDE" --port 1 --device 0 --medium none
vboxmanage closemedium dvd "${seed_iso}"
vboxmanage closemedium disk "${my_disk1}"
vboxmanage unregistervm $vmname --delete
popd

echo 
echo remove tmp/ to cleanup cached files
