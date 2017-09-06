#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
        echo "usage: ./configure_unichain.sh <number_of_files>"
            echo "No argument $1 supplied"
        }

        if [ -z "$1" ]; then
                printErr "<number_of_files>"
                    exit 1
                fi

                CONFDIR=../conf/unichain_confiles
                NUMFILES=$1


                UNICHAIN_TEMPLATE_FILE=../conf/template/unichain.conf.template

                if [ ! -f "$UNICHAIN_TEMPLATE_FILE" ]; then
                        echo "loss the config file $UNICHAIN_TEMPLATE_FILE "
                            exit 1
                        fi

                        if [ ! -d "$CONFDIR" ]; then
                                echo "loss the config dir $CONFDIR "
                                    exit 1
                                fi


                                num_pairs=$1
                                NUM_NODES=$1

                                # Send one of the config files to each instance
                                for (( HOST=0 ; HOST<$NUM_NODES ; HOST++ )); do
                                        CONFILE="bcdb_conf"$HOST
                                            echo "Sending "$CONFILE
                                                fab set_host:$HOST send_confile:$CONFILE
                                            done

                                            exit 0
