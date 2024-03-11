import pandas as pd 
import os
import numpy as np
import json 


provider_cols=["Age_Range", "Gender_Identity", "Race",  "Ethnicity", "Training", "Specialty",
          "Scope", "Religion", "Comfort with Counseling Re: Permanent Contraception"]

def load_provider_self_demographics(data_dir, provider_clean_up_dict):
    
    provider_UAB = pd.read_excel(os.path.join(data_dir, "providers_final.xlsx"), sheet_name='UAB')
    provider_UAB['site'] = 'UAB'
    # provider_UAB = provider_UAB[provider_UAB['Race'].notna()] # filter out missing age range

    provider_Metro = pd.read_excel(os.path.join(data_dir, "providers_final.xlsx"), sheet_name='Metro')
    provider_Metro['site'] = 'MetroHealth'
    provider_Metro = provider_Metro[provider_Metro['Age Range'].notna()] # filter out missing age range
    # provider_Metro['Age Range'] = [str(val) for val in provider_Metro['Age Range'].values]
    
    provider_UCSF = pd.read_excel(os.path.join(data_dir, "UCSFproviders_final.xlsx"), sheet_name='UCSF- self reported')
    provider_UCSF['site'] = 'UCSF'
    provider_UCSF['Unnamed: 0'] = (
        provider_UCSF['Unnamed: 0']
        .str.split(expand=True)[0]
        .str.rstrip(',')
        .str.lower())
    # provider_UCSF = provider_UCSF[provider_UCSF['Age Range'].notna()]  # filter out missing age range

    provider_demo_df = pd.concat([provider_UAB, provider_Metro, provider_UCSF], ignore_index=True)
    provider_demo_df = provider_demo_df.rename(
        columns={'Unnamed: 0':"prenatal_provider",
                    'Age Range':'Age_Range',
                    'Gender Identity':'Gender_Identity'})
    
    for col_name, value_map in provider_clean_up_dict.items():
        if col_name == 'Religion':
            provider_demo_df[col_name] = provider_demo_df[col_name].str.lower().map(value_map)
        else:
            provider_demo_df[col_name] = provider_demo_df[col_name].map(value_map)

    print(len(provider_demo_df))
    # provider_demo_df = provider_demo_df.dropna(subset=['Age_Range', 'Race', 'Gender_Identity'])
    provider_demo_df = provider_demo_df[provider_demo_df['Age_Range'].notna() |
                                        provider_demo_df['Race'].notna() |
                                        provider_demo_df['Gender_Identity'].notna() ]
    print(len(provider_demo_df))

    return provider_demo_df
    

def load_provider_peer_demographics(data_dir, provider_clean_up_dict):

    provider_UAB = pd.read_excel(os.path.join(data_dir, "providers peer reported.xlsx"), sheet_name='UAB')
    provider_UAB['site'] = 'UAB'
    # provider_UAB = provider_UAB[provider_UAB['Training'].notna()]
    
    provider_Metro = pd.read_excel(os.path.join(data_dir, "providers peer reported.xlsx"), sheet_name='Metro')
    provider_Metro['site'] = 'MetroHealth'
    # provider_Metro = provider_Metro[provider_Metro['Age Range'].notna()] # filter out missing age range

    provider_UCSF = pd.read_excel(os.path.join(data_dir, "UCSFproviders_final.xlsx"), sheet_name='tania- peer reported')
    provider_UCSF['site'] = 'UCSF'
    provider_UCSF['Unnamed: 0'] = (
        provider_UCSF['Unnamed: 0']
        .str.split(expand=True)[0]
        .str.rstrip(',')
        .str.lower())
    # provider_UCSF = provider_UCSF[provider_UCSF['Age Range'].notna()] # filter out missing age range
    
    provider_demo_df = pd.concat([provider_UAB, provider_Metro, provider_UCSF], ignore_index=True)
    provider_demo_df = provider_demo_df.rename(
        columns={'Unnamed: 0':"prenatal_provider",
                    'Age Range':'Age_Range',
                    'Gender Identity':'Gender_Identity'})
    
    for col_name, value_map in provider_clean_up_dict.items():
        if col_name == 'Religion':
            provider_demo_df[col_name] = provider_demo_df[col_name].str.lower().map(value_map)
        else:
            provider_demo_df[col_name] = provider_demo_df[col_name].map(value_map)

    print(len(provider_demo_df))
    # provider_demo_df = provider_demo_df.dropna(subset=['Age_Range', 'Race', 'Gender_Identity'])
    provider_demo_df = provider_demo_df[provider_demo_df['Age_Range'].notna() |
                                        provider_demo_df['Race'].notna() |
                                        provider_demo_df['Gender_Identity'].notna() ]
    print(len(provider_demo_df))

    return provider_demo_df


if __name__ == '__main__':

    data_dir = os.environ['DATA_DIR']
    # reporter = 'self'

    with open('cleanup/provider_clean_up_list.json', 'r') as fp:
        provider_clean_up_dict = json.load(fp=fp)

    # provider_demo_peer_df = load_provider_peer_demographics(data_dir, provider_clean_up_dict)
    # print(provider_demo_peer_df.head())
    # print(provider_demo_peer_df.set_index('site').notna().groupby(level=0).mean())
    # print(provider_demo_peer_df.notna().mean())
    
    provider_demo_self_df = load_provider_self_demographics(data_dir, provider_clean_up_dict)
    print(provider_demo_self_df.head())
    print(provider_demo_self_df.set_index('site').notna().groupby(level=0).mean())
    print(provider_demo_self_df.notna().mean())
    print(provider_demo_self_df['Training'].value_counts().keys())
    exit()
    # Accuracy check
    accuracy_cols = ['Age_Range', 'Race', 'Gender_Identity', 'Ethnicity', 'Training', 'Specialty', 'Scope', 'Religion', 'Comfort with Counseling Re: Permanent Contraception']
    suffixes=['_self', '_peer']
    for col in accuracy_cols:
        print(col)
        comp_df = (
            provider_demo_self_df[['prenatal_provider', col]]
            .merge(provider_demo_peer_df[['prenatal_provider', col]],
                on='prenatal_provider',
                how='inner',
                suffixes=suffixes)
        )
        print(np.mean(comp_df[col + suffixes[0]] == comp_df[col + suffixes[1]]))

    # provider_demo_df[['site', 'prenatal_provider']].sort_values(['site', 'prenatal_provider']).to_csv('output/provider_demo_list.csv', index=False)
    # print(provider_demo_df['Religion'].value_counts())

    # remove
    # "uab","combined",NA,TRUE
    # Owen, John MD = Owen, John S MD
    # Jenkins, Todd R. MD = Jenkins, Todd R MD
    # Gleason, Brian P. MD = Gleason, Brian P MD
    