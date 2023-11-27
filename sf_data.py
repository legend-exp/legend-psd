import json
import pandas as pd

class SFdata():
    """
    Object containing SF data based on pygama results.

    path_to_json [str]: path to par pht cal json

    Example:
    >>> sfdata = sf_data.SFdata('/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/ref/v02.00/generated/par/pht/cal/p07/r007/l200-p07-r007-cal-20230918T141158Z-par_pht.json')
    >>> sfdata.construct_sf_table()
    """    
    def __init__(self, path_to_json):
        self.sf_data = json.load(open(path_to_json))

    def construct_sf_table(self, sf_fields):
        '''        
        Returns table of SFs for each channel.

        sf_fields [dict]: dictionary with names of SFs (e.g. "sf_TlDEP") and a list of fields by which to locate that SF
        Example:
        { "sf_TlDEP": ["results", "aoe", "low_side_sfs", "1592.5"] }
        The dict keys will become table column names.
        If the path given in the dict is not found in json for a certain channel, it will be assigned null in the table        
        '''
        # columns are names of SFs and channel
        columns = list(sf_fields.keys())
        columns.append("channel")
        # the index of this dataframe will be channel
        df = pd.DataFrame(columns=columns)
        df = df.set_index("channel")

        # loop over channels in json
        for channel in self.sf_data:
            # dict entry for this channel
            this_channel = self.sf_data[channel]

            # go into jsons field by field
            try: 
                for sf in sf_fields:                
                    # start with top level
                    this_sf_data = this_channel.copy()                
                    for field in sf_fields[sf]:
                        this_sf_data = this_sf_data[field]

                    # now we end up with the final field which has fields "sf" and "sf_err"
                    df.at[channel, sf] = this_sf_data["sf"]
                    df.at[channel, sf+"_err"] = this_sf_data["sf"]
            except:
                # some fields don't have info
                df.at[channel, sf] = None

        return df

