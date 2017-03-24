
#! /bin/sh
# This script run at 00:00 every day

# The nginx logs root path
logs_path="/nginx/log/"

# compress the backup log with *.gz
compress="true"

# nginx pid file 
pid_path="/nginx/run/nginx.pid"

cur_log_access_name="access.log"
cur_log_error_name="error.log"

# gzip log 5 days after!
gzip_after_days=4
# remove log 60 days ago!
keep_days=60

# access and error log real path
cur_logfile_access_path=${logs_path}${cur_log_access_name}
cur_logfile_error_path=${logs_path}${cur_log_error_name}

# yesterday date string
yesterday_ymd=$(date -d "yesterday" +"%Y%m%d")

# backup log file root path
backup_logs_path="${logs_path}"
# backup log file cut directory
backup_logfile_path="${backup_logs_path}backup/"

# backup log file name with date suffix
backup_logfile_access_name="access_${yesterday_ymd}.log"
backup_logfile_error_name="error_${yesterday_ymd}.log"

backup_logfile_access_path="${backup_logfile_path}${backup_logfile_access_name}"
backup_logfile_error_path="${backup_logfile_path}${backup_logfile_error_name}"

mkdir -p ${backup_logfile_path}

# move old log file to backup dir
if [ -s ${cur_logfile_access_path} ]; then
	mv ${cur_logfile_access_path} ${backup_logfile_access_path}
fi

if [ -s ${cur_logfile_error_path} ]; then
	mv ${cur_logfile_error_path} ${backup_logfile_error_path}
fi

# gzip the logs in backup dir

if [ "${compress}" == "true" ]; then
        gzip -q `find ${backup_logfile_path} -name "access_*.log" -type f -mtime +${gzip_after_days}`
fi

if [ "${compress}" == "true" ]; then 
        gzip -q `find ${backup_logfile_path} -name "error_*.log" -type f -mtime +${gzip_after_days}`
fi

# remove the old backup logs after keep_days
find ${backup_logfile_path} -name "access_*" -type f -mtime +${keep_days} |xargs rm -f
find ${backup_logfile_path} -name "error_*" -type f -mtime +${keep_days} |xargs rm -f

# send signal to nginx, reopen the log and write continue
kill -USR1 `cat ${pid_path}`

