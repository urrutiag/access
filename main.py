import pandas as pd 
import os
import numpy as np
import json 
import provider_demographics
import delivery
import provider_linkage


def create_demographic_summary(delivery_df, col):

    delivery_summary = delivery_df.groupby(col).agg(
        providers=pd.NamedAgg(column='prenatal_provider', aggfunc='nunique'),
        deliveries=pd.NamedAgg(column='prenatal_provider', aggfunc='count'),
        form_valid=pd.NamedAgg(column='form_valid_int', aggfunc='sum'),
        form_valid_proportion=pd.NamedAgg(column='form_valid_int', aggfunc='mean'),
        ).reset_index()
    delivery_summary = delivery_summary.rename(columns={col:'group'})
    delivery_summary['form_not_valid'] = delivery_summary['deliveries'] - delivery_summary['form_valid']
    delivery_summary['form_not_valid_proportion'] = 1 - delivery_summary['form_valid_proportion']
    delivery_summary['form_valid_proportion_fmt'] = delivery_summary['form_valid_proportion'].map('{:,.1%}'.format)
    delivery_summary['form_not_valid_proportion_fmt'] = delivery_summary['form_not_valid_proportion'].map('{:,.1%}'.format)
    delivery_summary['demographic'] = col

    return delivery_summary


if __name__ == '__main__':

    data_dir = os.environ['DATA_DIR']
    reporter = 'peer'

    with open('cleanup/delivery_clean_up_list.json', 'r') as fp:
        delivery_clean_up_dict = json.load(fp=fp)
    with open('cleanup/provider_clean_up_list.json', 'r') as fp:
        provider_clean_up_dict = json.load(fp=fp)
    age_comp_df = pd.read_csv('cleanup/age_comp_map.csv')
    
    # Load deliveries
    delivery_df = delivery.load_delivery(data_dir, delivery_clean_up_dict)

    # merge provider name to delivery
    prenatal_provider_df = provider_linkage.get_linkage(data_dir)
    delivery_df = delivery_df.merge(prenatal_provider_df, on=['record_id', 'site'], how='left')
    
    print(len(delivery_df), 'deliveries')
    print(delivery_df['prenatal_provider'].notna().sum(), 'deliveries linked to provider')
    print(delivery_df['prenatal_provider'].nunique(), 'providers linked')
    print(delivery_df[['record_id', 'site', 'prenatal_provider']].head())
    delivery_df['linked_to_provider'] = delivery_df['prenatal_provider'].notna()
    print(delivery_df.groupby('site')['linked_to_provider'].mean())

    # merge provider demographics
    if reporter == 'self':
        provider_demo_df = provider_demographics.load_provider_self_demographics(data_dir, provider_clean_up_dict)
    elif reporter == 'peer':
        provider_demo_df = provider_demographics.load_provider_peer_demographics(data_dir, provider_clean_up_dict)
    print(delivery_df['prenatal_provider'].values[1])
    print(delivery_df['prenatal_provider'].values[3] in provider_demo_df['prenatal_provider'].values)
    # print(len(set( np.concatenate([provider_demo_df['prenatal_provider'].values, delivery_df['prenatal_provider'].values]))))
    
    delivery_df = delivery_df.merge(provider_demo_df, on=['site', 'prenatal_provider'], how='left')
    delivery_df['linked_to_provider_demographics'] = delivery_df['Race'].notna()
    print(delivery_df.groupby('site')['linked_to_provider_demographics'].mean())
    missed_demo = delivery_df.loc[~delivery_df['linked_to_provider_demographics'] & delivery_df['linked_to_provider'],['site', 'prenatal_provider']].drop_duplicates()
    missed_demo.sort_values(['site', 'prenatal_provider']).to_csv('output/missed_demo.csv', index=False)

    # add comparison features
    delivery_df['Race_same'] = delivery_df['Race'] == delivery_df['race_upd2'] # provider, mother
    delivery_df['Ethnicity_same'] = delivery_df['Ethnicity'] == delivery_df['mom_ethn_backgr_f2'] # provider, mother
    delivery_df = delivery_df.merge(age_comp_df.rename(columns={'provider_age_bin':'Age_Range'}), on=['mat_age_bin', 'Age_Range'], how='left')
    
    delivery_df = delivery_df.dropna(subset='prenatal_provider')
    print('N deliveries, providers:', len(delivery_df), delivery_df['prenatal_provider'].nunique())
    delivery_df = delivery_df[delivery_df['Race'].notna() | delivery_df['Age_Range'].notna() | delivery_df['Gender_Identity'].notna()]
    print('N deliveries, providers:', len(delivery_df), delivery_df['prenatal_provider'].nunique())
    # delivery_df = delivery_df.dropna(subset=['Race', 'Age_Range', 'Gender_Identity'])
    # print('N deliveries, providers:', len(delivery_df), delivery_df['prenatal_provider'].nunique())
    
    # exit()
    # provider summary table    
    linked_cols = ["Race_same", "Ethnicity_same", "Age_difference"]
    provider_cols = provider_demographics.provider_cols + linked_cols

    for provider_col in provider_cols:
        # print(f'percent missing {provider_col}', delivery_df.[col].isna().mean())
        # print(delivery_df[[provider_col]].value_counts(dropna=False))
        print(delivery_df.drop_duplicates(subset=['prenatal_provider'])[[provider_col]].value_counts(dropna=False))
    
    summary_list = [create_demographic_summary(delivery_df, col) for col in provider_cols]
    summary = pd.concat(summary_list)
    summary.to_csv(f'output/{reporter}_provider_by_valid.csv', index=False)
    
    # patient summary table
    mom_demo_cols = ['mat_age_bin', "mom_ethn_backgr_f2", "marital_status_f_di2", "education_level_f", "race_upd2"]
    summary_list = [create_demographic_summary(delivery_df, col) for col in mom_demo_cols]
    summary = pd.concat(summary_list)
    summary.to_csv(f'output/mother_by_valid.csv', index=False)
    
    binary_map_dict = {
        'Race':dict(Black=0, Asian=0, White=1),
        'Age_Range':{"20-30":0, "31-40":0, "41-50":1, "51-60":1, "60+":1},
        'Ethnicity':{"Hispanic":1, "Non-Hispanic":0},
        'Training':{"attending":1, "fellow":0, "resident":0, "CNM":0, "NP/PA":0},
        'Specialty':{"MFM":1, "family medicine":0, "general OB-GYN":1},
        'Scope':{"OB only":0, "OB & GYN":1},
        "Gender_Identity":{"Man":0, "Woman":1},
        'Religion':{"atheist/agnostic":0, "catholic":1, "hindu":1,"Mormon":1, "jewish":1, "protestant":1},
        'Age_difference':{"younger":0, "same":1, "older":1},
        'Race_same':{True:0, False:1},
        'Ethnicity_same':{True:0, False:1},
        "Comfort with Counseling Re: Permanent Contraception":{"somewhat comfortable":0, "very comfortable":1}}
    for col, binary_map in binary_map_dict.items():
        delivery_df[f'{col}_binary'] = delivery_df[col].map(binary_map)
    delivery_df.to_csv(f'output/{reporter}_delivery_df.csv', index=False)
