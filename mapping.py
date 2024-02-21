import pandas as pd

class Mapping:
    def __init__(self):
        self.mapping_dict = {
            "project_id" : "proj:id",
            "euroregion" : "proj:location",
            "wallarea" : "bldg:hasFacade -->  bldg:area", # Facades type wall
            "roofarea" : "bldg:roofArea", # Facades type roof
            "floorarea" : "bldg:livingArea",
            "ndwellings" : "bldg:nbDwellings",
            "u.envelope" : "bldg:hasFacade -->  bldg:facadeInsulation", # get_level(value)
            "u.roofs" : "bldg:roofInsulation", # get_level(value)
            "sh.fuel" : "bldg:heatingEnergy",
            "sh.layout" : "bldg:centralHeating",
            "ventilation.system" : "bldg:ventilation",
            "type.window" : "bldg:glazingLevel",
            "area.pv" : "bldg:ratioPV_Roof",
            # : "bldg:maxFacadeArea", # Calculated
            # : "bldg:hasFacade", # Facades type wall
            # : "bldg:hasFacade -->  bldg:orientation", # get_orientation(degree)
            # : "bldg:glazingRatio" Not used
        }
        self.df_mapping = self._get_euroregion_mapping_df()

    def _get_euroregion_mapping_df(self):
        dataframe = pd.read_excel('NUTS2021.xlsx', sheet_name='NUTS & SR 2021', header=None)
        df_code_2021 = pd.DataFrame(dataframe[0])
        df_nuts_lv1 = pd.DataFrame(dataframe[2])

        # Drop rows with invalid length
        df_code_2021 = df_code_2021[df_code_2021[0].astype(str).str.len() == 3]

        df_mapping = pd.concat([df_code_2021, df_nuts_lv1], axis=1)
        df_mapping.columns = ['Code 2021', 'NUTS LV1']
        df_mapping.dropna(inplace=True)
        return df_mapping

    def get_euroregion_name(self, code):
        row = self.df_mapping[self.df_mapping['Code 2021'] == code].squeeze()
        return row['NUTS LV1'] if not row.empty else None

    def get_euroregion_code(self, name):
        row = self.df_mapping[self.df_mapping['NUTS LV1'] == name].squeeze()
        return row['Code 2021'] if not row.empty else None

    def get_orientation(self, degree):
        switch = {
            0: "Nord",
            45: "Nord-Est",
            90: "Est",
            135: "Sud-Est",
            180: "Sud",
            225: "Sud-Ouest",
            270: "Ouest",
            315: "Nord-Ouest"
        }

        return switch.get(degree, "None")

    def get_level(self, value):
        level = "None"
        
        if value >= 0.6:
            level = "High"
        elif value >= 0.3:
            level = "Medium"
        elif value >= 0.1:
            level = "Low"

        return level