import pandas as pd 
import os
import numpy as np
import json 

def load_delivery(data_dir, delivery_clean_up_dict):

    delivery_df = pd.read_csv(os.path.join(data_dir, "all_sites_primary_vars.csv"))

    # features
    delivery_df['date_form_present_int'] = delivery_df['date_form_missing'].map({"missing":0, "not missing":1})
    delivery_df['form_valid_int'] = delivery_df['form_valid'].map({"no":0, "yes":1})

    # clean 
    for col_name, value_map in delivery_clean_up_dict.items():
        delivery_df[col_name] = delivery_df[col_name].map(value_map)
    
    # bin maternal age
    delivery_df["mat_age_bin"] = pd.cut(delivery_df["mat_age"], range(15,55,5), right=True, 
                                        labels=["16-20", "21-25", "26-30", "31-35", "36-40", "41-45", "46-50"])  # include right
    # delivery_df[, "mat_age_bin"] = factor(delivery_df$mat_age_bin, levels = c("16-20", "21-25", "26-30", "31-35", "36-40", "41-45", "46-50"))
    
    return delivery_df


    
if __name__ == '__main__':

    data_dir = os.environ['DATA_DIR']

    with open('cleanup/delivery_clean_up_list.json', 'r') as fp:
        delivery_clean_up_dict = json.load(fp=fp)
    
    delivery_df = load_delivery(data_dir, delivery_clean_up_dict)
    
    print(delivery_df['site_f'].value_counts())

    print(delivery_df.notna().mean())
    