#!/usr/bin/env python
# coding=utf-8
import os
import sys
import json
import yaml
import subprocess

def loadConfigContent(configFile):
    config_content = open(configFile)
    config_dict = {}
    for lines in config_content:
        items = lines.split('=', 1)
        config_dict[items[0]] = items[1]
    return config_dict

def loadJsonContent(jsonFile):
    with open(jsonFile, 'r') as f:
        temtplateDict = json.load(f)
    f.close()
    return temtplateDict

def searchfromcomponets(componets,name,item):
    result =''
    for componet in componets:
        if componet['id'].replace("-","").replace("_","") == name:
            result = componet[item]
    return  result


def generatePeerSection(templateContent, peerName,componets):
    templateContent['url'] = searchfromcomponets(componets,peerName,'api_url')
    #templateContent['grpcOptions']['ssl-target-name-override'] = proxyIp
    templateContent['tlsCACerts']['pem'] = searchfromcomponets(componets,peerName,'tls_cert')
    return templateContent


def generateOrdererSection(templateContent, ordererName,componets):
    templateContent['url'] = searchfromcomponets(componets,ordererName,'api_url')
    #templateContent['grpcOptions']['ssl-target-name-override'] = proxyIp

    templateContent['tlsCACerts']['pem'] = searchfromcomponets(componets,ordererName,'tls_cert')
    return templateContent

def generateOrgSection(templateContent,orgName,peers,orgType):
    templateContent['mspid'] = orgName
    templateContent['cryptoPath'] = templateContent['cryptoPath'].replace('orgname', orgName)
    if orgType == 'peerorg':
        templateContent['certificateAuthorities'] = orgName + 'ca'
        for peer in peers:
            if peer.split('.')[1] == orgName:
                templateContent['peers'].append(orgName + peer.split('.')[0])
    return templateContent

def generateConnectionProfiles(networkspec,componets):
    peerorg_names = []
    ordererorg_names = []
    peers = networkspec['network']['peers']
    for orderer_object in networkspec['network']['orderers']:
        ordererorg_names.append(orderer_object.split('.')[1])
    ordererorg_names = list(set(ordererorg_names))
    for peer_object in peers:
        peerorg_names.append(peer_object.split('.')[1])
    peerorg_names = list(set(peerorg_names))

    # generate collection profile for each peer organization
    for org in peerorg_names:
        connection_template = loadJsonContent('./templates/connection_template.json')
        # Load client
        connection_template['client']['organization'] = org
        # Load organizations including peer orgs and orderer org
        for org_name in peerorg_names:
            org_template = loadJsonContent('./templates/org_template.json')
            connection_template['organizations'][org_name] = generateOrgSection(org_template, org_name, peers, 'peerorg')
        org_template = loadJsonContent('./templates/org_template.json')
        for ordererorg_name in ordererorg_names:
            connection_template['organizations'][ordererorg_name] = generateOrgSection(org_template, ordererorg_name,'','ordererorg')

        # Load peers
        print peers
        for peer in peers:
            org_name = peer.split('.')[1]
            peer_name = peer.split('.')[0]
            peer_template = loadJsonContent('./templates/peer_template.json')
            peer_name = org_name + peer_name
            connection_template['peers'][peer_name] = generatePeerSection(peer_template, peer_name, componets)
        # Load orderers
        orderer_template = loadJsonContent('./templates/orderer_template.json')
        for ordererorg in networkspec['network']['orderers']:
            orderer_num = ordererorg.split('.')[0]
            ordererorg_name = ordererorg.split('.')[1]
            for orderer_index in range(int(orderer_num)):
                orderer_index += 1
                orderer_name = ordererorg_name + 'orderer' + str(orderer_index)
                connection_template['orderers'][orderer_name] = generateOrdererSection(orderer_template, orderer_name, componets)

        ca_template = loadJsonContent('./templates/ca_template.json')
        ca_template['caName'] = org + 'ca'
        ca_template['url'] = searchfromcomponets(componets, org + 'ca', 'api_url')
        ca_template['tlsCACerts']['pem'] = searchfromcomponets(componets, org + 'ca', 'tls_cert')
        connection_template['certificateAuthorities'] = ca_template
        # write out connection file
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/connection.json', 'w') as f:
            print('\nWriting connection file for ' + str(org) + ' - ' + f.name)
            json.dump(connection_template, f, indent=4)
        f.close()
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/connection.yml', 'w') as f:
            print('\nWriting connection file for ' + str(org) + ' - ' + f.name)
            yaml.safe_dump(connection_template, f, allow_unicode=True)
        f.close()

def generateIdentityProfiles(networkspec,componets):
    peerorg_names = []
    ordererorg_names = []
    peers = networkspec['network']['peers']
    for peer_object in peers:
        peerorg_names.append(peer_object.split('.')[1])
    peerorg_names = list(set(peerorg_names))

    # generate collection profile for each peer organization
    for org in peerorg_names:
        identity_template = loadJsonContent('./templates/identity_template.json')
        # Load client
        identity_template['name'] = org
        identity_template['private_key']= searchfromcomponets(componets,org,'admins')
        identity_template['cert'] = searchfromcomponets(componets,org,'root_certs')
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/identity.json', 'w') as f:
            print('\nWriting identity file for ' + str(org) + ' - ' + f.name)
            json.dump(identity_template, f, indent=4)
        f.close()

# certsPath = /opt/src/scripts/ibpv2/keyfiles
def generateCertificatesPackage(networkspec):
    certsPath = networkspec['work_dir'] + '/crypto-config/'
    # restructure msp dir
    mspCommand = 'cd '+ certsPath + ' && mkdir -p orgname/users/Admin@orgname/msp && cp -rf orgname/admin/* orgname/users/Admin@orgname/msp/'
    tlsCommand = 'cd ' + certsPath + ' && mkdir -p orgname/tlsca && cp -rf orgname/msp/tlscacerts/*.pem orgname/tlsca/ca.pem'
    peerorg_names = []
    ordererorg_names = []

    for orderer_object in networkspec['network']['orderers']:
        ordererorg_names.append(orderer_object.split('.')[1])
    ordererorg_names = list(set(ordererorg_names))
    for peer_object in networkspec['network']['peers']:
        peerorg_names.append(peer_object.split('.')[1])
    peerorg_names = list(set(peerorg_names))
    for org in peerorg_names:
        os.system(mspCommand.replace('orgname', org))
        os.system(tlsCommand.replace('orgname', org))
        os.rename(certsPath + "/" + org + "/users/Admin@" + org + "/msp/signcerts/cert.pem", certsPath + "/" + org + "/users/Admin@" + org + "/msp/signcerts/Admin@" + org + "-cert.pem")
    # ordererorg
    for ordererorg_name in ordererorg_names:
        os.system(mspCommand.replace('orgname', ordererorg_name))
        os.system(tlsCommand.replace('orgname', ordererorg_name))
        os.rename(certsPath + "/" + ordererorg_name + "/users/Admin@" + ordererorg_name + "/msp/signcerts/cert.pem", certsPath + "/" + ordererorg_name + "/users/Admin@" + ordererorg_name + "/msp/signcerts/Admin@" + ordererorg_name + "-cert.pem")
