import pandas as pd
from config import NUTS_PATH


# Class to handle the mapping between the Tecnalia data and the SPARQL query
class Mapping:
    def __init__(self):
        # Mapping dictionnary tecnalia -> SPARQL
        self.mapping_dict = {
            "project_id" : "proj:id",
            "euroregion" : "proj:location",
            "floorarea" : "bldg:livingArea",
            "ndwellings" : "bldg:nbDwellings",
            "sh.fuel" : "bldg:heatingEnergy",
            "sh.layout" : "bldg:centralHeating",
            "vent.system" : "bldg:ventilation",
            "type.window" : "bldg:glazingLevel",
            "area.pv" : "bldg:ratioPV_Roof"
        }

        # Mapping dictionnary Euroregion Code 2021 -> NUTS LV1
        self.df_mapping = self._get_euroregion_mapping_df()

    def _get_euroregion_mapping_df(self) -> pd.DataFrame:
        # Load the mapping file
        df_mapping = pd.read_csv(NUTS_PATH + 'euroregion_mapping.csv')
        return df_mapping

    def get_euroregion_name(self, code) -> str:
        # Get the euroregion name from the code
        row = self.df_mapping[self.df_mapping['Code 2021'] == code].squeeze()
        return row['NUTS LV1'] if not row.empty else None

    def get_euroregion_code(self, name) -> str:
        # Get the euroregion code from the name
        row = self.df_mapping[self.df_mapping['NUTS LV1'] == name].squeeze()
        return row['Code 2021'] if not row.empty else None

    def get_orientation(self, degree) -> str:
        # Get the orientation name from the degree
        max_degree = {
            0: "North",
            45: "North East",
            90: "East",
            135: "South East",
            180: "South",
            225: "South West",
            270: "West",
            315: "North West",
            360: "North"
        }
        diff = {x: abs(degree - x) for x in max_degree.keys()}
        min_degree = min(diff, key=diff.get)
        return max_degree.get(min_degree, "None")

    def get_central_heating(self, value) -> str:
        return value == "Central"

    def get_level(self, value) -> str:
        # Get the level name from the value

        if value >= 0.6:
            return "High"
        if value >= 0.3:
            return "Medium"
        if value >= 0.1:
            return "Low"

        return "None"