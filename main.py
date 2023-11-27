import json
from partition import *

def get_survival_fractions(settings_path):
    settings = json.load(open(settings_path))

    df_res = pd.DataFrame()
    for partition_name in settings["partitions"]:
        print(f"Partition {partition_name}")
        # list of strings of format pXX-rXXX
        partition_list = settings["partitions"][partition_name] 
        # partition knows channel maps corresponding to each run as well as paths to json files with SF info
        partition = Partition(partition_list, settings["data_path"])
        # print(partition.channel_maps)
        # print(partition.sf_info)

        # this functions takes names of SFs and paths to their values in json
        df_sf = partition.get_detector_sfs(settings["survival_fractions"])
        df_sf["partition"] = partition_name

        # add to total table for all partitions
        df_res = pd.concat([df_res, df_sf], axis=0)

    return df_res   