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


def generatePeerSection(templateContent, peerName,orgName, componets,networkspec):
    templateContent['url'] = searchfromcomponets(componets,peerName,'api_url')
    templateContent['grpcOptions']['ssl-target-name-override'] = searchfromcomponets(componets,peerName,'api_url').replace("//","").split(':')[1]

    #templateContent['tlsCACerts']['pem'] =
    with open(networkspec['work_dir'] + '/crypto-config/' + orgName + '/msptls.pem', 'r') as f1:
        templateContent['tlsCACerts']['pem'] = f1.read()
    f1.close()
    return templateContent


def generateOrdererSection(templateContent, ordererorg_name, orderer_name,componets,networkspec):
    templateContent['url'] = searchfromcomponets(componets,orderer_name,'api_url')
    with open(networkspec['work_dir'] + '/crypto-config/' + ordererorg_name + '/msptls.pem', 'r') as f1:
        templateContent['tlsCACerts']['pem'] = f1.read()
    f1.close()
    return templateContent

def generateOrgSection(templateContent,orgName,peers,type):
    templateContent['mspid'] = orgName
    templateContent['cryptoPath'] = templateContent['cryptoPath'].replace('orgname', orgName)
    templateContent['certificateAuthorities'].append(orgName + 'ca')
    if type == 'peer':
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
    # create a empty connection.json for oder reorg
    for ordererorg_name in ordererorg_names:
       connection_template = loadJsonContent('./templates/connection_template.json')
       with open(networkspec['work_dir'] + '/crypto-config/' + ordererorg_name + '/connection.json', 'w') as f:
          print('\nWriting connection file for ' + str(ordererorg_name) + ' - ' + f.name)
          json.dump(connection_template, f, indent=4)
       f.close()

    # generate collection profile for each peer organization
    for orgname in peerorg_names:
        connection_template = loadJsonContent('./templates/connection_template.json')
        # Load client
        connection_template['client']['organization'] = orgname
        # Load organizations including peer orgs and orderer org
        for org in peerorg_names:
            org_template = loadJsonContent('./templates/org_template.json')
            connection_template['organizations'][org] = generateOrgSection(org_template, org, peers,'peer')
        # organizations for orderer
        for ordererorg_name in ordererorg_names:
            org_template = loadJsonContent('./templates/org_template.json')
            connection_template['organizations'][ordererorg_name] = generateOrgSection(org_template, ordererorg_name,'','order')
        # Load peers
        print peers
        for peer in peers:
            org_name = peer.split('.')[1]
            peer_name = peer.split('.')[0]
            peer_template = loadJsonContent('./templates/peer_template.json')
            peer_name = org_name + peer_name
            connection_template['peers'][peer_name] = generatePeerSection(peer_template, peer_name,org_name, componets,networkspec)

    # Load orderers
        for ordererorg in networkspec['network']['orderers']:
            orderer_num = ordererorg.split('.')[0]
            ordererorg_name = ordererorg.split('.')[1]
            for orderer_index in range(int(orderer_num)):
                orderer_index += 1
                orderer_name = ordererorg_name + 'orderer' + str(orderer_index)
                orderer_template = loadJsonContent('./templates/orderer_template.json')
                connection_template['orderers'][orderer_name] = generateOrdererSection(orderer_template, ordererorg_name, orderer_name,componets,networkspec)
        for org in peerorg_names:
            ca_template = loadJsonContent('./templates/ca_template.json')
            ca_template['caName'] = org + 'ca'
            ca_template['url'] = searchfromcomponets(componets, org + 'ca', 'api_url')
            with open(networkspec['work_dir'] + '/crypto-config/' + org + '/catls/tls-ca-cert.pem', 'r') as f1:
                ca_template['tlsCACerts']['pem'] = f1.read()
            f1.close()
            connection_template['certificateAuthorities'][org + 'ca'] = ca_template
    # write out connection file
        with open(networkspec['work_dir'] + '/crypto-config/' + orgname + '/connection.json', 'w') as f:
            print('\nWriting connection file for ' + str(orgname) + ' - ' + f.name)
            json.dump(connection_template, f, indent=4)
        f.close()
    #with open(networkspec['work_dir'] + '/crypto-config/' + org + '/connection.yml', 'w') as f:
    #   print('\nWriting connection file for ' + str(org) + ' - ' + f.name)
    #   yaml.safe_dump(connection_template, f, allow_unicode=True)
    #f.close()

def generateIdentityProfiles(networkspec,componets):
    peerorg_names = []
    ordererorg_names = []
    for orderer_object in networkspec['network']['orderers']:
        ordererorg_names.append(orderer_object.split('.')[1])
    ordererorg_names = list(set(ordererorg_names))
    peers = networkspec['network']['peers']
    for peer_object in peers:
        peerorg_names.append(peer_object.split('.')[1])
    peerorg_names = list(set(peerorg_names))

    # generate collection profile for each peer organization
    for org in peerorg_names:
        identity_template = loadJsonContent('./templates/identity_template.json')
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/admin_cert', 'r') as f1:
            cert = f1.read()
        f1.close()
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/private_key', 'r') as f2:
            private_key = f2.read()
        f2.close()
        # Load client
        identity_template['name'] = org + 'Admin'
        identity_template['private_key']= private_key
        identity_template['cert'] = cert
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/identity.json', 'w') as f:
            print('\nWriting identity file for ' + str(org) + ' - ' + f.name)
            json.dump(identity_template, f, indent=4)
        f.close()
    for org in ordererorg_names:
        identity_template = loadJsonContent('./templates/identity_template.json')
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/admin_cert', 'r') as f1:
            cert = f1.read()
        f1.close()
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/private_key', 'r') as f2:
            private_key = f2.read()
        f2.close()
        # Load client
        identity_template['name'] = org + 'Admin'
        identity_template['private_key']= private_key
        identity_template['cert'] = cert
        with open(networkspec['work_dir'] + '/crypto-config/' + org + '/identity.json', 'w') as f:
            print('\nWriting identity file for ' + str(org) + ' - ' + f.name)
            json.dump(identity_template, f, indent=4)
        f.close()
# certsPath = /opt/src/scripts/ibpv2/keyfiles
def generateCertificatesPackage(networkspec):
    certsPath = networkspec['work_dir'] + '/crypto-config/'
    # restructure msp dir
    #peerCommand = 'cd '+ certsPath + '&& cd orgname && rm -r * !(connection.json | identity.json )'
    orderCommand = 'cd ' + certsPath + ' && rm -r orgname'
    #peerorg_names = []
    ordererorg_names = []

    for orderer_object in networkspec['network']['orderers']:
        ordererorg_names.append(orderer_object.split('.')[1])
    ordererorg_names = list(set(ordererorg_names))
    #for peer_object in networkspec['network']['peers']:
    #    peerorg_names.append(peer_object.split('.')[1])
    #peerorg_names = list(set(peerorg_names))
    #for org in peerorg_names:
    #    os.system(peerCommand.replace('orgname', org))
    # ordererorg
    for ordererorg_name in ordererorg_names:
        os.system(orderCommand.replace('orgname', ordererorg_name))