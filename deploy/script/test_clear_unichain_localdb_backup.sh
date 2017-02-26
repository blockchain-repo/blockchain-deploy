#!/bin/bash
# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

echo -e "[INFO]==========stop unichain=========="
fab stop_unichain

echo -e "[INFO]==========stop unichain_restore=========="
fab stop_unichain_restore

echo -e "[INFO]==========clear localdb backup files=========="
fab test_localdb_model_delete

echo -e "[INFO]==========clear and init unichain=========="
fab init_unichain:shards=True,replicas=True