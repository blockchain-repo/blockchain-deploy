
# -*- coding: utf-8 -*-

"""A Fabric fabfile with functionality to prepare, install, and configure
UnichainDB, including its storage backend (RethinkDB).
"""


from __future__ import with_statement, unicode_literals

import sys
import re

import time

from fabric.colors import red, green, blue, yellow, magenta, cyan
from fabric.api import sudo, cd, env, hosts, local, runs_once
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put, get, prompt
from fabric.context_managers import settings, hide

from configparser import ConfigParser

from hostlist_nginx import public_dns_names,public_hosts,public_pwds,public_host_pwds, public_usernames

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


#  pip 更新开关
pip_sources_switch = conf.get("on-off", "pip-sources", fallback="off")
pip_sources_boolean = conf.getboolean("on-off", "pip-sources", fallback=False)
pip_filename = conf.get("pip-sources", "pip_filename", fallback="pip.conf")
pip_bak_file = conf.get("pip-sources", "bak_file", fallback=True)
pip_bak_filename = conf.get("pip-sources", "bak_filename", fallback="pip.conf.bak")

# 功能开关属性
# nginx install or not
install_nginx_switch = conf.get("on-off", "nginx-node", fallback="off")
# install_nginx_boolean = conf.getboolean("on-off", "nginx-node", fallback=False)

# base nginx dir
base_nginx_dir = "/nginx"


# if conf.has_section("nginx-base_conf") and len(conf.items("nginx-base_conf")) >= 1:
#     base_nginx_dir = conf.get("nginx-base_conf", "base_nginx_dir", fallback=base_nginx_dir)

# nginx-base_conf
update_nginx_config = False
if conf.has_section("nginx-base_conf") and len(conf.items("nginx-base_conf")) >= 1:
    update_nginx_config = True
# nginx version
nginx_version = conf.get("nginx-base_conf", "version", fallback="1.10.3")
nginx_file_name = "nginx-{}".format(nginx_version)
keepalived_version = conf.get("keepalived-base_conf", "version", fallback="1.3.5")
keepalived_file_name = "keepalived-{}".format(keepalived_version)

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


