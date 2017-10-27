
# -*- coding: utf-8 -*-

"""A Fabric fabfile with functionality to prepare, install, and configure
UnichainDB, including its storage backend (RethinkDB).
"""


from __future__ import with_statement, unicode_literals

import sys

import time

from fabric.colors import red, green, blue, yellow, magenta, cyan
from fabric.api import sudo, cd, env, hosts, local, runs_once
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put, get, prompt
from fabric.context_managers import settings, hide

from configparser import ConfigParser

from hostlist_origin import public_dns_names,public_hosts,public_pwds,public_host_pwds, public_usernames

################################ Fabric Initial Config Data  ######################################

env['passwords'] = public_host_pwds
env['hosts']=env['passwords'].keys()

# env['passwords']['wangxin@localhost:22'] = "wangxin123"

from multi_apps_conf import app_config

_server_port = app_config['server_port']
_restore_server_port = app_config['restore_server_port']
_service_name = app_config['service_name']
_setup_name = app_config['setup_name']


conf = ConfigParser()
cluster_info_filename = "../conf/cluster_info.ini"
conf.read(cluster_info_filename, encoding="utf-8")


# 功能开关属性
# 1.1. apt 更新 开关
apt_sources_switch = conf.get("on-off", "apt-sources", fallback="off")
apt_sources_boolean = conf.getboolean("on-off", "apt-sources", fallback=False)
os_codename = conf.get("apt-sources", "codename", fallback="trusty")
apt_source_filename = conf.get("apt-sources", "source_filename", fallback=None)
apt_bak_file = conf.get("apt-sources", "bak_file", fallback=True)
apt_bak_filename = conf.get("apt-sources", "bak_filename", fallback="sources.list.bak")


# 1.2. third apt 更新开关
third_apt_sources_switch = conf.get("on-off", "third-apt-sources", fallback="off")
third_apt_sources_boolean = conf.getboolean("on-off", "third-apt-sources", fallback=False)

# 1.3. pip 更新开关
pip_sources_switch = conf.get("on-off", "pip-sources", fallback="off")
pip_sources_boolean = conf.getboolean("on-off", "pip-sources", fallback=False)
pip_filename = conf.get("pip-sources", "pip_filename", fallback="pip.conf")
pip_bak_file = conf.get("pip-sources", "bak_file", fallback=True)
pip_bak_filename = conf.get("pip-sources", "bak_filename", fallback="pip.conf.bak")

# apt and pip update ops 开关
apt_pip_update_switch = conf.get("on-off", "apt-pip-update", fallback="off")
apt_pip_update_boolean = conf.getboolean("on-off", "apt-pip-update", fallback=False)


zone_datetime_switch = conf.get("on-off", "zone-datetime", fallback="off")
zone_datetime_boolean = conf.getboolean("on-off", "zone-datetime", fallback=False)


# create net user
create_new_user_switch = conf.get("on-off", "create-new-user", fallback="off")
# create_new_user_boolean = conf.getboolean("on-off", "create-new-user", fallback=False)

# update node host
update_node_host_switch = conf.get("on-off", "update-node-host", fallback="off")
# update_node_host_boolean = conf.getboolean("on-off", "update-node-host", fallback=False)

# install base software
install_base_software_switch = conf.get("on-off", "install-base-software", fallback="off")
# install_base_software_boolean = conf.getboolean("on-off", "install-base-software", fallback=False)

# update origin password
update_orgin_node_password = False
for option in conf.options(section="node-info-origin"):
    host_string_password_newpwd = conf.get("node-info-origin", option).split(" ")
    if len(host_string_password_newpwd) == 3:
        update_orgin_node_password = True
        break

# create new user
create_new_user_boolean = False
if conf.has_section("node-info-new-user") and len(conf.items("node-info-new-user")) >= 1:
    create_new_user_boolean = True

# update new user node password
update_new_user_node_password = False
for option in conf.options(section="node-info-new-user"):
    host_string_password_newpwd = conf.get("node-info-new-user", option).split(" ")
    if len(host_string_password_newpwd) == 3:
        update_new_user_node_password = True
        break

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

# ---------------------------- local tools ---------------------------------


