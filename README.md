FileWatch demo example

This project will create a new cloud-init ubuntu Virtual Machine and then inside of it  a docker container implementing a filewatch service. Then it will open a browser to the file upload and mailcatcher web service.  Once done the user can enter y/n to keep or terminate the VM.

To execute on Ubuntu in an on the fly Ubuntu VirtualBox VM
* Requires host machine running ubuntu 2[24].04 with VirtualBox, qemu-utils, whois, cloud-image-utils and wget

1) Clone https://github.com/aunfl0w/FileWatch
2) Run create_vm_deploy.bash 
3) Upload a file in the browser that opens
4) Verify email in other tab

See a video at https://www.youtube.com/watch?v=uA8uWlkjGPQ


## Adapted from
https://github.com/davidkiser/FileWatch/

