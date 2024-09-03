FileWatch demo example

This project will create a new cloud-init ubuntu Virtual Machine and then inside of it  a docker container implementing a filewatch service. Then it will open a browser to the file upload and mailcatcher web service.  Once done the user can enter y/n to keep or terminate the VM.

To execute on Ubuntu in an on the fly Ubuntu VirtualBox VM
* Requires host machine running ubuntu 2[24].04 with VirtualBox, qemu-utils, whois, cloud-image-utils and wget

1) Clone https://github.com/aunfl0w/FileWatch
2) Run create_vm_deploy.bash 
3) upload a file in the browser that opens

## Adapted from
https://github.com/davidkiser/FileWatch/

