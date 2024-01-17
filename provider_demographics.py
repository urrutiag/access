import pandas as pd 
import os
import numpy as np
import json 


def load_provider_self_demographics(data_dir, provider_clean_up_dict):
    
    provider_UAB = pd.read_excel(os.path.join(data_dir, "providers_final.xlsx"), sheet_name='UAB')
    provider_UAB['site'] = 'UAB'
    
    provider_Metro = pd.read_excel(os.path.join(data_dir, "providers_final.xlsx"), sheet_name='Metro')
    provider_Metro['site'] = 'Metro'

    provider_UCSF = pd.read_excel(os.path.join(data_dir, "UCSFproviders_final.xlsx"), sheet_name='UCSF- self reported')
    provider_UCSF['site'] = 'UCSF'
    
    provider_demo_df = pd.concat([provider_UAB, provider_Metro, provider_UCSF], ignore_index=True)
    provider_demo_df = provider_demo_df.rename(
        columns={'Unnamed: 0':"prenatal_provider",
                    'Age Range':'Age_Range',
                    'Gender Identity':'Gender_Identity'})
    
    for col_name, value_map in provider_clean_up_dict.items():
        provider_demo_df[col_name] = provider_demo_df[col_name].map(value_map)

    return provider_demo_df
    

def load_provider_peer_demographics(data_dir, provider_clean_up_dict):

    provider_UAB = pd.read_excel(os.path.join(data_dir, "providers peer reported.xlsx"), sheet_name='UAB')
    provider_UAB['site'] = 'UAB'
    
    provider_Metro = pd.read_excel(os.path.join(data_dir, "providers peer reported.xlsx"), sheet_name='Metro')
    provider_Metro['site'] = 'Metro'

    provider_UCSF = pd.read_excel(os.path.join(data_dir, "UCSFproviders_final.xlsx"), sheet_name='tania- peer reported')
    provider_UCSF['site'] = 'UCSF'
    
    provider_demo_df = pd.concat([provider_UAB, provider_Metro, provider_UCSF], ignore_index=True)
    provider_demo_df = provider_demo_df.rename(
        columns={'Unnamed: 0':"prenatal_provider",
                    'Age Range':'Age_Range',
                    'Gender Identity':'Gender_Identity'})
    
    for col_name, value_map in provider_clean_up_dict.items():
        provider_demo_df[col_name] = provider_demo_df[col_name].map(value_map)

    return provider_demo_df


if __name__ == '__main__':

    data_dir = '/mnt/c/Users/Urrutia/Dropbox/Documents/UNC_OBGYN/kavita_access/data/'
    reporter = 'peer'

    with open('cleanup/provider_clean_up_list.json', 'r') as fp:
        provider_clean_up_dict = json.load(fp=fp)

    # load and combine
    if reporter == 'self':
        provider_demo_df = load_provider_self_demographics(data_dir, provider_clean_up_dict)
    
    elif reporter == 'peer':
        provider_demo_df = load_provider_peer_demographics(data_dir, provider_clean_up_dict)

    print(provider_demo_df.head())