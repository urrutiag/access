import pandas as pd 
import os
import numpy as np


def get_linkage(data_dir):

    metrohealth_provider_df = pd.read_csv(os.path.join(data_dir, "_metro_all_vars.csv"))
    metrohealth_provider_df = metrohealth_provider_df.rename(columns={"op_prenatal_most_prevalent_visit_provider":"prenatal_provider"})
    metrohealth_provider_df = metrohealth_provider_df[["record_id", "site", "prenatal_provider"]]

    ucsf_provider_df = pd.read_csv(os.path.join(data_dir, "_ucsf_all_vars.csv"))
    ucsf_provider_df = ucsf_provider_df.rename(columns={"attending_prenatal":"prenatal_provider"})
    ucsf_provider_df = ucsf_provider_df[["record_id", "site", "prenatal_provider"]]
    ucsf_provider_df['prenatal_provider'] = ucsf_provider_df['prenatal_provider'].str.lower()
    
    uab_provider_df = pd.read_excel(os.path.join(data_dir, "ST20_MB_POST_STERIL_OB_PROVIDER_DI.xlsx"), sheet_name='Sheet 1')   
    uab_provider_visits_df = uab_provider_df.groupby(['RECORD_ID', 'PROVIDER']).size().reset_index(name='visit_count')
    uab_provider_visits_df['max_visit_count'] = uab_provider_visits_df.groupby(['RECORD_ID'])['visit_count'].transform('max')
    uab_provider_most_prevalent_df = uab_provider_visits_df[uab_provider_visits_df['visit_count']==uab_provider_visits_df['max_visit_count']].groupby('RECORD_ID').agg('first').reset_index()
    uab_provider_most_prevalent_df['site'] = 'UAB'
    uab_provider_most_prevalent_df = uab_provider_most_prevalent_df.rename(columns={'PROVIDER':'prenatal_provider', 'RECORD_ID':'record_id'})
    uab_provider_most_prevalent_df = uab_provider_most_prevalent_df.drop(columns=['visit_count', 'max_visit_count'])

    prenatal_provider_df = pd.concat([metrohealth_provider_df, ucsf_provider_df, uab_provider_most_prevalent_df], ignore_index=True)
    
    return prenatal_provider_df



if __name__ == '__main__':

    data_dir = '/mnt/c/Users/Urrutia/Dropbox/Documents/UNC_OBGYN/kavita_access/data/'

    prenatal_provider_df = get_linkage(data_dir)
    print(prenatal_provider_df.head())


