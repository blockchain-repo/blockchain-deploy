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

    ## 服务检查
    env_check               环境检查
    check_log               获取所有节点日志信息
    drop                    初始化数据库
    detect_unichain         检测unichain及rethinkdb集群信息

    ## 服务部署
    first_install           第一次安装unichain
    add_node                增加节点
    delete_node             删除节点

    ## 服务升级
    update                  更新unichain
    update_config           更新unichain配置

    ## 服务集群控制
    start                   启动rethinkdb和unichain
    stop                    停止rethinkdb和unichain
    restart                 重启rethinkdb和unichain

    ## rethinkdb集群控制
    start_rethinkdb         启动rethinkdb
    stop_rethinkdb          停止rethinkdb
    restart_rethinkdb       重启rethinkdb

    ## 区块链服务控制
    start_unichain          启动unichain
    stop_unichain           停止unichain
    restart_unichain        重启unichain
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
    first_install)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./run_first_setup.sh $str_param | tee ../log/run_first_setup.log
    ;;
    update)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./run_update.sh $str_param | tee ../log/run_update.log
    ;;
    server_check)
        ./run_server_check.sh | tee ../log/run_server_check.log
    ;;
    detect_unichain)
        ./run_server_check.sh | tee ../log/run_server_check.log
    ;;
    start)
        ./clustercontrol.sh start | tee ../log/clustercontrol_start.log
    ;;
    update_config)
        ./run_update_config.sh  | tee ../log/run_update_config.log
    ;;
    init_env)
        ./init_node_env.sh  | tee ../log/init_node_env.log
    ;;
    add_node)
        ./modify_unichain_node.sh  | tee ../log/modify_unichain_node.log
        ./add_run_env_check.sh | tee ../log/add_run_env_check.log
    ;;
    check_log)
        ./get_node_log.sh  $2| tee ../log/get_node_log.log
    ;;
    delete_node)
        ./delete_unichain_node.sh  | tee ../log/delete_unichain_node.log
    ;;
    stop)
        ./clustercontrol.sh stop | tee ../log/clustercontrol_stop.log
        ./run_server_check.sh | tee ../log/run_server_check.log
    ;;
    restart)
        ./clustercontrol.sh stop | tee ../log/clustercontrol_stop.log
        ./clustercontrol.sh start | tee ../log/clustercontrol_start.log
        ./run_server_check.sh | tee ../log/run_server_check.log
    ;;
    start_node)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./startnode.sh $str_param | tee ../log/startnode.log
    ;;
    stop_node)
        str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./stopnode.sh $str_param | tee ../log/stopnode.log
    ;;
    start_rethinkdb)
        fab start_rethinkdb
    ;;
    stop_rethinkdb)
        fab stop_rethinkdb
    ;;
    restart_rethinkdb)
        fab stop_rethinkdb
        fab start_rethinkdb
    ;;
    start_unichain)
        fab start_unichain
    ;;
    stop_unichain)
        fab stop_unichain
    ;;
    restart_unichain)
        fab stop_unichain
        fab start_unichain
    ;;
    install_node)
        str_param=`echo $@|awk '{for(i=3;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./install_node.sh $str_param | tee ../log/install_node.log
    ;;
    uninstall)
        ./run_uninstall.sh | tee ../log/uninstall.log
    ;;
    unichain_init)
         str_param=`echo $@|awk '{for(i=2;i<=NF;i++){if(i!=NF)print $i" ";else print $i}}'`
        ./unichain_init.sh $str_param | tee ../log/unichain_init.log
    ;;
     drop)
       ./unichain_rethinkdb_drop.sh | tee ../log/unichain_rethinkdb_drop.log
    ;;
    *)
        usage
    ;;
esac

exit 0
