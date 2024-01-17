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
    delivery_summary['form_not_valid'] = delivery_summary['deliveries'] - delivery_summary['form_valid']
    delivery_summary['form_not_valid_proportion'] = 1 - delivery_summary['form_valid_proportion']
    delivery_summary['form_valid_proportion_fmt'] = delivery_summary['form_valid_proportion'].map('{:,.1%}'.format)
    delivery_summary['form_not_valid_proportion_fmt'] = delivery_summary['form_not_valid_proportion'].map('{:,.1%}'.format)

    return delivery_summary


if __name__ == '__main__':

    data_dir = '/mnt/c/Users/Urrutia/Dropbox/Documents/UNC_OBGYN/kavita_access/data/'
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
    
    # merge provider demographics
    if reporter == 'self':
        provider_demo_df = provider_demographics.load_provider_self_demographics(data_dir, provider_clean_up_dict)
    elif reporter == 'peer':
        provider_demo_df = provider_demographics.load_provider_peer_demographics(data_dir, provider_clean_up_dict)
    delivery_df = delivery_df.merge(provider_demo_df, on=['site', 'prenatal_provider'], how='left')

    # add comparison features
    delivery_df['race_same'] = delivery_df['Race'] == delivery_df['race_upd2'] # provider, mother
    delivery_df['ethnicity_same'] = delivery_df['Ethnicity'] == delivery_df['mom_ethn_backgr_f2'] # provider, mother
    delivery_df = delivery_df.merge(age_comp_df.rename(columns={'provider_age_bin':'Age_Range'}), on=['mat_age_bin', 'Age_Range'], how='left')
    
    # provider summary table
    # TODO run all cols, concat and save csv
    cols=["Race",  "Age_Range", "Ethnicity", "Training", "Specialty",
          "Scope", "Gender_Identity", "Religion", "Comfort with Counseling Re: Permanent Contraception", 
          "Race_same", "Ethnicity_same", "Age_difference"]
    summary = create_demographic_summary(delivery_df, col='Race')
    print(summary)

    # patient summary table
    mom_demo_cols = ['mat_age_bin', "mom_ethn_backgr_f2", "marital_status_f_di2", "education_level_f", "race_upd2"]
    summary = create_demographic_summary(delivery_df, col='mat_age_bin')
    print(summary)
