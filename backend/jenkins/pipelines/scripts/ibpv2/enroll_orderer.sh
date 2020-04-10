#!/bin/bash -xe

org_name=$1
work_dir=$2
binary_url=$3
ca_name=${org_name}'ca'

source $work_dir'/apis.ini' || true


TLS_CERT=$(jq -r .tls_cert $work_dir/crypto-config/${org_name}/${ca_name}.json)
ENROLL_ID=$(jq -r .enroll_id $work_dir/crypto-config/${org_name}/${ca_name}.json)
ENROLL_PASS=$(jq -r .enroll_secret $work_dir/crypto-config/${org_name}/${ca_name}.json)
CA_URL=$(jq -r .api_url $work_dir/crypto-config/${org_name}/${ca_name}.json)
CA_URL=${CA_URL:8}
CA_NAME=$(jq -r .ca_name $work_dir/crypto-config/${org_name}/${ca_name}.json)
TLS_CA_NAME=$(jq -r .tlsca_name $work_dir/crypto-config/${org_name}/${ca_name}.json)

if [ ! -d $work_dir'/bin/' ]; then
    wget https://github.com/hyperledger/fabric/releases/download/v1.4.6/hyperledger-fabric-linux-amd64-1.4.6.tar.gz
    tar -zxvf hyperledger-fabric-linux-amd64-1.4.6.tar.gz
    rm hyperledger-fabric-linux-amd64-1.4.6.tar.gz
fi

export PATH=$PATH:$work_dir/bin

BASE_FOLDER=$work_dir'/crypto-config'

PEER_ORG_NAME=${org_name}
export ${PEER_ORG_NAME}_FOLDER="${BASE_FOLDER}/${PEER_ORG_NAME}"
export ${PEER_ORG_NAME}_CA_TLS=${BASE_FOLDER}/${PEER_ORG_NAME}/catls/
export ${PEER_ORG_NAME}_CA_ADMIN=${BASE_FOLDER}/${PEER_ORG_NAME}/ca-admin
export ${PEER_ORG_NAME}_MSP=${BASE_FOLDER}/${PEER_ORG_NAME}/admin/msp/
export ${PEER_ORG_NAME}_TLSCA_ADMIN=${BASE_FOLDER}/${PEER_ORG_NAME}/tlsca-admin

var=${PEER_ORG_NAME}_FOLDER
mkdir -p ${!var}
var=${PEER_ORG_NAME}_CA_TLS
mkdir -p ${!var}
var=${PEER_ORG_NAME}_CA_ADMIN
mkdir -p ${!var}
var=${PEER_ORG_NAME}_MSP
mkdir -p ${!var}
var=${PEER_ORG_NAME}_TLSCA_ADMIN
mkdir -p ${!var}

IFS=':' read -ra ADDR <<< "$CA_URL"
export PROXY_IP=${ADDR[0]}
export ${PEER_ORG_NAME}_CA_HOST=${ADDR[0]}
export ${PEER_ORG_NAME}_CA_PORT=${ADDR[1]}

var0=${PEER_ORG_NAME}_CA_HOST
var1=${PEER_ORG_NAME}_CA_PORT
NAME=${PEER_ORG_NAME}ca CA_HOST=${!var0} CA_PORT=${!var1} ./wait_for_pod.sh

var0=${PEER_ORG_NAME}_CA_FOLDER
echo $TLS_CERT | base64 -d -w 0 > ${PEER_ORG_NAME}_CA_TLS/tls-ca-cert.pem

CSRHOSTS="${PROXY_IP},${PEER_ORG_NAME},127.0.0.1,localhost"

# Enroll ca admin
FABRIC_CA_CLIENT_HOME=${PEER_ORG_NAME}_CA_ADMIN fabric-ca-client enroll -u https://admin:pass4chain@${!var1}:${!var0} --caname ${CA_NAME} --tls.certfiles ${PEER_ORG_NAME}_CA_TLS/tls-ca-cert.pem --csr.hosts ${CSRHOSTS}
FABRIC_CLIENT_RC=$(($FABRIC_CLIENT_RC + $?))

