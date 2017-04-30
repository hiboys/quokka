#!/bin/bash
ansible-playbook ./prod/deploy.yml --private-key=\
./prod/ssh_keys/192.168.0.100_prod_key -u deployer -i ./prod/hosts --tags "git"
