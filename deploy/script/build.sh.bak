#!/bin/bash
#####################################
##  Install the deployment portal  ##
#####################################

mkdir -p ../log

function echo_green
{
    local content=$@
    echo -e "\033[1;32m${content}\033[0m"
    return 0
}

function usage
{
    echo_green "
Usage:
    $0 [\$1]
Options:
    h|-h|help|-help usage help
    env_check    before setup, check tools already in env
    first_setup  \$1: nostart, if set \$1,it cann't start nodes after setup
                 first setup:
                    sence: first setup use
                    op:    a.install base tools|depends libs|rethinkdb|bigchaindb|unichain
                           b.configure rethinkdb|bigchaindb|unichain
                           c.start cluster nodes server
    update       \$1: nostart, if set \$1,it cann't start nodes after update
                    update setup:
                         sence: a. when unichain pro  is updated
                                b. when unichain conf is updated
                                c. when update fail, need rollback
                         op:    a.update unichain
                                b.reconfigure rethinkdb|bigchaindb|unichain
                                c.restart cluster nodes server
    server_check     after setup, check servers in cluster nodes are running
    check_log        获取所有节点log信息
    update_config    更新配置信息
    init_env         初始化各节点所需环境
    add_node         增加节点
    delete_node      删除节点
    start_all        start all cluster nodes
    stop_all         stop  sll cluster nodes
    start_node       start signal cluster node
    stop_node        stop  signal cluster node
    install_node     install or reinstall single cluster node
    uninstall        uninstall unichain
    unichain_init    update or downnload the unichain
                        usage:
                            -h  使用帮助
                            -g  使用git方式对代码进行更新打包
                            -b  git方式操作对应的分支
                            -s  下载代码仓库地址
                            -u  更新代码，如果不存在则使用git方式下载代码
                            -p  对代码进行打包，生成unichain-archive.tar.gz，并copy至sources下
                                如果选择git方式打包，则使用git archive, 否则默认为tar & gzip 打包
                            -d  删除下载的unichain代码及生成的unichain-archive.tar.gz文件
    "
    return 0
}

chmod +755 *.sh 2>/dev/null
chmod +755 *.py 2>/dev/null

case $1 in
    h|help|-h|-help)
        usage
    ;;
    env_check)
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    first_setup)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./run_first_setup.sh $str_param | tee ../log/run_first_setup.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    update)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./run_update.sh $str_param | tee ../log/run_update.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    server_check)
        ./run_server_check.sh | tee ../log/run_server_check.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    start_all)
        ./clustercontrol.sh start | tee ../log/clustercontrol_start.log
        ./run_env_check.sh | tee ../log/run_env_check.log
        ./run_server_check.sh | tee ../log/run_server_check.log 
    ;;
    update_config)
        ./run_update_config.sh  | tee ../log/run_update_config.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    init_env)
        ./init_node_env.sh  | tee ../log/init_node_env.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    add_node)
        ./modify_unichain_node.sh  | tee ../log/modify_unichain_node.log
        ./add_run_env_check.sh | tee ../log/add_run_env_check.log
    ;;
    check_log)
        ./get_node_log.sh  $2| tee ../log/get_node_log.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    delete_node)
        ./delete_unichain_node.sh  | tee ../log/delete_unichain_node.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    stop_all)
        ./clustercontrol.sh stop | tee ../log/clustercontrol_stop.log
        ./run_server_check.sh | tee ../log/run_server_check.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    start_node)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./startnode.sh $str_param | tee ../log/startnode.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    stop_node)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./stopnode.sh $str_param | tee ../log/stopnode.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    install_node)
        str_param=`echo $@|awk '{for(i=3;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./install_node.sh $str_param | tee ../log/install_node.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    uninstall)
        ./run_uninstall.sh | tee ../log/uninstall.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    unichain_init)
         str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./unichain_init.sh $str_param | tee ../log/unichain_init.log
        ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
     drop)
       ./unichain_rethinkdb_drop.sh | tee ../log/unichain_rethinkdb_drop.log
       ./run_env_check.sh | tee ../log/run_env_check.log
    ;;
    *)
        usage
    ;;
esac

exit 0
