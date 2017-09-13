
# -*- coding: utf-8 -*-

"""A Fabric fabfile with functionality to prepare, install, and configure
UnichainDB, including its storage backend (RethinkDB).
"""


from __future__ import with_statement, unicode_literals
import os
from os import environ  # a mapping (like a dict)
import sys

import time
import datetime
import json

from fabric.colors import red, green, blue, yellow, magenta, cyan
from fabric.api import sudo, cd, env, hosts, local, runs_once
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put, get, prompt
from fabric.context_managers import settings, hide

from configparser import ConfigParser

from hostlist import public_dns_names,public_hosts,public_pwds,public_host_pwds, public_usernames

################################ Fabric Initial Config Data  ######################################

env['passwords'] = public_host_pwds
env['hosts']=env['passwords'].keys()

from multi_apps_conf import app_config

_server_port = app_config['server_port']
_restore_server_port = app_config['restore_server_port']
_service_name = app_config['service_name']
_setup_name = app_config['setup_name']


conf = ConfigParser()
cluster_info_filename = "../conf/cluster_info.ini"
conf.read(cluster_info_filename, encoding="utf-8")

# 1.3. pip 更新开关
pip_sources_switch = conf.get("on-off", "pip-sources", fallback="off")
pip_sources_boolean = conf.getboolean("on-off", "pip-sources", fallback=False)
pip_filename = conf.get("pip-sources", "pip_filename", fallback="pip.conf")
pip_bak_file = conf.get("pip-sources", "bak_file", fallback=True)
pip_bak_filename = conf.get("pip-sources", "bak_filename", fallback="pip.conf.bak")


############################### decorator for function tips ##############################
import functools


def function_tips(start="green", end="green"):
    def wrapper(func):
        @functools.wraps(func)
        def function(*args, **kw):
            start_content = "[{}] run {} ...".format(env.host_string, func.__name__)
            end_content = "[{}] run {} finished".format(env.host_string, func.__name__)


            if start == "red":
                print(red(start_content))
            elif start == "green":
                print(green(start_content))
            elif start == "blue":
                print(blue(start_content))
            elif start == "yellow":
                print(yellow(start_content))
            elif start == "magenta":
                print(magenta(start_content))
            elif start == "cyan":
                print(cyan(start_content))
            else:
                print(start_content)

            cost_start = time.clock()

            outcome = func(*args, **kw)

            cost_time = time.clock() - cost_start


            if end == "red":
                print(red(end_content))
            elif end == "green":
                print(green(end_content))
            elif end == "blue":
                print(blue(end_content))
            elif end == "yellow":
                print(yellow(end_content))
            elif end == "magenta":
                print(magenta(end_content))
            elif end == "cyan":
                print(cyan(end_content))
            else:
                print(end_content)

            print(magenta("[{}] run {} cost time {:.6f}s.".format(env.host_string, func.__name__, cost_time)))

            return outcome

        return function

    return wrapper


# ------------ update_node pip sources start ----------

