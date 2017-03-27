#检查nginx进程是否存在
count=$(ps -C nginx --no-heading|wc -l)

#进程数等于0的时候
if [ "${count}" = "0" ]; then
	#尝试启动一次nginx，停止2秒后再次检测
    /etc/init.d/nginx start
    sleep 2
   	count=$(ps -C nginx --no-heading|wc -l)
    if [ "${count}" = "0" ]; then
		#如果启动没成功，就杀掉keepalive触发主备切换
        /etc/init.d/keepalived stop
        exit 1
	else
    	exit 0
    fi
fi