@hosts("localhost")
@task
@function_tips()
def local_apt_pip_update(switch=None, apt=True, pip=False):
    with settings(hide('stdout'), warn_only=True):
        # print(blue("{} local apt pip update start ...".format(env.host_string)))
        if not switch:
            switch = apt_pip_update_boolean

        # update_node_apt(switch=apt, codename="trusty", bak_file=True)
        update_node_apt(switch=apt, bak_file=True)
        update_node_third_apt(switch=True)
        update_node_pip(switch=pip, bak_file=True)

        if switch:
            print(blue("node {}@{} will cost 0~5 minutes to update the apt and pip sources, please wait."
                       .format(env.user, env.host)))
            sudo("apt-get update")
            print(blue("node {}@{} update the apt and pip sources over".format(env.user, env.host)))
        # print(blue("{} local apt pip update over".format(env.host_string)))

# ------------------------------ pre deal for nodes  start ------------------------------


# ------------ 1.1 generates_origin_node_info start ----------
@hosts("localhost")
@task
@function_tips()
def generates_origin_node_info(switch=True):
    if not switch:
        return

    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        # print(blue("{} init node info origin start ...".format(env.host_string)))
        # log
        pos = "#all nodes as follow"
        file = "../conf/origin_nodes"
        local("sed -i '/{}/{{p;:a;N;$!ba;d}}' {}".format(pos, file))
        # copy the option values append in content after
        if not conf.has_section("node-info-origin") or len(conf.items("node-info-origin")) == 0:
            exit("not exist section node-info-origin or length is  0!")

        node_info_origin_section = "node-info-origin"

        origin_nodes_list = []
        for option in conf.options(section=node_info_origin_section):
            env_password = conf.get(node_info_origin_section, option)
            host_string_password_newpwd = env_password.split(" ")

            if len(host_string_password_newpwd) <=1:
                print(red("error node info"))
                return

            host_string = host_string_password_newpwd[0]
            password = host_string_password_newpwd[1]
            new_env_password = host_string + " " + password
            origin_nodes_list.append(new_env_password)

        # must reverse, because sed is reverse order!
        origin_nodes_list.reverse()
        for origin_node in origin_nodes_list:
            cmd_sudo_add = "sed -i '/{}/a {}' {}".format(pos, origin_node, file)
            local(cmd_sudo_add)

# ------------ 1.1 generates_origin_node_info end ----------


# ------------ 1.2 update_origin_node_password start ----------


@task
@parallel
@function_tips()
def update_origin_node_password(node_info_origin_section="node-info-origin"):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not update_orgin_node_password:
            print(red("password no change"))
            return

        file = "../conf/origin_nodes"
        for option in conf.options(section=node_info_origin_section):
            host_string_password_newpwd = conf.get(node_info_origin_section, option).split(" ")
            host_string = host_string_password_newpwd[0]

            # filter other node
            if host_string != env.host_string:
                continue

            # filter no change password node
            if len(host_string_password_newpwd) != 3:
                print(blue("password no change"))
                return

            old_password = host_string_password_newpwd[1]
            new_password = host_string_password_newpwd[2]

            # print(red("Password old({}) == new({}) {}".format(old_password,
            # new_password, old_password == new_password)))
            if new_password == env.passwords[env.host_string]:
                print(blue("password no change"))
                return

            old_env_password = env.host_string + ".*"
            new_env_password = host_string + " " + new_password

            user = env.user
            echo_info = "change node {:<25} passwod from {} to {}".format(env.host_string,
                                                                          env.passwords[env.host_string],
                                                                          new_password)
            cmd_chpasswd = "{}:{} | sudo chpasswd".format(user, new_password)
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            fun_name = sys._getframe().f_code.co_name
            sudo("echo {}".format(cmd_chpasswd))
            env['passwords'][host_string] = new_password
            print(blue("password changed"))
            local("echo '{} {} {}' >> ../log/init_node_password.log".format(now, fun_name, echo_info))
            local("sed -i 's/{}/{}/g' {}".format(old_env_password, new_env_password, file))


# ------------ 1.2 update_origin_node_password end ----------

# ------------ 1.3 update host name start ----------

