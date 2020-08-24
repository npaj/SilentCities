import json
import re
import requests
import wget
import os
import shutil
import zipfile
import pandas as pd
import numpy as np

def Down(query, first=False, HDD=0):

    if first:
        url = query
    else:
        url = 'https://api.osf.io/v2/nodes/{0}/files/{2}{1}'.format(
            REPO, query, DISK)
    STOP = False
    while STOP == False:
        if site == '':
            # Downloading all site
            resp = requests.get(url)
            resp.raise_for_status()
            data = json.loads(resp.content)
            for i in data['data']:
                current_path = os.path.join(SAVEPATH[HDD], str(
                    i['attributes']['materialized_path'])[1:])
                if i['attributes']['kind'] == 'folder':
                    if not os.path.exists(current_path):
                        os.makedirs(current_path)
                    Down(i['attributes']['path'], HDD=HDD)

                if i['attributes']['kind'] == 'file':
                    sub = re.search(r'sub-(\S+)_task', i['attributes']['name'])
                    guids.append((sub, i['id']))
                    # print(i['attributes']['materialized_path'],i['attributes']['path'], i['attributes']['size'])

                    _, _, free = shutil.disk_usage(SAVEPATH[HDD])
                    try:
                        size = int(i['attributes']['size'])*3
                    except:
                        size = 4550779562 * 3
                    if int(free) > size:
                        current_file_path = os.path.join(SAVEPATH[HDD], str(
                            i['attributes']['materialized_path'])[1:])

                        if True in [os.path.exists(os.path.join(k, str(
                                    i['attributes']['materialized_path'])[1:-4])) for k in SAVEPATH] or True in [os.path.exists(os.path.join(k, str(
                                        i['attributes']['materialized_path'])[1:])) for k in SAVEPATH]:
                            print(
                                current_file_path[:-4] + '     already exist')
                            if os.path.exists(current_file_path[:-4]+'.zip'):
                                try:
                                    print('unzip')
                                    with zipfile.ZipFile(current_file_path, 'r', allowZip64=True) as zip_ref:
                                        zip_ref.extractall(
                                            current_file_path[:-4])
                                    os.remove(current_file_path)
                                except:
                                    print('error : ' + current_file_path)
                                    ERROR['file'].append(current_file_path)
                                    ERROR['pb'].append('zip')

                            if i['attributes']['name'][-4:] == '.rar':
                                print('error : rarfile')
                                
                                ERROR['file'].append(current_file_path)
                                ERROR['pb'].append('.rar')
                        else:
                            try:
                                print('downloading : ' + current_file_path)
                                filename = wget.download(
                                    i['links']['download'], out=current_file_path)
                                print(filename + '        has been downloaded')
                            except:
                                print(current_file_path + '    error')
                                
                                ERROR['file'].append(current_file_path)
                                ERROR['pb'].append('download')
                            try:
                                if current_file_path[-4:] == '.zip' and os.path.exists(current_file_path):
                                    with zipfile.ZipFile(current_file_path, 'r', allowZip64=True) as zip_ref:
                                        zip_ref.extractall(
                                            current_file_path[:-4])

                                    os.remove(current_file_path)
                                if current_file_path[-4:] == '.rar':
                                    print('error : rarfile')
                                    
                                    ERROR['file'].append(current_file_path)
                                    ERROR['pb'].append('.rar')

                            except:
                                print(current_file_path + '    error unzip')
                                
                                ERROR['file'] .append(current_file_path)
                                ERROR['pb'].append('zip')

                    else:
                        print('HDD {} is full'.format(HDD))
                        if HDD <= len(SAVEPATH):
                            HDD += 1
                        else:
                            STOP = True
                            break
                df = pd.DataFrame.from_dict(ERROR)
                df.to_csv('ERROR2.csv')

            url = data['links']['next']
            if url is None:
                STOP = False
                break

        else:
            # Downloading one site
            current_path = os.path.join(SAVEPATH[HDD], site)
            if not os.path.exists(current_path):
                os.makedirs(current_path)
            resp = requests.get(url)
            resp.raise_for_status()
            data = json.loads(resp.content)

            for i in data['data']:
                if i['attributes']['kind'] == 'folder':
                    Down(i['attributes']['path'], HDD=0)

                if i['attributes']['kind'] == 'file':
                    if site+'_' in i['attributes']['name']:
                        sub = re.search(r'sub-(\S+)_task',
                                        i['attributes']['name'])
                        guids.append((sub, i['id']))
                        _, _, free = shutil.disk_usage(SAVEPATH[HDD])
                        try:
                            size = int(i['attributes']['size'])*3
                        except:
                            size = 4550779562 * 3
                        if int(free) > size:
                            current_file_path = os.path.join(SAVEPATH[HDD], str(
                                i['attributes']['materialized_path'])[1:])

                            if True in [os.path.exists(os.path.join(k, str(
                                    i['attributes']['materialized_path'])[1:-4])) for k in SAVEPATH] or True in [os.path.exists(os.path.join(k, str(
                                    i['attributes']['materialized_path'])[1:])) for k in SAVEPATH]:
                                print(
                                    current_file_path[:-4] + '  already exist')
                                if os.path.exists(current_file_path[:-4]+'.zip'):
                                    print('unzip')
                                    with zipfile.ZipFile(current_file_path, 'r') as zip_ref:
                                        zip_ref.extractall(
                                            current_file_path[:-4])
                                    print('del')
                                    os.remove(current_file_path)
                            else:
                                try:
                                    print('downloading : '+current_file_path)
                                    filename = wget.download(
                                        i['links']['download'], out=current_file_path)
                                    print(
                                        filename + '        has been downloaded')
                                except:
                                    print(current_file_path + '    error')
                                    ERROR['file'].append(current_file_path)
                                    ERROR['pb'].append('download')

                                    
                                try:
                                    if current_file_path[-4:] == '.zip':
                                        with zipfile.ZipFile(current_file_path, 'r') as zip_ref:
                                            zip_ref.extractall(
                                                current_file_path[:-4])
                                        os.remove(current_file_path)
                                    if current_file_path[-4:] == '.rar':
                                        print('error : rarfile')
                                        ERROR['file'].append(current_file_path)
                                        ERROR['pb'].append('.rar')
                                        

                                except:
                                    print(current_file_path +
                                          '    error unzip')
                                    ERROR['file'].append(current_file_path)
                                    ERROR['pb'].append('unzip')
                                    

                        else:
                            print('HDD {} is full'.format(HDD))
                            if HDD <= len(SAVEPATH):
                                HDD += 1
                            else:
                                STOP = True
                                break
                    else:
                        pass
            df = pd.DataFrame.from_dict(ERROR)
            df.to_csv('ERROR2.csv')

            url = data['links']['next']
            if url is None:
                STOP = False
                break

DISK =  'osfstorage' #'dropbox'
REPO = 'h285u'
SAVEPATH = ['/media/nicolas/Silent', '/media/nicolas/LaCie']
query = ''
url = 'https://api.osf.io/v2/nodes/{0}/files/{2}/{1}'.format(REPO, query, DISK)
guids = []
site = ''
ERROR = {'file': [], 'pb': []}

Down(url, True)

DISK =  'dropbox'
url = 'https://api.osf.io/v2/nodes/{0}/files/{2}/{1}'.format(REPO, query, DISK)
Down(url, True)

print('done')