# register org admin
FABRIC_CA_CLIENT_HOME=${PEER_ORG_NAME}_CA_ADMIN fabric-ca-client register -u https://admin:pass4chain@${!var1}:${!var0} --caname ${CA_NAME}  --id.name peeradmin --id.secret pass4chain --id.type admin --tls.certfiles ${PEER_ORG_NAME}_CA_TLS/tls-ca-cert.pem --csr.hosts ${CSRHOSTS}
FABRIC_CLIENT_RC=$(($FABRIC_CLIENT_RC + $?))


# Enroll MSP
FABRIC_CA_CLIENT_HOME=${PEER_ORG_NAME}_MSP fabric-ca-client enroll -u https://peeradmin:pass4chain@${!var1}:${!var0} --caname ${CA_NAME}  --tls.certfiles ${PEER_ORG_NAME}_CA_TLS/tls-ca-cert.pem --csr.hosts ${CSRHOSTS}
FABRIC_CLIENT_RC=$(($FABRIC_CLIENT_RC + $?))

# register Orderer
FABRIC_CA_CLIENT_HOME=${PEER_ORG_NAME}_MSP fabric-ca-client register -u https://admin:pass4chain@${!var1}:${!var0} --caname ${CA_NAME}  --id.name orderer --id.secret pass4chain --id.type orderer --tls.certfiles ${PEER_ORG_NAME}_CA_TLS/tls-ca-cert.pem --csr.hosts ${CSRHOSTS}
FABRIC_CLIENT_RC=$(($FABRIC_CLIENT_RC + $?))

#Enroll tlsca-admin with TLS CA

FABRIC_CA_CLIENT_HOME=${PEER_ORG_NAME}_TLSCA_ADMIN fabric-ca-client enroll -u https://admin:pass4chain@${!var1}:${!var0} --caname ${TLS_CA_NAME} --tls.certfiles ${PEER_ORG_NAME}_CA_TLS/tls-ca-cert.pem --csr.hosts ${CSRHOSTS}
FABRIC_CLIENT_RC=$(($FABRIC_CLIENT_RC + $?))

# register TLS CA
FABRIC_CA_CLIENT_HOME=${PEER_ORG_NAME}_TLSCA_ADMIN fabric-ca-client register -u https://admin:pass4chain@${!var1}:${!var0} --caname ${TLS_CA_NAME}  --id.name peertls --id.secret pass4chain --id.type peer --tls.certfiles ${PEER_ORG_NAME}_CA_TLS/tls-ca-cert.pem --csr.hosts ${CSRHOSTS}
FABRIC_CLIENT_RC=$(($FABRIC_CLIENT_RC + $?))

admin_cert=$(cat $work_dir/crypto-config/${org_name}/admin/msp/signcerts/cert.pem | base64 -w 0)
root_certs=$(cat $work_dir/crypto-config/${org_name}/ca-admin/msp/cacerts/*.pem | base64 -w 0)
tls_root_certs=$(cat $work_dir/crypto-config/${org_name}/tlsca-admin/msp/cacerts/*.pem | base64 -w 0)
private_key=$(cat $work_dir/crypto-config/${org_name}/admin/msp/keystore/* | base64 -w 0)

echo $admin_cert > $work_dir/crypto-config/${org_name}/admin_cert
echo $root_certs > $work_dir/crypto-config/${org_name}/root_certs
echo $tls_root_certs > $work_dir/crypto-config/${org_name}/tls_root_certs
echo $private_key > $work_dir/crypto-config/${org_name}/private_key
echo $TLS_CERT > $work_dir/crypto-config/${org_name}/ca_cert
cp  $work_dir/crypto-config/${org_name}/ca-admin/msp/cacerts/*.pem $work_dir/crypto-config/${org_name}/msptls.pem