@task
@parallel
@function_tips()
def update_node_hostname(use_conf=True, prefix="unichain", start=1, uni=False):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        update_node_host_boolean = conf.getboolean("on-off", "update-node-host", fallback=False)
        if not update_node_host_boolean:
            print(env.host_string)
            print(red("[{}] host no change".format(env.host_string)))
            return

        node_hostname = sudo("hostname")
        if use_conf is True:
            update_node_host_boolean = conf.getboolean("on-off", "update-node-host", fallback=False)
            node_host_section = "node-host"
            if not update_node_host_boolean or not conf.has_section(node_host_section) or len(conf.items(node_host_section)) == 0:
                print(red("[{}] host no change".format(env.host_string)))
                return

            node_info_origin_section  = "node-info-origin"


            for option in conf.options(section=node_info_origin_section):
                env_password = conf.get(node_info_origin_section, option)
                host_string_password_newpwd = env_password.split(" ")
                host_string = host_string_password_newpwd[0]

                # filter other nodes
                if host_string != env.host_string:
                    continue

                if conf.has_option(node_host_section, option):
                    old_hostname = node_hostname
                    new_hostname = conf.get(node_host_section, option)

                    if len(new_hostname) <= 1:
                        print(red("hostname is too short(should >= 2)".format(old_hostname, new_hostname)))
                        return

                    if old_hostname == new_hostname:
                        print(red("hostname old({}) == new({}) no change".format(old_hostname, new_hostname)))
                        return
                    else:
                        sudo("sed -i s/{}/{}/g /etc/hosts 2>/dev/null".format(node_hostname, new_hostname))
                        sudo("sed -i s/{}/{}/g /etc/hostname 2>/dev/null".format(node_hostname, new_hostname))
                        sudo("hostname {}".format(new_hostname))
                        echo_info = "conf change node {} hostname from {} to {}".format(env.host_string, node_hostname,
                                                                                        new_hostname)
                        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        fun_name = sys._getframe().f_code.co_name
                        local("echo '{} {} {}' >> ../log/update_node_hostname.log".format(now, fun_name, echo_info))
                        print(blue(
                            "{} update node host from {} to {}".format(env.host_string, node_hostname, new_hostname)))
        else:
            if uni is True:
                # change all host to prefix
                new_hostname = "{}".format(prefix)
                if node_hostname == new_hostname:
                    print(red("Old hostname({}) == new hostname({}), no update.".format(node_hostname, new_hostname)))
                    return

                sudo("sed -i s/{}/{}/g /etc/hosts 2>/dev/null".format(node_hostname, new_hostname))
                sudo("sed -i s/{}/{}/g /etc/hostname 2>/dev/null".format(node_hostname, new_hostname))
                sudo("hostname {}".format(new_hostname))
                echo_info = "change node {} hostname from {} to {}".format(env.host_string, node_hostname, new_hostname)
                now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                fun_name = sys._getframe().f_code.co_name
                local("echo '{} {} {}' >> ../log/update_node_hostname.log".format(now, fun_name, echo_info))
                print(blue("{} update node host from {} to {}".format(env.host_string, node_hostname, new_hostname)))
            else:
                for i in range(0, len(env['hosts'])):
                    if env.host in public_hosts[i]:
                        new_hostname = "{}{}".format(prefix, i+int(start))
                        if node_hostname == new_hostname:
                            print(red("Old hostname({}) == new hostname({}), no update.".format(node_hostname, new_hostname)))
                            return

                        sudo("sed -i s/{}/{}/g /etc/hosts 2>/dev/null".format(node_hostname, new_hostname))
                        sudo("sed -i s/{}/{}/g /etc/hostname 2>/dev/null".format(node_hostname, new_hostname))
                        sudo("hostname {}".format(new_hostname))
                        echo_info = "change node {} hostname from {} to {}".format(env.host_string, node_hostname, new_hostname)
                        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        fun_name = sys._getframe().f_code.co_name
                        local("echo '{} {} {}' >> ../log/update_node_hostname.log".format(now, fun_name, echo_info))
                        print(blue("{} update node host from {} to {}".format(
                            env.host_string, node_hostname, new_hostname)))

# ------------ 1.3 update host name end ----------


