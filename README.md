FileWatch demo example

This project will create a docker container implementing a filewatch service,and then launch it into a local docker instance.

To execute (testing in an Ubuntu virtual box VM)

1) Grab the build_and_run.yaml and inventory from https://github.com/davidkiser/FileWatch/
2) Run the ansible playbook  -  sudo ansible-playbook -b build_and_run.yaml 
3) Access from a local browser
   UI for filewatch service    https://127.0.0.1:5443/   
   Mailcatcher UI to check mail delivery   http://127.0.0.1:1080/  

![Screenshot of app](https://github.com/davidkiser/FileWatch/blob/main/ss/Screenshot%202024-08-22%20125132.png)
![Screenshot of ansible execution](https://github.com/davidkiser/FileWatch/blob/main/ss/Screenshot%202024-08-22%20151659.png)
