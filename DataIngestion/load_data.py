#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This file is automatically generated by AION for AION_110_1 usecase.
File generation time: 2022-05-03 06:08:12
'''
#Standard Library modules
import json
import platform

#Third Party modules
import pandas as pd 
from pathlib import Path

                    
def read_json(file_path):                    
    data = None                    
    with open(file_path,'r') as f:                    
        data = json.load(f)                    
    return data                    
                    
def write_json(data, file_path):                    
    with open(file_path,'w') as f:                    
        json.dump(data, f)                    
                    
def read_data(file_path, encoding='utf-8', sep=','):                    
    return pd.read_csv(file_path, encoding=encoding, sep=sep)                    
                    
def write_data(data, file_path, index=False):                    
    return data.to_csv(file_path, index=index)                    
                    
#Uncomment and change below code for google storage                    
#def write_data(data, file_path, index=False):                    
#    file_name= file_path.name                    
#    data.to_csv('output_data.csv')                    
#    storage_client = storage.Client()                    
#    bucket = storage_client.bucket('aion_data')                    
#    bucket.blob('prediction/'+file_name).upload_from_filename('output_data.csv', content_type='text/csv')                    
#    return data                    
                    
def is_file_name_url(file_name):                    
    supported_urls_starts_with = ('gs://')                    
    return file_name.startswith(supported_urls_starts_with)                    

        
#This function will read the data and save the data on persistent storage        
def load_data(base_config):        
    location = base_config['dataLocation']        
    if not Path(location).exists():        
        if not is_file_name_url(location):        
            raise ValueError(f'Data location does not exists: {location}')        
    usecase = base_config['modelName']+'_'+base_config['modelVersion']        
    home = Path.home()        
    if platform.system() == 'Windows':        
        from pathlib import WindowsPath        
        output_data_dir = WindowsPath(home)/'AppData'/'Local'/'HCLT'/'AION'/'Data'        
        output_model_dir = WindowsPath(home)/'AppData'/'Local'/'HCLT'/'AION'/'target'/usecase        
    else:        
        from pathlib import PosixPath        
        output_data_dir = PosixPath(home)/'HCLT'/'AION'/'Data'        
        output_model_dir = PosixPath(home)/'HCLT'/'AION'/'target'/usecase        
    output_data_dir.mkdir(parents=True, exist_ok=True)        
    output_model_dir.mkdir(parents=True, exist_ok=True)        
    config_file = Path(__file__).parent/'load_data.json'        
    if not Path(config_file).exists():        
        raise ValueError(f'Config file is missing: {config_file}')        
    config = read_json(config_file)        
    status = {}        
    csv_path = str(output_data_dir/(usecase+'_data'+'.csv'))        
    df = read_data(base_config['dataLocation'])        
    required_features = config['selected_features'] + [config['target_feature']]        
    missing_features = [x for x in required_features if x not in df.columns.tolist()]        
    if missing_features:        
        raise ValueError(f'Some feature/s is/are missing: {missing_features}')        
    df = df[required_features]        
    try:        
        write_data(df,csv_path,index=False)        
        status = {'Status':'Success','DataFilePath':csv_path}        
    except:        
        raise ValueError('Unable to create data file')        
    deploy_file = output_model_dir/'deploy.json'        
    deployment_dict = dict()        
    deployment_dict['load_data'] = {}        
    deployment_dict['load_data']['selected_features'] = [x for x in config['selected_features'] if x != config['target_feature']]        
    deployment_dict['load_data']['status'] = status        
    write_json(deployment_dict, deploy_file)        
    return json.dumps(status)        
        
if __name__ == '__main__':        
    import sys        
    if len(sys.argv) != 2:        
        print({'Status':'Falure','Message':'config file not present'})        
        exit()        
    config = sys.argv[1]        
    if Path(config).is_file() and Path(config).suffix == '.json':        
        config = read_json(config)        
    else:        
        config = json.loads(config)        
    try:        
        print(load_data( config))        
    except Exception as e:        
        status = {'Status':'Failure','Message':str(e)}        
        print(json.dumps(status))