# ------------ 2.1 clear_blockchain_nodes start ----------
@hosts("localhost")
@task
@function_tips()
def clear_blockchain_nodes(pos=None, tips=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not pos:
            pos = "#all nodes as follow"
        file = "../conf/blockchain_nodes"

        if not file or local("test -f {}".format(file)).failed:
            print(red("file {} not exist !".format(file)))
            return

        pos_line_num = local("grep -n '{pos}' {file} |awk 'NR==1'|awk -F ':' '{{print $1}}'"
                            .format(pos=pos, file=file), capture=True)
        if pos_line_num:
            pos_linenum = int(pos_line_num)
            if tips:
                lines = local("sed -n '{},$p' '{}'|wc -l".format(pos_linenum, file), capture=True)
                if int(lines) >= 1:
                    content = local("sed -n '{},$p' '{}' 2>/dev/null".format(pos_linenum+1, file), capture=True)
                    if content:
                        confirm = prompt('Would you like to continue delete the content follows:\n{}\nafter "{}" in file {} ? \
                    (y/n)'.format(content, pos, file),
                                     default='n', validate=r'^y|n$')
                        if confirm == "n":
                            print(red("{} give up delete the content after {} in file {}".format(env.host_string, pos, file)))
                            return
            local("sed -i '{start},$d' {file}".format(start=pos_linenum+1, file=file))
            file_content = local("cat {}".format(file), capture=True)
            print(blue("now {} content, as follows:".format(file)))
            print(yellow(file_content))

    time.sleep(1)
# ------------ 2.1 clear_blockchain_nodes end ----------


# ------------ 2.2 generates_new_user_node_info start ----------
@hosts("localhost")
@task
@function_tips()
def generates_new_user_node_info(switch=True):
    if not switch:
        return

    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        # log
        pos = "#all nodes as follow"
        file = "../conf/blockchain_nodes"
        clear_blockchain_nodes(pos=pos)

        # copy the option values append in content after
        if not conf.has_section("node-info-new-user") or len(conf.items("node-info-new-user")) == 0:
            exit("not exist section node-info-new-user or length is  0!")

        node_info_new_user_section = "node-info-new-user"

        origin_nodes_list = []
        for option in conf.options(section=node_info_new_user_section):
            env_password = conf.get(node_info_new_user_section, option)
            host_string_password_newpwd = env_password.split(" ")

            if len(host_string_password_newpwd) <= 1:
                print(red("error node info"))
                return

            host_string = host_string_password_newpwd[0]
            password = host_string_password_newpwd[1]

            if len(host_string_password_newpwd) == 3:
                print(magenta("[{}] password update, if exist user.".format(host_string)))

                # if exist new user, generate the newest node info
                password = host_string_password_newpwd[2]

            new_env_password = host_string + " " + password
            origin_nodes_list.append(new_env_password)

        # must reverse, because sed is reverse order!
        origin_nodes_list.reverse()
        for origin_node in origin_nodes_list:
            cmd_sudo_add = "sed -i '/{}/a {}' {}".format(pos, origin_node, file)
            local(cmd_sudo_add)

# ------------ 2.2 generates_new_user_node_info end ----------


# please execute 2.1, 2.2 or 2.2 first
# ------------ 2.3 create_new_user start ----------
@task
@parallel
@function_tips()
def create_new_user(node_info_new_user_section="node-info-new-user"):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not create_new_user_boolean:
            print(red("no create new user "))
            return
        # env['passwords']['wangxin@localhost:22'] = "wangxin123"

        file = "../conf/blockchain_nodes"
        for option in conf.options(section=node_info_new_user_section):
            env_password = conf.get(node_info_new_user_section, option).split(" ")
            new_user_host_string = env_password[0]
            new_user_password = env_password[1]

            username_host_port = new_user_host_string.split("@")
            username = username_host_port[0]
            host = username_host_port[1].split(":")[0]
            old_host = env.host
            # filter other node
            if host != old_host:
                continue

            old_env_password = ".*@" + env.host_string.split("@")[1] + ".*"
            new_env_password = new_user_host_string + " " + new_user_password

            cmd_exist_user_info = "grep -w {} {}".format(old_env_password, file)
            sudo(cmd_exist_user_info)

            # print(red(old_env_password + " " + new_env_password))

            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            fun_name = sys._getframe().f_code.co_name

            cmd_exist_user = "cat /etc/passwd|grep -w {}|wc -l".format(username)
            result = sudo(cmd_exist_user)

            if result == "0":
                cmd_useradd = "useradd {} -rm -s /bin/bash ".format(username)
                cmd_chpasswd = "{}:{} | sudo chpasswd".format(username, new_user_password)

                cmd_sudo_remove = "sed -i /^{}.*ALL=/d /etc/sudoers 2>/dev/null".format(username)
                cmd_sudo_add = 'sed -i /^{}.*ALL=/a"{}  ALL=(ALL:ALL) ALL" /etc/sudoers'.format(
                    "root", username)
                sudo(cmd_useradd)
                sudo("echo {}".format(cmd_chpasswd))
                sudo(cmd_sudo_remove)
                sudo(cmd_sudo_add)

                local("echo  '{} {}: node {:<25}  {}' >> ../log/create_new_user.log".format(
                    now, fun_name, env.host_string, cmd_useradd + "\t" + cmd_chpasswd + "\n\t"
                                                    + cmd_sudo_remove + "\t" + cmd_sudo_add))

                local("sed -i 's/{}/{}/g' {}".format(old_env_password, new_env_password, file))
                print(blue("node {} add user {} success".format(env.host_string, username)))
            else:
                # print(red("node {} exist user {}".format(env.host_string, username)))

                # if len == 3 and exist user, update the password in blockchain_nodes file
                if len(env_password) == 3:
                    new_user_new_password = env_password[2]
                    new_env_password = new_user_host_string + " " + new_user_new_password
                    print(magenta("[{}] update the password in blockchain_nodes(exist user).".format(new_user_host_string)))

                exist_user_lines = local("grep '{}' {}|wc -l 2>/dev/null".format(env.host, file),
                                         capture=True)

                if exist_user_lines == "0":
                    local("echo {} >> {}".format(
                        new_env_password, file))
                else:
                    local("sed -i 's/{}/{}/g' {}".format(old_env_password, new_env_password, file))
                local("echo  '{} {}: node {:<25}  {}' >> ../log/create_new_user.log".format(
                    now, fun_name, env.host_string, "use old account {}".format(new_user_host_string)))

# ------------ 2.3 create_new_user end ----------


# because the pip should be in current user folder, so exclude pip update here!
# ------------ 3. update_node apt, third apt start ----------
@task
@parallel
@function_tips()
def node_apt_update(switch=None):
    # with settings(hide('warnings', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        if not switch:
            switch = apt_pip_update_boolean

        update_node_apt()
        update_node_third_apt()

        if switch:
            print(blue("node {}@{} will cost 0~5 minutes to update the apt sources, please wait."
                       .format(env.user, env.host)))
            sudo("apt-get update")



@task
@parallel
@function_tips()
def node_apt_dpkg_update(switch=None):
    # with settings(hide('warnings', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        sudo("apt-get update")
        sudo('apt-get -f install')
        sudo("dpkg --configure -a")


@task
@parallel
@function_tips()
def update_node_apt(switch=None, source=None, codename=None, bak_file=None, bak_filename=None):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        # print(blue("{} update node apt start ...".format(env.host_string)))
        if not switch:
            switch = apt_sources_boolean
        if not source:
            source = apt_source_filename
        if not codename:
            codename = os_codename
        if not bak_file:
            bak_file = apt_bak_file
        if not bak_filename:
            bak_filename = apt_bak_filename

        if switch:
            if source:
                file_path = "../sources/sys_config/apt_pip/{}".format(source)
            else:
                file_path = "../sources/sys_config/apt_pip/sources.list".format(codename)
                # file_path = "../sources/sys_config/apt_pip/{}-sources.list".format(codename)
            if bak_file:
                sudo("cp -f /etc/apt/sources.list /etc/apt/{} 2>/dev/null".format(bak_filename))
            sudo("echo update the node {} sources.list".format(env.host))
            put(file_path, "temp_apt_sources", mode=0o644, use_sudo=True)
            sudo("mv temp_apt_sources /etc/apt/sources.list")
            sudo("chown --reference=/etc/apt /etc/apt/sources.list ")
        # print(green("{} update node apt over".format(env.host_string)))



@task
@parallel
@function_tips()
def update_node_third_apt(switch=None):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings( warn_only=True):
        # print(blue("{} update node third apt start ...".format(env.host_string)))
        if not switch:
            switch = third_apt_sources_boolean

        if switch:
            #TODO rethinkdb
            sudo("echo 'deb http://download.rethinkdb.com/apt trusty main' | "
                 "sudo tee /etc/apt/sources.list.d/rethinkdb.list")
                 # "sudo tee /etc/apt/trusty-sources.list.d/rethinkdb.list")
            sudo("wget -qO- http://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -")

            #TODO collectd
            sudo("echo 'deb http://http.debian.net/debian wheezy-backports-sloppy main contrib non-free' "
                 "| sudo tee /etc/apt/sources.list.d/backports.list")
                 # "| sudo tee /etc/apt/trusty-sources.list.d/backports.list")
            # fixed the GPG Error
            sudo("gpg --keyserver pgpkeys.mit.edu --recv-key  8B48AD6246925553")
            sudo("gpg -a --export 8B48AD6246925553 | sudo apt-key add -")
            sudo("gpg --keyserver pgpkeys.mit.edu --recv-key  7638D0442B90D010")
            sudo("gpg -a --export 7638D0442B90D010 | sudo apt-key add -")

            #TODO nginx

# ------------ 3. update_node apt, third apt end ----------


# update the current user pip, if specify the other user, shouldn`t run here
@task
@parallel
@function_tips()
def update_node_pip(switch=None, source=None, bak_file=None, bak_filename=None):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings( warn_only=True):
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


# ------------ 4. install_base_software start ----------
# Install base software
@task
@parallel
@function_tips()
def install_base_software(switch=None):
    # python pip3 :
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings( warn_only=True):
        # This deletes the dir where "apt-get update" stores the list of packages
        # sudo('rm -rf /var/lib/apt/lists/')
        # # Re-create that directory, and its subdirectory named "partial"
        # sudo('mkdir -p /var/lib/apt/lists/partial/')
        # # Repopulate the list of packages in /var/lib/apt/lists/
        # sudo('apt-get -y update')
        # # Configure all unpacked but unconfigured packages.
        # sudo('dpkg --configure -a')
        # # Attempt to correct a system with broken dependencies in place.
        # sudo('apt-get -y -f install')

        # Install the base dependencies not already installed.

        install_base_software_boolean = conf.getboolean("on-off", "install-base-software", fallback=False)
        if not switch:
            switch = install_base_software_boolean

        if switch is True:
            print(blue("node {}@{} will cost 0~5 minutes to install the base dependencies, please wait."
                       .format(env.user, env.host)))
            sudo('apt-get -y install git gcc g++ python3-dev libssl-dev libffi-dev python3-setuptools \
python3-pip ntp screen')
            sudo('apt-get -y -f install')

            sudo('pip3 install --upgrade pip')
            sudo('pip3 install --upgrade setuptools')
            sudo('pip3 --version')

# ------------ 4. install_base_software end ----------


# ------------ 5. sync_zone_datetime start ----------
@task
@parallel
@function_tips()
def sync_zone_datetime(switch=None, zone_info_file=None, ntpdate_site=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    # with settings(warn_only=True):
        if not switch:
            switch = zone_datetime_boolean
        default_zone_info_file = "../sources/sys_config/zoneinfo_shanghai"

        if switch and not local("test -f {}".format(default_zone_info_file)).failed:
            if not zone_info_file:
                zone_info_file = default_zone_info_file
            sudo("service ntp stop")
            sudo("cp -f /etc/localtime /etc/localtime.bak 2>/dev/null")
            put(zone_info_file, "/etc/localtime", use_sudo=True, mode=0o644)
            sudo("chown --reference=/etc /etc/localtime")
            if not ntpdate_site:
                ntpdate_site = "cn.pool.ntp.org"
            sudo("ntpdate {}".format(ntpdate_site), timeout=60)
            sudo("service ntp start")
            node_time = sudo("date")
            print(blue("[{}] time is {}".format(env.host_string, node_time)))

# ------------ 5. sync_zone_datetime end ----------

# ------------------------------ pre deal for nodes end ------------------------------


# ----------------------------- new user password update start ------------------------------
# update the remote nodes password

@task
@parallel
@function_tips()
def update_new_user_password(node_info_new_user_section="node-info-new-user"):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not update_new_user_node_password:
            print(red("new user password no change"))
            return

        file = "../conf/blockchain_nodes"
        for option in conf.options(section=node_info_new_user_section):
            env_password = conf.get(node_info_new_user_section, option).split(" ")
            new_user_host_string = env_password[0]
            new_user_password = env_password[1]

            username_host_port = new_user_host_string.split("@")
            username = username_host_port[0]
            host = username_host_port[1].split(":")[0]
            old_host = env.host

            # filter other node
            if host != old_host:
                continue

            old_env_password = ".*@" + env.host_string.split("@")[1] + ".*"
            new_env_password = new_user_host_string + " " + new_user_password

            cmd_exist_user_info = "grep -w {} {}".format(old_env_password, file)
            sudo(cmd_exist_user_info)

            # print(red(old_env_password + " " + new_env_password))

            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            fun_name = sys._getframe().f_code.co_name

            cmd_exist_user = "cat /etc/passwd|grep -w {}|wc -l".format(username)
            result = sudo(cmd_exist_user)

            if result != "0" and len(env_password) == 3:
                # if len == 3 and exist user, update the password in blockchain_nodes file

                new_user_new_password = env_password[2]

                # no logon, password cann`t catpute, so must remove the == judge!
                # if new_user_new_password == new_user_password:
                #     print(red("[{}] password no diff, no update".format(new_user_host_string)))

                new_env_password = new_user_host_string + " " + new_user_new_password
                print(magenta("[{}] update the password (exist user).".format(new_user_host_string)))

                echo_info = "change node {:<25} passwod from {} to {}".format(env.host_string,
                                                                              new_user_password,
                                                                              new_user_new_password)
                cmd_chpasswd = "{}:{} | sudo chpasswd".format(username, new_user_new_password)
                now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                fun_name = sys._getframe().f_code.co_name
                sudo("echo {}".format(cmd_chpasswd))
                local("echo '{} {} {}' >> ../log/update_new_user_password.log".format(now, fun_name, echo_info))

            exist_user_lines = local("grep '{}' {}|wc -l 2>/dev/null".format(env.host, file),
                          capture=True)

            if exist_user_lines == "0":
                local("echo {} >> {}".format(
                    new_env_password, file))
            else:
                local("sed -i 's/{}/{}/g' {}".format(old_env_password, new_env_password, file))


@task
@function_tips()
def delete_user(username=None, use_prefix=False):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not username:
            print(red("username not exist!"))
            return

        if len(username) <= 1 or username == "root" or username == ".*":
            print(red("error input username!"))
            return

        if username in public_usernames:
            print(red("You can`t delete the current login user!"))
            return

        cmd_exist_user = "cat /etc/passwd|grep -w {}|wc -l".format(username)
        result = sudo(cmd_exist_user)
        if result != "0":
            if use_prefix is True:
                username = "{}.*".format(username)

            confirm = prompt('Would you like to continue delete user {} ? (y/n)'.format(username),
                             default='n', validate=r'^y|n$')
            if confirm == "n":
                print(red("{} give up delete user {}".format(env.host_string, username)))
                return

            sudo("kill -9 `ps -u {}|grep -v grep |awk 'NR>=2{{print $1}}\'` 2>/dev/null ".format(username))
            cmd_userdel = "userdel -r {} 2>/dev/null".format(username)
            sudo(cmd_userdel)
            cmd_sudo_remove = "sed -i /^{}.*ALL=/d /etc/sudoers 2>/dev/null".format(username)
            sudo(cmd_sudo_remove)
            print(blue("[{}] delete the user {} success".format(env.host_string, username)))
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            fun_name = sys._getframe().f_code.co_name
            local("echo '{} {}: node {:<25} exec {}' >> ../log/node_user.log".format(
                now, fun_name, env.host_string, cmd_userdel + "\t" + cmd_sudo_remove))
        else:
            print(red("[{}] not contains the user {}".format(env.host_string , username)))


@task
@parallel
@function_tips()
def delete_user_parallel(username=None, use_prefix=False):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not username:
            print(red("username not exist!"))
            return

        if len(username) <= 1 or username == "root" or username == ".*":
            print(red("error input username!"))
            return

        if username in public_usernames:
            print(red("You can`t delete the current login user!"))
            return

        cmd_exist_user = "cat /etc/passwd|grep -w {}|wc -l".format(username)
        result = sudo(cmd_exist_user)
        if result != "0":
            if use_prefix is True:
                username = "{}.*".format(username)

            sudo("kill -9 `ps -u {}|grep -v grep |awk 'NR>=2{{print $1}}\'` 2>/dev/null ".format(username))
            cmd_userdel = "userdel -r {} 2>/dev/null".format(username)
            sudo(cmd_userdel)
            cmd_sudo_remove = "sed -i /^{}.*ALL=/d /etc/sudoers 2>/dev/null".format(username)
            sudo(cmd_sudo_remove)
            print(blue("[{}] delete the user {} success".format(env.host_string, username)))
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            fun_name = sys._getframe().f_code.co_name
            local("echo '{} {}: node {:<25} exec {}' >> ../log/node_user.log".format(
                now, fun_name, env.host_string, cmd_userdel + "\t" + cmd_sudo_remove))

        else:
            print(red("[{}] not contains the user {}".format(env.host_string, username)))


@task
@function_tips()
def add_user_to_sudo(username=None):
    """Can`t add the not exist users in os or add the current user again"""
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not username or len(username) <= 1 or username == "root" or username == ".*":
            print(red("error input username !"))
            return

        if username == env.user:
            print(red("You can`t add the current user into sudoers"))
            return

        cmd_exist_user = "cat /etc/passwd|grep -w {}|wc -l".format(username)
        result = sudo(cmd_exist_user)

        if result != "0":
            sudo("sed -i /^{}.*ALL=/d /etc/sudoers 2>/dev/null".format(username))
            sudo("sed -i /^{}.*ALL=/a'{}    ALL=(ALL:ALL) ALL' /etc/sudoers".format("root", username))
        else:
            print(red("the user not exist!"))


@task
@function_tips()
def remove_user_from_sudo(username=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not username or len(username) <= 1 or username == "root" or username == ".*":
            print(red("error input username !"))
            return

        if username == env.user:
            print(red("You can`t remove the current user from sudoers"))
            return

        confirm = prompt('Would you like to continue remove user {} from sudoers ? (y/n)'.format(username),
                         default='n', validate=r'^y|n$')
        if confirm == "n":
            print(red("{} give up removing user {} from sudoers".format(env.host_string, username)))
            return

        sudo("sed -i /^'{}'.*ALL=/d /etc/sudoers".format(username))


@task
@function_tips()
def seek_sudo_user(username=None, num=2):
    with settings(warn_only=True):
        if not username or len(username) <= 1:
            print(red("error input username !"))
            return

        if not num or int(num) <= 1:
            num = 1
        # sudo("grep -n -A {} 'User privilege specification' /etc/sudoers 2>/dev/null".format(num))
        sudo("grep -n -A {} -w '{}' /etc/sudoers 2>/dev/null".format(num, username))


@task
@parallel
@function_tips()
def seek_apt_pip(default="apt", grep=None):
    with settings(warn_only=True):
        apt = False
        pip = False

        if default == "apt":
            apt = True
        if default == "pip":
            pip = True
        if default == "all":
            apt = True
            pip = True
        if apt:
            if not grep:
                sudo("cat /etc/apt/sources.list ")
            else:
                sudo("grep '{}' /etc/apt/sources.list 2>/dev/null".format(grep))
        if pip:
            sudo(blue("cat ~/.pip/pip.conf 2>/dev/null"))


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
# ----------------------------- node password, host, user functions  end ------------------------------


# ------------------------------ other deals  start ------------------------------
def update_conf_value(section, key, value, filename=cluster_info_filename):
    if conf.has_section(section):
        if conf.has_option(section, key):
            conf.set(section, key, value=value)
            conf.write(open(name=filename, mode="w"))


def remove_conf_key(section, key, filename=cluster_info_filename):
    if conf.has_section(section):
        if conf.has_option(section, key):
            conf.remove_option(section, key)
            conf.write(open(name=filename, mode="w"))


def read_conf_value(section, key, default=None):
    if conf.has_section(section):
        return conf.get(section, key, fallback=default)
    return None

# ------------------------------ other deals  end------------------------------


# --------------------------------- unichain related install start -------------------------------------

@task
@parallel
@function_tips()
def init_all_nodes(service_name=None, setup_name=None, shred=False, times=3, show=False,
                   only_code=True, config_del=False):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(hide('running'), warn_only=True):
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

        if shred:
            if not times or int(times) <= 1:
                times = 2
            if show:
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
            if config_del:
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

        if  not only_code:
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



# python3,pip,pip3
@task
@function_tips()
def stop_python():
    with settings(warn_only=True):
        sudo("killall -9 python python3 pip pip3 2>/dev/null")


# ---------------------------------  unichain related install end ---------------------------------------



################################################################
# Security / Firewall Stuff
################################################################

@task
@function_tips()
def harden_sshd():
    """Security harden sshd."""

    # Enable password authentication
    sed('/etc/ssh/sshd_config',
        '#PasswordAuthentication yes',
        'PasswordAuthentication yes',
        use_sudo=True)

    # Deny root login
    sed('/etc/ssh/sshd_config',
        'PermitRootLogin yes',
        'PermitRootLogin no',
        use_sudo=True)


@task
@function_tips()
def disable_root_login():
    """Disable `root` login for even more security. Access to `root` account
    is now possible by first connecting with your dedicated maintenance
    account and then running ``sudo su -``.
    """
    sudo('passwd --lock root')


@task
@function_tips()
def set_fw():
    # snmp
    sudo('iptables -A INPUT -p tcp --dport 161 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 161 -j ACCEPT')
    # dns
    sudo('iptables -A OUTPUT -p udp -o eth0 --dport 53 -j ACCEPT')
    sudo('iptables -A INPUT -p udp -i eth0 --sport 53 -j ACCEPT')
    # rethinkdb
    sudo('iptables -A INPUT -p tcp --dport 28015 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 28015 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 29015 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 29015 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 8080 -j ACCEPT')
    sudo('iptables -A INPUT -i eth0 -p tcp --dport 8080 -j DROP')
    sudo('iptables -I INPUT -i eth0 -s 127.0.0.1 -p tcp --dport 8080 -j ACCEPT')
    # save rules
    sudo('iptables-save >  /etc/sysconfig/iptables')




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
        if show:
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

