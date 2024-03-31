#!/bin/bash

update_venv(){
  cwd=$(pwd)
  cd $1
  rm -rf .venv
  poetry env use 3.11
  poetry lock && poetry install
  cd $cwd
}

# the order is important
update_venv lib/py_dev_dependencies
update_venv lib/py_edge_interface
update_venv lib/py_edge_device
update_venv lib/py_edge_server
update_venv lib/py_monorepo_manager
update_venv services/api
update_venv services/device
