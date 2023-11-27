import legend_data_monitor as ldm
import os
import sys

from sf_data import *

class Partition():
    """
    Class containing information about a partition:
    - channel map of each run in the partition
    - paths to par pht jsons with survival fraction information for each run

    run_list [list]: list of strings of format pXX-rXXX
    data_path [str]: path to top level data folder (before version)

    Example:
    >>> partition = Partition(["p07-r007", "p07-r008"], "/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/ref/")
    >>> partition.channel_maps

    {'p07-r007':
        name location position cc4_id cc4_channel daq_crate daq_card  ....
    channel                                                                      
    ch1078400  V07302A        8       10     F2           2         1        1   .... 
    ch1078405  B00002A        9        1     C1           0         1        1   ....
    ...            ...      ...      ...    ...         ...       ...      ...   ....  
    ch1121604  V05261A        8        8     F2           0         0       12   .... 
    ch1121605  V05268A        8        9     F2           1         0       12   .... 
              
    'p07-r008':               
        name location position cc4_id cc4_channel daq_crate daq_card  \
    channel                                                                      
    ch1078400  V07302A        8       10     F2           2         1        1   
    ch1078405  B00002A        9        1     C1           0         1        1   
    ...
    }

    >>> partition.sf_info
    {'p07-r007': '/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/ref/v02.00/generated/par/pht/cal/p07/r007/l200-p07-r007-cal-20230918T141158Z-par_pht.json',
    'p07-r008': '/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/ref/v02.00/generated/par/pht/cal/p07/r008/l200-p07-r008-cal-20230925T080300Z-par_pht.json'}
    """    

    def __init__(self, run_list, data_path):
        self.run_list = run_list
        # data path check
        path_error(data_path)
        self.data_path = data_path

        # SF info
        self.sf_info = self._get_sf_info()

        # dictionary of channel maps for each run of the partition
        self.channel_maps = self._get_channel_maps()


    def get_detector_sfs(self, sf_fields):
        """
        Returns a table of SFs for each detector.

        sf_fields [dict]: dictionary containing names of SFs to put in the table
            e.g.("sf_TlDEP") and json fields where to take the value from
            Example: {"sf_TlDEP": ["results", "aoe", "low_side_sfs", "1592.5"]}

        Example output:
                sf_TlDEP  sf_TlDEP_err       run     name
        channel                                              
        ch1104000  89.302646     89.302646  p07-r007  V02160A
        ch1104001  89.796233     89.796233  p07-r007  V02160B
        ch1104002  89.479456     89.479456  p07-r007  V05261B
        ...
        """
        print("Getting survival fractions from pht jsons")
        df_sf = pd.DataFrame()
        for period_run in self.sf_info:
            print(period_run)
            # SF data from this run for each channel
            sf_data = SFdata(self.sf_info[period_run])
            # SF table for channels
            sf_channel_table = sf_data.construct_sf_table(sf_fields)
            # add period and rund info
            sf_channel_table["run"] = period_run 
            # map to detector name. Note: can also preserve string, position, status etc.
            sf_channel_table = pd.concat([sf_channel_table, self.channel_maps[period_run]["name"].reindex(sf_channel_table.index)], axis=1)
            # add to the table to the global table for all runs
            df_sf = pd.concat([df_sf, sf_channel_table], axis=0)
        return df_sf


    def _get_channel_maps(self):
        """
        Get channel map for each run in this partition.

        Returns dictionary with keys pXX-rXXX containing channel map DataFrames
        """
        channel_maps = {}
        for period_run in self.run_list:
            print(period_run)
            # e.g. p08-r008
            period, run = period_run.split("-")
            # load channel map for future channel mapping of per channel SF results
            geds = ldm.Subsystem('geds', experiment='L200', period=period, runs=int(run[1:]), type='cal',
                version='v02.00',  path=self.data_path)
            run_channel_map = geds.channel_map
            # in the jsons, channels are saved as "chXXX" -> convert to this format for convenience
            run_channel_map["channel"] = run_channel_map["channel"].apply(lambda x: f"ch{x}")
            # set index to channel for convenience
            channel_maps[period_run] = run_channel_map.set_index("channel")
        return channel_maps
    

    def _get_sf_info(self):
        """
        Get paths to par pht cal jsons containing SF info
        """
        path_elements = ["v02.00", "generated", "par", "pht", "cal"]
        path_to_par_cal_dir = os.path.join(self.data_path, *path_elements)
        path_error(path_to_par_cal_dir)            
        
        par_jsons = {}
        for period_run in self.run_list:
            period, run = period_run.split("-")
            path_to_run_json = os.path.join(path_to_par_cal_dir, period, run)
            path_error(path_to_run_json)
            # there is one json in each folder
            par_json = [x for x in os.listdir(path_to_run_json) if ".json" in x][0]
            par_jsons[period_run] = os.path.join(path_to_run_json, par_json)

        return par_jsons


# ------- helper function

def path_error(path):
    if not os.path.exists(path):
        print("The path:")
        print(path)
        print("does not exist!")
        sys.exit(1)    