# ------------ 1.1 clear_nginx_nodes start ----------
@hosts("localhost")
@task
@function_tips()
def clear_nginx_nodes(pos=None, tips=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not pos:
            pos = "#all nodes as follow"
        file = "../conf/nginx_nodes"

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

# ------------ 1.1 clear_nginx_nodes end ----------


# ------------ 1.2 generate_nginx_node_info start ----------
@hosts("localhost")
@task
@function_tips()
def generate_nginx_node_info(switch=True):
    if not switch:
        return

    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        # log
        pos = "#all nodes as follow"
        file = "../conf/nginx_nodes"
        clear_nginx_nodes(pos=pos)

        # copy the option values append in content after
        if not conf.has_section("node-info-origin") or len(conf.items("node-info-origin")) == 0:
            exit("not exist section node-info-origin or length is  0!")

        nginx_node_section = "nginx-node"

        nginx_nodes_list = []
        for option in conf.options(section=nginx_node_section):
            env_password = conf.get(nginx_node_section, option)
            host_string_password = env_password.split(" ")

            if len(host_string_password) <= 1:
                print(red("error node info"))
                return

            nginx_nodes_list.append(env_password)

        # must reverse, because sed is reverse order!
        nginx_nodes_list.reverse()
        for nginx_node in nginx_nodes_list:
            cmd_sudo_add = "sed -i '/{}/a {}' {}".format(pos, nginx_node, file)
            local(cmd_sudo_add)

# ------------ 1.2 generates_new_user_node_info end ----------

# ------------ 2. update_node pip start ----------


# update the current user pip, if specify the other user, shouldn`t run here
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

# ------------ 2. update_node pip end ----------

# ------------------------ 3. create nginx user and grop sart -----------
@task
@parallel
@function_tips()
def create_nginx_user_group(switch=None, user=None, group=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if env.host == "localhost":
            return

        if not user:
            user = "nginx"
            group = "nginx"

        cmd_exist_user = "cat /etc/passwd|grep -w {}|wc -l".format(user)
        result = sudo(cmd_exist_user)

        if result == "0":
            sudo("groupadd {group}".format(group=group))
            sudo("useradd {user} -g {group} -s /usr/sbin/nologin -M".format(user=user, group=group))
            print(yellow("user:{}, group:{} add success!".format(user, group)))
        else:
            print(red("user:{}, group:{} exist!".format(user, group)))

@task
@parallel
@function_tips()
def delete_nginx_user_group(switch=None, user=None, group=None):
    if not user:
        user = "nginx"
        group = "nginx"

    sudo("deluser {user}".format(user=user))
    # sudo("delgroup {group}".format(group=group))

# ------------------------ 3. create nginx user and grop end -----------


# ------------ 4.1 download_nginx to local start ----------
@runs_once
@hosts("localhost")
@task
@function_tips()
def download_nginx(switch=None, version=None, delete=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not version:
            version = nginx_version
            # version = "1.11.10"

        if not version:
            version = "1.10.3"

        # check if exist the nginx-*.tar.gz
        nginx_app_name = "nginx-{version}.tar.gz".format(version=version)
        nginx_app_dir = "../sources/software"

        if delete:
            local("rm -rf {}/{}".format(nginx_app_dir, nginx_app_name))

        if local("test -f {}/{}".format(nginx_app_dir, nginx_app_name)).failed:
            download_url = "http://nginx.org/download/{}".format(nginx_app_name)
            local("wget '{}' -c -P {}/".format(download_url, nginx_app_dir))
        else:
            print(red("{} already exist in {}".format(nginx_app_name, nginx_app_dir)))


# ------------ 4.2 send_nginx to remote nodes start ----------
@task
@parallel
@function_tips()
def send_nginx(version=None, delete=None, decompress=True):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        if not version:
            version = nginx_version
            # version = "1.11.10"

        # check if exist the nginx-*.tar.gz
        nginx_app_name = "nginx-{version}.tar.gz".format(version=version)
        nginx_app_dir = "nginx-{version}".format(version=version)
        local_nginx_app_dir = "../sources/software"
        nginx_dir = "~/nginx"

        if delete:
            sudo("rm -rf {}".format(nginx_dir))

        if run("test -d {}".format(nginx_dir)).failed:
            sudo("mkdir -p {}".format(nginx_dir), user=env.user, group=env.user)
        put("{}/{}".format(local_nginx_app_dir, nginx_app_name), nginx_dir,  mode=0o644, use_sudo=True)

        if decompress:
            with cd("{}".format(nginx_dir)):
                sudo("tar -xvf {}".format(nginx_app_name))
                sudo("chown {0}:{0} -R {1}".format(env.user, nginx_app_dir))


@task
@function_tips()
def delete_nginx_files():
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        nginx_dir = "~/nginx"
        confirm = prompt('Would you like to continue delete nginx files in {}? (y/n)'.format(nginx_dir),
                         default='n', validate=r'^y|n$')
        if confirm == "n":
            print(red("{} give up delete nginx files in {}".format(env.host_string, nginx_dir)))
            return
        sudo("rm -rf {}".format(nginx_dir))


# ------------ 4.3 remote install_nginx_dependency start ----------
@task
@parallel
@function_tips()
def install_nginx_dependency(switch=None):
    # 安装nginx的依赖包 zlib pcre openssl（可以源码安装也可以直接系统安装）
    with settings(hide('stdout'), warn_only=True):
        sudo("apt-get install -y libpcre3 libpcre3-dev zlib1g-dev libssl-dev build-essential")


# ------------ 4.4 remote compile_nginx start ----------
@task
@parallel
@function_tips()
def compile_nginx(path=None, filename=None):
    if not filename:
        filename = nginx_file_name
    if not path:
        path = "~/nginx/{}".format(filename)
    with cd("{}".format(path)):
        print(yellow(path))
        base_nginx_dir = "/nginx"

        configure = "./configure " \
                    "--prefix={0} " \
                    "--user={1} " \
                    "--group={1} " \
                    "--sbin-path={0}/sbin/nginx " \
                    "--conf-path={0}/conf/nginx.conf " \
                    "--error-log-path={0}/log/error.log " \
                    "--http-log-path={0}/log/access.log " \
                    "--pid-path={0}/run/nginx.pid " \
                    "--lock-path={0}/lock/nginx.lock " \
                    "--with-http_dav_module " \
                    "--with-http_ssl_module " \
                    "--with-http_stub_status_module " \
                    "--with-http_gzip_static_module " \
                    "--http-client-body-temp-path={0}/tmp/nginx/client/ " \
                    "--http-proxy-temp-path={0}/tmp/nginx/proxy/ " \
                    "--http-fastcgi-temp-path={0}/tmp/nginx/fastcgi/ " \
                    "--http-uwsgi-temp-path={0}/tmp/nginx/uwsgi/ " \
                    "--http-scgi-temp-path={0}/tmp/nginx/scgi/ " \
                    "--with-http_realip_module " \
                    "--with-ipv6 " \
                    "--with-debug " \
                    "--with-http_sub_module ".format(base_nginx_dir, "nginx")
        sudo(configure)


# ------------ 4.5 remote make and install_nginx start ----------
@task
@parallel
@function_tips()
def make_install_nginx(filename=None):
    if not filename:
        filename = nginx_file_name
    path = "~/nginx/{}".format(filename)
    base_nginx_dir = "/nginx"

    with cd("{}".format(path)):
        sudo("rm -rf {base_nginx_dir}".format(base_nginx_dir=base_nginx_dir))
        sudo("mkdir -p {base_nginx_dir}".format(base_nginx_dir=base_nginx_dir))
        sudo("mkdir -p {base_nginx_dir}/tmp/nginx/{{client,proxy,fastcgi,uwsgi,scgi}}"
             .format(base_nginx_dir=base_nginx_dir))

        # nginx related script
        sudo("mkdir -p {base_nginx_dir}/script".format(base_nginx_dir=base_nginx_dir))

        sudo("mkdir -p {base_nginx_dir}/conf/sites-enabled".format(base_nginx_dir=base_nginx_dir))
        # enable: default -> /etc/nginx/sites-available/default
        # ln -s /etc/nginx/sites-available/default default
        sudo("mkdir -p {base_nginx_dir}/conf/sites-available".format(base_nginx_dir=base_nginx_dir))
        sudo("mkdir -p {base_nginx_dir}/cache/nginx/temp".format(base_nginx_dir=base_nginx_dir))
        sudo("mkdir -p {base_nginx_dir}/cache/nginx/cache".format(base_nginx_dir=base_nginx_dir))

        sudo("make && make install")

        # sudo("chown -R {0}:{0}  {1}".format("nginx", base_nginx_dir))


# ------------ 4.5 remote add_nginx_service start ----------
@task
@parallel
@function_tips()
def config_nginx_service(init_file=None):
    with settings(warn_only=True):
        # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):

        # nginx_group = "nginx"
        target_file = "/etc/init.d/nginx"

        if not init_file:
            init_file = "../sources/sys_config/nginx/base_conf/nginx-init.sh"

        if local("test -f {}".format(init_file)).failed:
            print(red("{} not exist".format(init_file)))
            return

        put(init_file, target_file, mode=0o755, use_sudo=True)
        sudo("chown {0}:{0} -R {1}".format("root", "/etc/init.d/nginx"))

        sudo("ln -fs {}/sbin/nginx /usr/bin/nginx".format(base_nginx_dir))
        sudo("update-rc.d -f nginx remove")
        sudo("update-rc.d nginx defaults")
        sudo("service nginx restart")


# ------------ 5. generate_nginx_server_conf start ----------
@hosts("localhost")
@task
@function_tips()
def generate_nginx_server_conf(filename=None, server_port=None, delete=None):
    with settings(hide('running', 'stdout'), warn_only=True):
    # with settings(warn_only=True):
        if not filename or len(filename) <= 3:
            print(red("filename error(length must >= 4)!"))
            return
        if not server_port:
            print(red("server_port error!"))
            return

        nginx_server_tempfile = "../conf/template/nginx/nginx-server.template"
        server_file = "../sources/sys_config/nginx/base_conf/{}".format(filename)

        if local("test -f {}".format(server_file)).failed:
            local("cp {} {}".format(nginx_server_tempfile, server_file))
            local("sed -i 's/{{UPSTREAM_NAME}}/{}/' {}".format(filename, server_file))
            local("sed -i 's/{{SERVER_PORT}}/{}/' {}".format(server_port, server_file))
            print(yellow("please specify the upstream server mannualy in {}".format(server_file)))
        else:
            if delete:
                confirm = prompt('Would you like to continue delete nginx server conf {} ? (y/n)'.format(server_file),
                                 default='n', validate=r'^y|n$')
                if confirm == "n":
                    print(red("{} give up delete nginx server conf  {}".format(env.host_string, server_file)))
                    return
                else:
                    local("rm -rf {}".format(server_file))
                    local("cp {} {}".format(nginx_server_tempfile, server_file))
                    local("sed -i 's/{{UPSTREAM_NAME}}/{}/' {}".format(filename, server_file))
                    local("sed -i 's/{{SERVER_PORT}}/{}/' {}".format(server_port, server_file))
            print(yellow("please specify the upstream server mannualy in {}".format(server_file)))


@hosts("localhost")
@task
@function_tips()
def delete_local_nginx_server_conf(filename=None):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        if not filename or len(filename) <= 3:
            print(red("filename error(length must >= 4)!"))
            return

        server_file = "../sources/sys_config/nginx/base_conf/{}".format(filename)

        if local("test -f {}".format(server_file)).failed:
            return

        confirm = prompt('Would you like to continue delete local nginx server conf {} ? (y/n)'.format(server_file),
                         default='n', validate=r'^y|n$')
        if confirm == "n":
            print(red("{} give up delete local nginx server conf {}".format(env.host_string, server_file)))
            return
        else:
            local("rm -rf {}".format(server_file))


# ------------ 6. configure nginx start ----------
@task
@parallel
@function_tips()
def config_nginx_conf(filename=None):
    with settings(hide('running', 'stdout'), warn_only=True):
        local_nginx_conf_dir = "../sources/sys_config/nginx/base_conf"
        if not filename:
            filename = "nginx.conf"

        local_nginx_conf_file = "{}/{}".format(local_nginx_conf_dir, filename)
        if local("test -f {}".format(local_nginx_conf_file)).failed:
            print(red("not exist {}".format(local_nginx_conf_file)))
            return

        nginx_dir = "/nginx"
        nginx_conf = "{}/conf/nginx.conf".format(nginx_dir)
        bak_nginx_conf = "{}/conf/nginx.conf.bak".format(nginx_dir)

        sudo("mv {} {}".format(nginx_conf, bak_nginx_conf))
        put(local_nginx_conf_file, nginx_conf, mode=0o755, use_sudo=True)
        sudo("chown {0}:{0} -R {1}".format("root", nginx_conf))
        sudo("service nginx reload")


@task
@parallel
@function_tips()
def delete_nginx_server_config(filename=None):
    with settings(hide('stdout'), warn_only=True):
    # with settings(warn_only=True):
        if not filename or len(filename) <= 3:
            print(red("filename error(length must >= 4)!"))
            return

        nginx_dir = "/nginx"
        sudo("service nginx stop")
        sudo("rm -rf {}/conf/sites-available/{}".format(nginx_dir, filename))
        sudo("rm -rf {}/conf/sites-enabled/{}".format(nginx_dir, filename))
        sudo("service nginx restart")


@task
@parallel
@function_tips()
def config_nginx_server(filename=None):
    with settings(hide('running', 'stdout'), warn_only=True):
    # with settings(warn_only=True):
        local_nginx_server_dir = "../sources/sys_config/nginx/base_conf"

        servers_list = local("ls {} |awk '{{print $0}}'".format(local_nginx_server_dir), capture=True)
        servers_list = servers_list.split("\n")

        if len(servers_list) == 0:
            print(red("please execute generate_nginx_server_conf to generate the nginx_server files"))
            return

        if not filename or filename not in servers_list:
            print(red("param filename must in {}".format(servers_list)))
            return

        local_nginx_server_file = "{}/{}".format(local_nginx_server_dir, filename)

        nginx_dir = "/nginx"
        nginx_available_server_file = "{}/conf/sites-available/{}".format(nginx_dir, filename)
        nginx_enabled_server_file = "{}/conf/sites-enabled/{}".format(nginx_dir, filename)

        nginx_enabled_dir = "{}/conf/sites-enabled".format(nginx_dir)
        # sudo("rm -rf {}".format(nginx_available_server_file))

        put(local_nginx_server_file, nginx_available_server_file, mode=0o755, use_sudo=True)

        with cd(nginx_enabled_dir):
            sudo("rm -rf {}".format(nginx_enabled_server_file))
            sudo("ln -sf {source} {target}".format(source=nginx_available_server_file, target=filename))
        sudo("chown {0}:{0} -R {1}".format("root", nginx_available_server_file))
        sudo("chown {0}:{0} -R {1}".format("root", nginx_enabled_server_file))
        sudo("service nginx reload")


# ------------ 6. uninstall nginx start ----------
@task
@parallel
@function_tips()
def uninstall_nginx():
    # with settings(hide('running', 'stdout'), warn_only=True):
    with settings(hide('running'), warn_only=True):
        if not base_nginx_dir or base_nginx_dir != "/nginx":
            print(red("nginx base dir error, should be nginx!"))
            return

        sudo("service nginx stop")
        sudo("update-rc.d -f nginx remove")
        sudo("rm -rf /etc/init.d/nginx")
        sudo("rm -rf {}".format(base_nginx_dir))


# ------------ 7. nginx common ops ----------
@task
@parallel
@function_tips()
def nginx_ops(op=None):
    with settings(hide('running', 'stdout'), warn_only=True):
    # with settings(warn_only=True):
        ops_list = ["start", "stop", "restart", "reload", "force-reload", "status", "test"]
        if not op or op not in ops_list:
            print(red("op must in {}".format(ops_list)))
            return
        result = sudo("service nginx {}".format(op))
        print(yellow(result))


@task
@parallel
@function_tips()
def config_nginx_log_cut(delete=None):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        conf_dir = "../sources/sys_config/nginx/base_conf"
        filename = "nginx_log_cut_days.sh"
        conf_file = "{}/{}".format(conf_dir, filename)
        remote_conf_file = "/nginx/script/{}".format(filename)

        if delete:
            sudo("rm -rf {}".format(conf_file))

        put(conf_file, remote_conf_file, mode=0o755, use_sudo=True)
        sudo("chown {0}:{0} -R {1}".format("root", remote_conf_file))


def reg_utils(reg, str=None):
    if not str:
        # print(red("input should not be empty!"))
        return False
    result = re.match(reg, str)
    # print(red(result))
    if not result:
        return False
    else:
        return True


@task
@parallel
@function_tips()
def config_nginx_log_crontab(m=None, h=None, dom=None, mon=None, dow=None, user=None):
    with settings(hide('stdout'), warn_only=True):
        # minute - 从0到59的整数
        m_reg = r"[0-5]?[0-9]$"
        # hour - 从0到23的整数
        h_reg = r"1?[0-9]$|(2[0-3])$"
        # day - 从1到31的整数 (必须是指定月份的有效日期)
        dom_reg = r"[1-2]?[1-9]$|[1-3][0-1]$"
        # month - 从1到12的整数 (或如Jan或Feb简写的月份)
        mon_reg = r"[1-9]$|1[1-2]$"
        # dayofweek - 从0到7的整数，0或7用来描述周日 (或用Sun或Mon简写来表示)
        dow_reg = r"[0-7]$"
        # command - 需要执行的命令(可用as ls /proc >> /tmp/proc或 执行自定义脚本的命令)

        if not reg_utils(m_reg, m):
            m = "*"
        else:
            m = int(m)

        if not reg_utils(h_reg, h):
            h = "*"
        else:
            h = int(h)

        if not reg_utils(dom_reg, dom):
            dom = "*"
        else:
            dom = int(dom)

        if not reg_utils(mon_reg, mon):
            mon = "*"
        else:
            mon = int(mon)

        if not reg_utils(dow_reg, dow):
            dow = "*"
        else:
            dow = int(dow)

        # not exist?
        if not user:
            user = "root"
        else:
            cmd_exist_user = "cat /etc/passwd|grep -w {}|wc -l".format(user)
            result = sudo(cmd_exist_user)
            if result == "0":
                print(red("[{}] not exist the user {}".format(env.host_string, user)))
                return
        # m h dom mon dow user  command
        # vi /etc/crontab
        script_file_name = "nginx_log_cut_days.sh"
        script_file = "/nginx/script/{}".format(script_file_name)
        crontab_script = "bash {} 2>/dev/null".format(script_file)
        # command = " 0 0    * * *   root    bash {} 2>/dev/null".format(script_file)
        command = "{:<2} {:<2}   {} {} {}   {}   {}".format(
            m, h, dom, mon, dow, user, crontab_script)

        # command = "{m} {h}     {dom} {mon} {dow}   {user}   {crontab_script}".format(
        #     m=m, h=h, dom=dom, mon=mon, dow=dow, user=user, crontab_script=crontab_script)

        sudo("sed -i /'{}'/d /etc/crontab".format(script_file_name))
        sudo("echo '{}' >> /etc/crontab".format(command))
        sudo("/etc/init.d/cron restart")


# ----------------------------- Install keepalived start ------------------------------
@runs_once
@hosts("localhost")
@task
@function_tips()
def download_keepalived(version=None, delete=None):
    with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        if not version:
            version = keepalived_version
            # version = "1.3.5"

        if not version:
            version = "1.3.5"

        # check if exist the nginx-*.tar.gz
        keepalived_app_name = "keepalived-{version}.tar.gz".format(version=version)
        keepalived_app_dir = "../sources/software"

        if delete:
            local("rm -rf {}/{}".format(keepalived_app_dir, keepalived_app_name))

        if local("test -f {}/{}".format(keepalived_app_dir, keepalived_app_name)).failed:
            download_url = "http://www.keepalived.org/software/{}".format(keepalived_app_name)
            local("wget '{}' -c -P {}/".format(download_url, keepalived_app_dir))
        else:
            print(red("{} already exist in {}".format(keepalived_app_name, keepalived_app_dir)))

@task
@parallel
@function_tips()
def install_keepalived_dependency():
    # 安装nginx的依赖包 zlib pcre openssl（可以源码安装也可以直接系统安装）
    with settings(hide('stdout'), warn_only=True):
        sudo("apt-get install -y daemon")


@task
@parallel
@function_tips()
def send_keepalived(version=None, delete=None, decompress=True):
    # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
    with settings(warn_only=True):
        if not version:
            version = keepalived_version
            # version = "1.3.5"

        # check if exist the keepalived-*.tar.gz
        keepalived_app_name = "keepalived-{version}.tar.gz".format(version=version)
        keepalived_app_dir = "keepalived-{version}".format(version=version)
        local_keepalived_app_dir = "../sources/software"
        keepalived_dir = "~/keepalived"

        if delete:
            sudo("rm -rf {}".format(keepalived_dir))

        if run("test -d {}".format(keepalived_dir)).failed:
            sudo("mkdir -p {}".format(keepalived_dir), user=env.user, group=env.user)
        put("{}/{}".format(local_keepalived_app_dir, keepalived_app_name), keepalived_dir, mode=0o644, use_sudo=True)

        if decompress:
            with cd("{}".format(keepalived_dir)):
                sudo("tar -xvf {}".format(keepalived_app_name))
                sudo("chown {0}:{0} -R {1}".format(env.user, keepalived_app_dir))


@task
@parallel
@function_tips()
def compile_keepalived(path=None, filename=None):
    if not filename:
        filename = keepalived_file_name
    if not path:
        path = "~/keepalived/{}".format(filename)
    with cd("{}".format(path)):
        print(yellow(path))
        base_keepalived_dir = "/keepalived"

        configure = "./configure " \
                    "--prefix={0} ".format(base_keepalived_dir)
        sudo(configure)


@task
@parallel
@function_tips()
def make_install_keepalived(filename=None):
    if not filename:
        filename = keepalived_file_name
    path = "~/keepalived/{}".format(filename)
    base_keepalived_dir = "/keepalived"

    with cd("{}".format(path)):
        sudo("rm -rf {base_keepalived_dir}".format(base_keepalived_dir=base_keepalived_dir))
        sudo("mkdir -p {base_keepalived_dir}".format(base_keepalived_dir=base_keepalived_dir))

        # keepalived related script
        sudo("mkdir -p {base_keepalived_dir}/script".format(base_keepalived_dir=base_keepalived_dir))
        sudo("make && make install")


@task
@parallel
@function_tips()
def config_keepalived_service(init_file=None):
    with settings(warn_only=True):
        # with settings(hide('warnings', 'running', 'stdout'), warn_only=True):
        version = keepalived_version
        target_file = "/etc/init.d/keepalived"
        sudo("ln -sf /keepalived/sbin/keepalived /usr/sbin/")

        if not init_file:
            init_file = "../sources/sys_config/keepalived/base_conf/keepalived-init.sh"

        if local("test -f {}".format(init_file)).failed:
            print(red("{} not exist".format(init_file)))
            return

        sudo("rm -rf /etc/init.d/keepalived")
        put(init_file, target_file, mode=0o755, use_sudo=True)
        # sudo("cp ~/keepalived/keepalived-{}/keepalived/etc/init.d/keepalived /etc/init.d/".format(version))

        sudo("sed -i s/'daemon.*keepalived.*'/'\/etc\/init.d\/nginx start \\n"
             "\\tdaemon keepalived start'/g "
             " /etc/init.d/keepalived")
        sudo("sed -i s/'\/etc\/rc.d\/init.d\/functions'/'\/lib\/lsb\/init-functions'/ /etc/init.d/keepalived")

        #  touch：cannot tounch /var/lock/subsys/sshd：no such file or directory
        sudo("mkdir /var/lock/subsys")
        sudo("sed -i '/mkdir \/var\/lock\/subsys/d' /etc/rc.local")
        sudo("sed -i '/exit/i mkdir /var/lock/subsys' /etc/rc.local")

        sudo("mkdir /etc/sysconfig")
        sudo("mkdir /etc/keepalived")
        sudo("cp -f /keepalived/etc/sysconfig/keepalived /etc/sysconfig/")
        sudo("cp -f /keepalived/etc/keepalived/keepalived.conf /etc/keepalived/")

        # sudo("update-rc.d -f keepalived remove")
        sudo("update-rc.d -f keepalived defaults")
        sudo("service keepalived restart")









# ----------------------------- new user password update start ------------------------------
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

