#!/bin/bash

set -e

# update local apt sources and pip yes, default yes!
fab local_update_apt_pip

# update cluster node apt sources and pip config, default yes!
fab update_apt_pip