@task
@parallel
@function_tips()
def update_node_pip(switch=None, source=None, bak_file=None, bak_filename=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not switch:
            switch = pip_sources_boolean
        if not source:
            source = pip_filename
        if not bak_file:
            bak_file = pip_bak_file
        if not bak_filename:
            bak_filename = pip_bak_filename

        if switch:
            file_path = "../sources/sys_config/apt_pip/{}".format(source)
            if bak_file:
                if run("test -f ~/.pip/pip.conf").failed:
                    sudo("mkdir -p ~/.pip", user=env.user, group=env.user)
                else:
                    sudo("cp -f ~/.pip/pip.conf ~/.pip/{} 2>/dev/null".format(bak_filename))
                    sudo("chown {}:{} ~/.pip/pip.conf.bak".format(env.user, env.user))
            sudo("echo update the node {} pip.conf".format(env.host))
            put(file_path, "temp_pip_sources", mode=0o644, use_sudo=True)
            sudo("mv temp_pip_sources ~/.pip/pip.conf")

# ------------ update_node pip sources end ----------


# ------------------------------ file and dir seek  start ------------------------------
@task
@parallel
@function_tips()
def seek_file_content(path=None, grep=None):
    with settings(warn_only=True):
        if not path or sudo("test -f {}".format(path)).failed:
            print(red("error input path !"))
            return

        if not grep:
            sudo("cat {}".format(path))
        else:
            sudo("grep '{}' {} 2>/dev/null".format(grep, path))


@task
@parallel
@function_tips()
def seek_file_list(path=None, order="desc"):
    with settings(warn_only=True):
        if not path or sudo("test -d {}".format(path)).failed:
            print(red("path error!"))
            return
        if order == "asc":
            sudo("ls -lht {}".format(path))
        else:
            sudo("ls -lhtr {}".format(path))

# ------------------------------ file and dir seek  end ------------------------------


# --------------------------------- unichain related install start -------------------------------------

@task
@parallel
@function_tips()
def init_all_nodes(service_name=None, setup_name=None, shred=False, times=3, show=False,
                   only_code=True, config_del=False):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(hide('running', 'stdout'), warn_only=True):
        if not service_name:
            service_name = _service_name
            setup_name = _setup_name
        if not service_name or not setup_name or service_name == ".*":
            print(red("error service or setup name !"))
            return

        sudo('killall -9 {} 2>/dev/null'.format(service_name))
        sudo('killall -9 {}_api 2>/dev/null'.format(service_name))
        # sudo('killall -9 {}_restore_api 2>/dev/null'.format(service_name))
        sudo('killall -9 rethinkdb 2>/dev/null')
        sudo('killall -9 collectd 2>/dev/null')
        sudo('killall -9 pip 2>/dev/null')
        sudo('killall -9 pip3 2>/dev/null')
        sudo('apt-get -f install')
        sudo("dpkg --configure -a")

        if shred is True:
            if not times or int(times) <= 1:
                times = 2
            if show is True:
                cmd_shred = "shred -fuz -n {} -v ".format(times)
            else:
                cmd_shred = "shred -fuz -n {} ".format(times)

            sudo('/bin/rm /usr/local/bin/{} 2>/dev/null'.format(service_name))

            print(blue('echo "[INFO]==========uninstall {}=========="'.format(service_name)))

            # purge del dist files
            count_bin = sudo("find /usr/local/bin/{}* -type f|wc -l".format(service_name))
            if count_bin != "0":
                sudo('{} `find /usr/local/bin/{}* -type f 2>/dev/null`'.format(cmd_shred, service_name))
            sudo('/bin/rm -f /usr/local/bin/{} 2>/dev/null'.format(service_name))

            count_lib = sudo("find /usr/local/lib/python3.4/dist-packages/{}* -type f|wc -l".format(setup_name))
            if count_lib != "0":
                sudo('{} `find /usr/local/lib/python3.4/dist-packages/{}* -type f 2>/dev/null`'
                     .format(cmd_shred, setup_name))
            sudo('/bin/rm -rf /usr/local/lib/python3.4/dist-packages/{}* 2>/dev/null'.format(setup_name))

            # purge del unichain files
            count_unichain_files = sudo("find ~/{} -type f|wc -l".format(service_name))
            if count_unichain_files != "0":
                sudo('{} `find ~/{} -type f 2>/dev/null`'.format(cmd_shred, service_name))
            sudo('/bin/rm -rf ~/{} 2>/dev/null'.format(service_name))

            count_unichain_archive = sudo("find ~/{}-archive.tar.gz -type f|wc -l".format(service_name))
            if count_unichain_archive != "0":
                sudo('{} `find ~/{}-archive.tar.gz -type f 2>/dev/null`'.format(cmd_shred, service_name))
            sudo('/bin/rm -rf ~/{}-archive.tar.gz 2>/dev/null'.format(service_name))

            # purge del unichain conf files
            if config_del is True:
                count_conf = sudo("find ~/.{} -type f|wc -l".format(service_name))
                if count_conf != "0":
                    sudo('{} `find ~/.{} -type f 2>/dev/null`'.format(cmd_shred, service_name))
                sudo('/bin/rm ~/.{}'.format(service_name))

            # purge del unichain logs
            count_unichain_logs = sudo("find ~/{}_log -type f|wc -l".format(service_name))
            if count_unichain_logs != "0":
                sudo('{} `find ~/{}_log -type f 2>/dev/null`'.format(cmd_shred, service_name))
            sudo('/bin/rm -rf ~/{}_log 2>/dev/null'.format(service_name))

        else:
            # unichain delete
            sudo('/bin/rm /usr/local/bin/{} 2>/dev/null'.format(service_name))
            sudo('/bin/rm -rf /usr/local/lib/python3.4/dist-packages/{}-* 2>/dev/null'.format(setup_name))

            # unichain code delete
            sudo('/bin/rm -rf ~/{} 2>/dev/null'.format(service_name))
            sudo('/bin/rm -rf ~/{}-archive.tar.gz 2>/dev/null'.format(service_name))

            # unichain configure delete
            if config_del:
                sudo('/bin/rm -rf ~/.{} 2>/dev/null'.format(service_name))

            # unichain log delete
            sudo('/bin/rm -rf ~/{}_log* 2>/dev/null'.format(service_name))

        sudo('/bin/rm -rf /data/rethinkdb/* 2>/dev/null')
        sudo('/bin/rm -rf /data/localdb_{}/* 2>/dev/null'.format(service_name))

        if only_code is False:
            sudo('pip3 uninstall -y plyvel')
            sudo('apt-get remove --purge -y libleveldb1')
            sudo('apt-get remove --purge -y libleveldb-dev')
            sudo('apt-get remove --purge -y rethinkdb')

            # sudo('apt-get remove --purge -y collectd')

            # try:
            #     sudo('dpkg --purge collectd')
            # except:
            #     fixed_dpkg_error()
            #     sudo('dpkg --purge collectd')
            # sudo("echo 'uninstall ls over'")


@task
@parallel
@function_tips()
def kill_all_nodes(service_name=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not service_name:
            service_name = _service_name
        sudo('killall -9 {} 2>/dev/null'.format(service_name))
        sudo('killall -9 {}_api 2>/dev/null'.format(service_name))
        sudo('killall -9 rethinkdb 2>/dev/null')
        sudo('killall -9 pip 2>/dev/null')
        sudo('killall -9 pip3 2>/dev/null')


# Install RethinkDB
@task
@parallel
@function_tips()
def install_rethinkdb():
    # with settings(hide('stdout'), warn_only=True):
    with settings(warn_only=True):
        sudo("dpkg --configure -a")
        sudo("mkdir -p /data/rethinkdb")
        # install rethinkdb
        sudo('source /etc/lsb-release && echo "deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main" | sudo tee /etc/apt/sources.list.d/rethinkdb.list')
        sudo("wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -")
        sudo("apt-get update")

        sudo("apt-get -y install rethinkdb")
        # initialize rethinkdb data-dir
        sudo('rm -rf /data/rethinkdb/*')

# # Install RethinkDB
# @task
# @parallel
# @function_tips()
# def install_rethinkdb():
#     # with settings(hide('stdout'), warn_only=True):
#     with settings(warn_only=True):
#         sudo("mkdir -p /data/rethinkdb")
#         # install rethinkdb
#         sudo("source /etc/lsb-release && echo 'deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main' \
#         | sudo tee /etc/apt/trusty-sources.list.d/rethinkdb.list")
#         sudo("wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -")
#         sudo("apt-get update")
#
#         sudo("apt-get -y install rethinkdb")
#         # initialize rethinkdb data-dir
#         sudo('rm -rf /data/rethinkdb/*')


# Configure RethinkDB
@task
@parallel
@function_tips()
def configure_rethinkdb():
    """Configure of RethinkDB"""
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        # copy base_conf file to target system
        put('../conf/rethinkdb.conf',
            '/etc/rethinkdb/instances.d/default.conf',
            mode=0o600,
            use_sudo=True)
        # finally restart instance
        sudo('/etc/init.d/rethinkdb restart')


# Configure RethinkDB
@task
@parallel
@function_tips()
def send_configure_rethinkdb():
    """Configure of RethinkDB"""
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        # copy base_conf file to target system
        put('../conf/rethinkdb.conf',
            '/etc/rethinkdb/instances.d/default.conf',
            mode=0o600,
            use_sudo=True)


# delete the disk data for rethinkdb in /data/rethinkdb/*
@task
@parallel
@function_tips()
def clear_rethinkdb_data():
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo('rm -rf /data/rethinkdb/* 2>/dev/null')


@task
@function_tips()
def start_rethinkdb():
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo("service rethinkdb start")
        time.sleep(2)
        check_rethinkdb_run()


@task
@function_tips()
def check_rethinkdb_run():
    with settings(hide('running', 'stdout'), warn_only=True):
        while True:
            process_count = sudo("ps -e|grep -w rethinkdb|wc -l")
            rethinkdb_start = process_count != "0"
            if rethinkdb_start:
                break
            else:
                print(red("rethinkdb nodes {} not run, will restart!".format(env.host)))
                start_rethinkdb()


@task
@function_tips()
def stop_rethinkdb():
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo("service rethinkdb stop")


@task
@function_tips()
def restart_rethinkdb():
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo("service rethinkdb restart")
        time.sleep(2)
        check_rethinkdb_run()


# what`s ?
@task
@function_tips()
def rebuild_rethinkdb():
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo("service rethinkdb index-rebuild -n 2")


@task
@parallel
@function_tips()
def append_rethinkdb_join(port=29015):
    with settings(hide('running', 'stdout'), warn_only=True):
        if port is None:
            port = 29015
        join_infos = ""
        rethinkdb_conf_path = "/etc/rethinkdb/instances.d/default.conf"
        for host in public_hosts:
            join_info = "join={}:{}".format(host, port)
            join_infos += join_info + "\\n"
            sudo("echo {} {}".format(host, join_info))
        join_infos =join_infos[:-2]
        print(blue("The joins will write to {}:\n{}".format(rethinkdb_conf_path, join_infos)))
        if join_infos != '':
           sudo("sed -i '$a {}' /etc/rethinkdb/instances.d/default.conf".format(join_infos))


@task
@parallel
@function_tips()
def rewrite_rethinkdb_join(port=29015):
    with settings(hide('running', 'stdout'), warn_only=True):
        if port is None:
            port = 29015
        join_infos = ""
        rethinkdb_conf_path = "/etc/rethinkdb/instances.d/default.conf"
        for host in public_hosts:
            join_info = "join={}:{}".format(host, port)
            join_infos += join_info + "\\n"
        join_infos = join_infos[:-2]
        print(blue("The joins will write to [{}] {}:\n{}".format(env.host_string, rethinkdb_conf_path, join_infos)))
        if join_infos != '':
           sudo("sed -i '/^\s*join=/d' /etc/rethinkdb/instances.d/default.conf")
           sudo("sed -i '$a {}' /etc/rethinkdb/instances.d/default.conf".format(join_infos))


@task
@parallel
@function_tips()
def remove_rethinkdb_join():
    with settings(hide('running', 'stdout'), warn_only=True):
         sudo("sed -i '/^\s*join=/d' /etc/rethinkdb/instances.d/default.conf")


@task
@parallel
@function_tips()
def seek_rethinkdb_join():
    with settings(hide('running'), warn_only=True):
        sudo("sed -n '/^\s*join=/p' /etc/rethinkdb/instances.d/default.conf")


# Install Collectd
@task
@parallel
@function_tips()
def install_collectd():
    """Installation of Collectd"""
    # with settings(hide('running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        sudo("echo 'deb http://http.debian.net/debian wheezy-backports-sloppy main contrib non-free' | "
             "sudo tee /etc/apt/sources.list.d/backports.list")
        # fixed the GPG Error
        sudo("gpg --keyserver pgpkeys.mit.edu --recv-key  8B48AD6246925553")
        sudo("gpg -a --export 8B48AD6246925553 | sudo apt-key add -")
        sudo("gpg --keyserver pgpkeys.mit.edu --recv-key  7638D0442B90D010")
        sudo("gpg -a --export 7638D0442B90D010 | sudo apt-key add -")
        sudo("apt-get update")
        try:
            sudo("apt-get install -y --force-yes -t wheezy-backports-sloppy collectd")
        except:
            sudo("rm /var/cache/apt/archives/lock")
            sudo("rm /var/lib/dpkg/lock")
            sudo("apt-get install -y --force-yes -t wheezy-backports-sloppy collectd")


# Configure Collectd
@task
@parallel
@function_tips()
def configure_collectd():
    """Configure of Collectd"""
    with settings(hide('running', 'stdout'), warn_only=True):
        # fix: lib version too high
        sudo('ln -sf /lib/x86_64-linux-gnu/libudev.so.?.?.? /lib/x86_64-linux-gnu/libudev.so.0')
        sudo('ldconfig')
        # copy base_conf file to target system
        put('../conf/collectd.conf',
            '/etc/collectd/collectd.conf',
            mode=0o600,
            use_sudo=True)


@task
@parallel
@function_tips()
def start_collectd():
    """Installation of Collectd"""
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo('service collectd restart', pty=False)


@task
@parallel
@function_tips()
def stop_collectd():
    """Installation of Collectd"""
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo('service collectd stop', pty=False)


# install localdb
@task
@parallel
@function_tips()
def install_localdb():
    # leveldb & plyvel install
    with settings(hide('running', 'stdout'), warn_only=True):
        sudo('dpkg --configure -a')
        sudo('apt-get install -y libleveldb1 libleveldb-dev libsnappy1 libsnappy-dev')
        sudo('apt-get -y -f install')
        sudo('pip3 install plyvel==0.9')

@task
@parallel
@function_tips()
def init_localdb(service_name=None):
    with settings(hide('running', 'stdout'), warn_only=True):
        if not service_name:
            service_name = _service_name

        if not service_name or len(service_name) <= 1 or service_name == ".*":
            print(red("error service name"))
            return

        user_group = env.user
        sudo('rm -rf /data/localdb_{}/*'.format(service_name))
        sudo("mkdir -p /data/localdb_{}".format(service_name))
        sudo("chown -R " + user_group + ':' + user_group + ' /data/localdb_{}'.format(service_name))


# Send the specified configuration file to
# the remote host and save it there in
# ~/.unichain
# Use in conjunction with set_host()
# No @parallel
@task
@function_tips()
def send_confile(confile, service_name=None):
    with settings(hide('running', 'stdout'), warn_only=True):
        if not service_name:
            service_name = _service_name

        if not service_name or len(service_name) <= 1 or service_name == ".*":
            print(red("error service name"))
            return

        put('../conf/unichain_confiles/' + confile, 'tempfile')
        run('mv tempfile ~/.{}'.format(service_name))
        run('{} show-base_conf'.format(service_name))


# Install UnichainDB from the archive file
# named unichain-archive.tar.gz
@task
@parallel
@function_tips()
def install_unichain_from_archive(service_name=None, setup_name=None):
    # with settings(hide('running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        if not setup_name:
            setup_name = _setup_name

        if not service_name or len(service_name) <= 1 or service_name == ".*":
            print(red("error service name"))
            return

        if not setup_name or len(setup_name) <= 1 or setup_name == ".*":
            print(red("error setup name"))
            return

        put('unichain-archive.tar.gz')

        sudo('/bin/rm -f /usr/local/bin/{}* 2>/dev/null'.format(service_name))
        sudo('/bin/rm -rf /usr/local/lib/python3.4/dist-packages/{}* 2>/dev/null'.format(setup_name))

        with settings(warn_only=True):
            if run("test -d ~/{}".format(service_name)).failed:
                print(blue("create {} directory".format(service_name)))
                sudo("mkdir -p ~/{}".format(service_name), user=env.user, group=env.user)
                # sudo("chown -R " + user_group + ':' + user_group + ' ~/')
            else:
                print(blue("remove old {} directory".format(service_name)))
                sudo("/bin/rm -rf {}/*".format(service_name))

        run('tar zxf unichain-archive.tar.gz -C {} >/dev/null 2>&1'.format(service_name))

        # must install dependency first!
        with cd('./{}'.format(service_name)):
            sudo('python3 setup.py install')

        sudo('/bin/rm -f unichain-archive.tar.gz')



# Initialize UnichainDB
# i.e. create the database, the tables,
# the indexes, and the genesis block.
# (The @hosts decorator is used to make this
# task run on only one node. See http://tinyurl.com/h9qqf3t )
@task
@runs_once
@function_tips()
def init_unichain(service_name=None, shards=False, replicas=False):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        stop_unichain()
        check_unichain()
        run('{} -y drop'.format(service_name),pty=False)
        run('{} init'.format(service_name), pty=False)
        if shards is True:
            set_shards()
        if replicas is True:
            set_replicas()


# Configure UnichainDB
@task
@parallel
@function_tips()
def configure_unichain(service_name=None):
    if not service_name:
        service_name = _service_name
    run('{} -y configure'.format(service_name), pty=False)


@runs_once
@task
@function_tips()
def drop_unichain(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        run('{} -y drop'.format(service_name), pty=False)


# Set the number of shards (tables[bigchain,votes,backlog])
@runs_once
@task
@function_tips()
def set_shards(num_shards=len(public_dns_names), service_name=None):
    # num_shards = len(public_hosts)
    if not service_name:
        service_name = _service_name
    run('{} set-shards {}'.format(service_name, num_shards))
    run("echo set shards = {}".format(num_shards))


# Set the number of replicas (tables[bigchain,votes,backlog])
@runs_once
@task
@function_tips()
def set_replicas(num_replicas=(int(len(public_dns_names)/2)+1), service_name=None):
    if not service_name:
        service_name = _service_name
    run('{} set-replicas {}'.format(service_name, num_replicas))
    run("echo set replicas = {}".format(num_replicas))


# unichain_restore_app
@task
@parallel
@function_tips()
def start_unichain_restore(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        stop_unichain()
        start_rethinkdb()
        sudo('screen -d -m {}_restore -y start &'.format(service_name), pty=False, user=env.user)


@task
@parallel
@function_tips()
def stop_unichain_restore(service_name=None, service_port=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not service_name:
            service_name = _service_name
            service_port = _server_port
        sudo("killall -9 {}_restore 2>/dev/null".format(service_name))
        try:
            sudo("kill -9 `netstat -nlp | grep :{} | awk '{{ print $7 }}' | awk -F'/' '{{ print $1 }}'`".format(
                service_port))
        except:
            pass
        run("echo stop {}_restore and kill the port {}".format(service_name, service_port))

# unichain
@task
@parallel
@function_tips()
def start_unichain(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        stop_unichain_restore()
        sudo('screen -d -m {} -y start &'.format(service_name), pty=False, user=env.user)
        sudo('screen -d -m {}_api start &'.format(service_name), pty=False, user=env.user)

@task
@parallel
@function_tips()
def stop_unichain(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        # sudo("kill `ps -ef|grep unichain | grep -v grep|awk '{print $2}'` ")
        sudo("killall -9 {}_api 2>/dev/null".format(service_name))
        sudo("killall -9 {} 2>/dev/null".format(service_name))

@task
@parallel
@function_tips()
def restart_unichain(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        sudo("killall -9 {}_api 2>/dev/null".format(service_name))
        sudo("killall -9 {} 2>/dev/null".format(service_name))
        sudo('screen -d -m {} -y start &'.format(service_name), pty=False, user=env.user)
        sudo('screen -d -m {}_api start &'.format(service_name), pty=False, user=env.user)

@task
@parallel
@function_tips()
def start_unichain_load(service_name=None):
    if not service_name:
        service_name = _service_name
    sudo('screen -d -m {} load &'.format(service_name), pty=False)

#


# python3,pip,pip3
@task
@function_tips()
def stop_python():
    with settings(warn_only=True):
        sudo("killall -9 python python3 pip pip3 2>/dev/null")

# unichain
# uninstall old unichain
@task
@parallel
@function_tips()
def uninstall_unichain(service_name=None, setup_name=None, only_code=True):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        if not setup_name:
            setup_name = _setup_name
        init_all_nodes(service_name=service_name, setup_name=setup_name, shred=False, only_code=only_code)


# ---------------------------------  unichain related install end ---------------------------------------


################################ Check Env Start ######################################

#step:check port&process&data,conf path
@task
@function_tips()
def check_rethinkdb():
    with settings(warn_only=True):
        print("[INFO]==========check rethinkdb begin==========")
        process_num=run('ps -aux|grep -E "/usr/bin/rethinkdb"|grep -v grep|wc -l')
        if process_num == 0:
            print("[INFO]=====process[rethinkdb] num detect result: is 0")
        else:
            print("[ERROR]=====process[rethinkdb] num detect result: is %s" % (str(process_num)))
        #TODO:read from conf
        driver_port = 28015
        cluster_port = 29015
        http_port = 8080
        check_driver_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (driver_port))
        if not check_driver_port:
            print("[INFO]=====driver_port[%s] detect result: is not used!" % (driver_port))
        else:
            print("[ERROR]=====driver_port[%s] detect result: is used!" % (driver_port))
        check_cluster_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (cluster_port))
        if not check_cluster_port:
            print("[INFO]=====cluster_port[%s] detect result: is not used!" % (cluster_port))
        else:
            print("[ERROR]=====cluster_port[%s] detect result:  is used!" % (cluster_port))
        check_http_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (http_port))
        if not check_http_port:
            print("[INFO]=====http_port[%s] detect result: is not used!" % (http_port))
        else:
            print("[ERROR]=====http_port[%s] detect result: is used!" % (http_port))

#step:check port&process&data,conf path
@task
@function_tips()
def check_localdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step:check port&process&data,conf path
@task
@function_tips()
def check_unichain(service_name=None, server_port=None):
    if not service_name:
        service_name = _service_name
    with settings(warn_only=True):
        print("[INFO]==========check {} pro begin==========".format(service_name))
        process_num=run('ps -aux|grep -E "/usr/local/bin/{} -y start|SCREEN -d -m {} -y start"|grep -v grep|wc -l'
                        .format(service_name, service_name))
        if process_num == 0:
            print("[INFO]=====process[{}] num check result: is 0".format(service_name))
        else:
            print("[ERROR]=====process[{}] num check result: is {}".format(service_name, process_num))
        ##TODO:confirm port in conf
        if not server_port:
            server_port = _server_port
        api_port=server_port
        check_api_port=sudo('netstat -nlap|grep "LISTEN"|awk -v v_port=":%s" \'{if(v_port==$4) print $0}\'' % (api_port))
        if not check_api_port:
            print("[INFO]=====api_port[%s] detect result: is not used!" % (api_port))
        else:
            print("[ERROR]=====api_port[%s] detect result: is used!" % (api_port))

#step:check port&process&data,conf path
@task
@function_tips()
def check_unichain_api(service_name=None):
    with settings(warn_only=True):
        if not service_name:
           service_name = _service_name
        print("[INFO]==========check {} api begin==========".format(service_name))
        process_num=run('ps -aux|grep -E "/usr/local/bin/{}_api start|SCREEN -d -m {}_api start"|grep -v grep|wc -l'
                        .format(service_name, service_name))
        if process_num == 0:
            print("[INFO]=====process[{}_api] num check result: is 0".format(service_name))
        else:
            print("[ERROR]=====process[{}_api] num check result: is {}".format(service_name, process_num))

################################ Check Env End ######################################

################################ Detect server ######################################
#step: get port & detect port
@task
@function_tips()
def detect_rethinkdb():
    with settings(warn_only=True):
        print("[INFO]==========detect rethinkdb begin==========")
        rethinkdb_conf = "/etc/rethinkdb/instances.d/default.conf"
        driver_port = sudo('cat %s|grep -v "^#"|grep "driver-port="|awk -F"=" \'{print $2}\'' % (rethinkdb_conf))
        cluster_port = sudo('cat %s|grep -v "^#"|grep "cluster-port="|awk -F"=" \'{print $2}\'' % (rethinkdb_conf))
        http_port = sudo('cat %s|grep -v "^#"|grep "http-port="|awk -F"=" \'{print $2}\'' % (rethinkdb_conf))
        if not driver_port :
            driver_port = 28015
        if not cluster_port:
            cluster_port = 29015
        if not http_port:
            http_port = 8080
        check_driver_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (driver_port))
        if not check_driver_port:
            print("[ERROR]=====driver_port[%s] detect result: NOT exist!" % (driver_port))
        else:
            print("[INFO]=====driver_port[%s] detect result: is OK!" % (driver_port))
        check_cluster_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (cluster_port))
        if not check_cluster_port:
            print("[ERROR]=====cluster_port[%s] detect result: not alive" % (cluster_port))
        else:
            print("[INFO]=====cluster_port[%s] detect result:  is OK!" % (cluster_port))
        check_http_port=sudo('netstat -nlap|grep "LISTEN"|grep rethinkdb|grep ":%s"' % (http_port))
        if not check_http_port:
            print("[ERROR]=====http_port[%s] detect result: not alive" % (http_port))
        else:
            print("[INFO]=====http_port[%s] detect result: is OK!" % (http_port))
        process_num=run('ps -aux|grep -E "/usr/bin/rethinkdb"|grep -v grep|wc -l')
        if process_num == 0:
            print("[ERROR]=====process[rethinkdb] num detect result: is 0")
        else:
            print("[INFO]=====process[rethinkdb] num detect result: is %s" % (str(process_num)))


#step: get port & detect port & detect process
@task
@function_tips()
def detect_localdb():
    with settings(warn_only=True):
        #TODO:
        pass

#step: get port & detect port & detect process
@task
@function_tips()
def detect_unichain(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        print("[INFO]==========detect {} pro begin==========".format(service_name))
        process_num=run('ps -aux|grep -E "/usr/local/bin/{} -y start|SCREEN -d -m {} -y start"|grep -v grep|wc -l'
                        .format(service_name, service_name))
        if int(process_num) == 0:
            print("[ERROR]=====process[{}] num detect result: is 0".format(service_name))
        else:
            print("[INFO]=====process[{}] num detect result: is {}".format(service_name, process_num))

#step: get port & detect port & detect process
@task
@function_tips()
def detect_unichain_api(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        print("[INFO]==========detect {} api begin==========".format(service_name))
        process_num=run('ps -aux|grep -E "/usr/local/bin/{}_api start|SCREEN -d -m {}_api start"|grep -v grep|wc -l'
                        .format(service_name, service_name))
        if int(process_num) == 0:
            print("[ERROR]=====process[{}_api] num detect result: is 0".format(service_name))
        else:
            print("[INFO]=====process[{}] num detect result: is {}".format(service_name, process_num))

        unichain_conf = "/home/{}/.{}".format(env.user, service_name)
        unichain_conf_str=run('cat ~/.{}'.format(service_name))
        #with open(unichain_conf, "a") as r:
        #    unichain_conf_str=r.readline()
        unichain_conf_str.replace("null", "")
        unichain_dict = json.loads(unichain_conf_str)
        server_url = str(unichain_dict["server"]["bind"])
        api_endpoint = str(unichain_dict["api_endpoint"])
        if server_url.startswith("0.0.0.0"):
            api_url = api_endpoint.replace("/uniledger/v1", "")
            api_detect_res = run('curl -i %s 2>/dev/null|head -1|grep "200 OK"' % (api_url))
            if not api_detect_res:
                print("[ERROR]=====api[%s] detect result: is not requested!!!" % (api_url))
            else:
                print("[INFO]=====api[%s] detect result: is OK!" % (api_url))
        else:
            print("[ERROR]=====api[%s] detect result:  is not requested!" % (api_endpoint))


#########################bak conf task#########################
@task
@parallel
@function_tips()
def bak_rethinkdb_conf(base):
    with settings(hide('running', 'stdout'), warn_only=True):
        get('/etc/rethinkdb/instances.d/default.conf',
            '%s/rethinkdb/default.conf_%s_%s' % (base, env.user, env.host), use_sudo=True)

@task
@parallel
@function_tips()
def bak_collected_conf(base):
    with settings(hide('running', 'stdout'), warn_only=True):
        get('/etc/collectd/collectd.conf', ' %s/collected/collected.conf_%s_%s' % (base, env.user, env.host),
            use_sudo=True)

@task
@parallel
@function_tips()
def bak_unichain_conf(base, service_name=None):
    with settings(hide('running', 'stdout'), warn_only=True):
        if not service_name:
            service_name = _service_name
        get('~/.{}'.format(service_name), '{}/unichain/unichain_{}_{}'.format(base, env.user, env.host),
            use_sudo=True)


######################### uninstall deals #########################
# 彻底卸载
@task
@parallel
@function_tips()
def purge_uninstall(service_name=None, setup_name=None, only_code=False):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
            setup_name = _setup_name

        sudo('killall -9 {} 2>/dev/null'.format(service_name))
        sudo('killall -9 {}_api 2>/dev/null'.format(service_name))
        sudo('killall -9 pip,pip3 2>/dev/null')

        stop_collectd()

        # shred delete files
        cmd_destroy = "shred -fuz -n 3 "
        # cmd_destroy = "shred -fuz -n 3 -v "

        run('echo "[INFO]==========uninstall {}-pro=========="'.format(service_name))
        count_conf = sudo("find ~/.{} -type f|wc -l".format(service_name))
        if count_conf != "0":
            sudo('{} `find ~/.{} -type f 2>/dev/null`'.format(cmd_destroy, service_name))
        sudo('/bin/rm ~/.{}'.format(service_name))

        # purge del files
        count_bin = sudo("find /usr/local/bin/{}* -type f|wc -l".format(service_name))
        if count_bin != "0":
            sudo('{} `find /usr/local/bin/{}* -type f 2>/dev/null`'.format(cmd_destroy, service_name))
        sudo('/bin/rm -f /usr/local/bin/{} 2>/dev/null'.format(service_name))

        # purge del files
        count_lib = sudo("find /usr/local/lib/python3.4/dist-packages/{}* -type f|wc -l".format(setup_name))
        if count_lib != "0":
            sudo('{} `find /usr/local/lib/python3.4/dist-packages/{}* -type f 2>/dev/null`'
                 .format(cmd_destroy, setup_name))
        sudo('/bin/rm -rf /usr/local/lib/python3.4/dist-packages/{}* 2>/dev/null'.format(setup_name))

        # purge del files
        count_unichain_files = sudo("find ~/{}* -type f|wc -l".format(service_name))
        if count_unichain_files != "0":
            sudo('{} `find ~/{}* -type f 2>/dev/null`'.format(cmd_destroy, service_name))
        sudo('/bin/rm -rf ~/{} 2>/dev/null'.format(service_name))

        # purge del logs
        count_unichain_logs = sudo("find ~/{}_log -type f|wc -l".format(service_name))
        if count_unichain_logs != "0":
            sudo('{} `find ~/{}_log -type f 2>/dev/null`'.format(cmd_destroy, service_name))
        sudo('/bin/rm -rf ~/{}_log 2>/dev/null'.format(service_name))

        # purge del data
        sudo('/bin/rm -rf /data/rethinkdb 2>/dev/null')
        sudo('/bin/rm -rf /data/localdb_{} 2>/dev/null'.format(service_name))

        if only_code is False:
            sudo('pip3 uninstall -y plyvel')
            sudo('apt-get remove --purge -y libleveldb1')
            sudo('apt-get remove --purge -y libleveldb-dev')
            sudo('apt-get remove --purge -y rethinkdb')

            # try:
            #     sudo('dpkg --purge collectd')
            # except:
            #     fixed_dpkg_error()
            #     sudo('dpkg --purge collectd')
            # sudo("echo 'uninstall ls over'")

# 彻底卸载
@task
@parallel
@function_tips()
def purge_delete_files(path_name=None, times=3, show=False):
    with settings(warn_only=True):
        if not path_name:
            return

        # shred delete files
        if not times:
            times = 3
        if show is True:
            cmd_destroy = "shred -fuz -n {} -v ".format(times)
        else:
            cmd_destroy = "shred -fuz -n {} ".format(times)

        run('echo "[INFO]==========uninstall {}=========="'.format(path_name))
        count_conf = sudo("find ~/{} -type f|wc -l".format(path_name))
        time.sleep(6)
        if count_conf != "0":
            sudo('{} `find ~/{} -type f 2>/dev/null`'.format(cmd_destroy, path_name))
        sudo('/bin/rm -rf ~/{}'.format(path_name))


################################ First Install Start######################################

#set on node
@task
@function_tips()
def set_node(host, password):
    env['passwords'][host]=password
    env['hosts']=env['passwords'].keys()


@task
@function_tips()
def set_host(host_index):
    """A helper task to change env.hosts from the
    command line. It will only "stick" for the duration
    of the fab command that called it.

    Args:
        host_index (int): 0, 1, 2, 3, etc.
    Example:
        fab set_host:4 fab_task_A fab_task_B
        will set env.hosts = [public_dns_names[4]]
        but only for doing fab_task_A and fab_task_B
    """
    env.hosts = [public_dns_names[int(host_index)]]
    env.password = [public_pwds[int(host_index)]]



# ------------------------------------------- other deals -----------------------------------
# count the special process count
@task
@parallel
@function_tips()
def count_process_with_name(name):
    with settings(hide('running', 'stdout'), warn_only=True):
        print(blue("{} count process with name {} start ...".format(env.host_string, name)))
        user = env.user
        cmd = "echo '{}`s process name {}, count is ' `ps -e |grep -w {} | wc -l`".format(user,name,name)
        result = sudo("{}".format(cmd) )
        print(green("{}".format(result)))


@task
@parallel
def kill_process_with_name(name):
    with settings(hide('running', 'stdout'), warn_only=True):
        print(blue("{} kill process with name {} start ...".format(env.host_string, name)))
        sudo("killall -9 {} 2>/dev/null".format(name))
        print(green("{} kill process with name {} over".format(env.host_string, name)))


@task
@parallel
@function_tips()
def kill_process_with_port(port):
    with settings(hide('running', 'stdout'), warn_only=True):
        print(blue("{} kill process with port {} start ...".format(env.host_string, port)))
        try:
            sudo("kill -9 `netstat -nlp | grep :{} | awk '{{print $7}}' | awk '!a[$0]++' | \
awk -F'/' '{{ print $1 }}'` 2>/dev/null".format(port))
        except:
            raise
        print(green("{} kill process with port {} over".format(env.host_string, port)))


@task
@function_tips()
def reboot_all_hosts_serial():
    with settings(hide('running', 'stdout'), warn_only=True):
        print(blue("{} will reboot...".format(env.host_string)))
        confirm = prompt('Would you like to continue reboot {} ? (y/n)'.format(env.host_string),
                         default='n', validate=r'^y|n$')
        if confirm == 'n':
            print(red("{} give up rebooting!".format(env.host_string)))
            return
        sudo("reboot",timeout=120)
        print(green("{} reboot success".format(env.host_string)))


@task
@function_tips()
def reboot_all_hosts():
    with settings(hide('running', 'stdout'), warn_only=True):
        print(blue("{} will reboot...".format(env.host_string)))
        sudo("reboot",timeout=120)
        print(green("{} reboot success".format(env.host_string)))


#################################### Test unichain #################################
@task
@parallel
@function_tips()
def test_localdb_model_delete(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        sudo('mkdir -p /data/backup_localdb_{}'.format(service_name), pty=False)
        sudo("echo delete localdb backup files in node {}".format(env.host))
        sudo("mv /data/localdb_{}/* /data/backup_localdb_{}".format(service_name, service_name))
        sudo("echo delete localdb backup files in node {} over".format(env.host))

@task
@parallel
@function_tips()
def test_localdb_model_download(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        sudo("echo download localdb backup files to node {}".format(env.host))
        sudo("mv /data/backup_localdb_{}/* /data/localdb_{}".format(service_name, service_name))
        sudo("echo download localdb backup files to node {} over".format(env.host))

@task
@parallel
@function_tips()
def test_localdb_model_files(service_name=None, path="/data/localdb_{}".format(_service_name)):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        sudo("echo files in node {}".format(env.host))
        sudo("ls {}".format(path))

@task
@parallel
@function_tips()
def test_localdb_rethinkdb(args="-irbvt", filename="validate_localdb_format.py", datetimeformat="%Y%m%d%H",
                           service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        user = env.user
        with cd("~/{}/ul_tests/localdb".format(service_name)):
            filename_prefix = filename.split(".")[0]
            if run("test -d test_result").failed:
                sudo("mkdir test_result", user=env.user, group=env.user)
            sudo("python3 {} {} | tee test_result/{}_{}_$(date +{}).txt".format(filename, args, user,filename_prefix,
                                                                                datetimeformat))
        sudo("echo 'test_localdb_rethinkdb over'")


@task
@function_tips()
def local_configure_unichain(conpath, service_name=None):
    if not service_name:
        service_name = _service_name
    local('{} -y -c {} configure'.format(service_name, conpath))


@task
@parallel
def reconfig_unichain(service_name=None):
    with settings(warn_only=True):
        if not service_name:
            service_name = _service_name
        tmpfile = '/tmp/remote_temp.%s.txt' % os.getpid()
        get('~/.{}'.format(service_name), tmpfile)

        with open(tmpfile) as f:
            try:
                config = json.load(f)
            except ValueError as err:
                raise

        with open('../conf/template/unichain.conf.template') as f:
            try:
                config2 = json.load(f)
            except ValueError as err:
                raise
        config3 = {'logger_config': config2['logger_config'], 'argument_config': config2['argument_config']}
        config.update(config3)

        with open(tmpfile, 'w') as f:
            json.dump(config, f, indent=4)

        put(tmpfile, 'tempfile')
        run('mv tempfile ~/.{}'.format(service_name))
        print('For this node, {} show-base_conf says:'.format(service_name))
        run('{} show-base_conf'.format(service_name))

#  修改节点配置文件
@task
def modify_node_confile():
    """发送unichain配置文件"""
    with settings(warn_only=True):
        user = sudo("echo $HOME")
        filepath = user + '/.unichain'
        get(filepath, "./unichain_conf")
        sudo('cp ~/.unichain ~/.unichain_bak')
        local('python3 modify_node_confiles.py')
        put('unichain_conf', "~/.unichain")


#  修改节点配置文件
@task
def update_unichain_config(host_index):
    """发送unichain配置文件"""
    with settings(warn_only=True):
        node_ip = public_hosts[int(host_index)]
        user = sudo("echo $HOME")
        filepath = user + '/.unichain'
        get(filepath, "./unichain_conf")
        sudo('cp ~/.unichain ~/.unichain_bak')
        local('python3 update_node_confiles.py {}'.format(node_ip))
        put('unichain_conf', "~/.unichain")