import itertools
import uuid
from functools import reduce
from SPARQLWrapper import SPARQLWrapper, JSON
from mapping import Mapping

SPARQLQuery = SPARQLWrapper(
    "http://localhost:3030/GenScen/query")
SPARQLRemove = SPARQLWrapper(
    "http://localhost:3030/GenScen/update")
SPARQLInsert = SPARQLWrapper(
    "http://localhost:3030/GenScen/update")


def _get_prefix():
    return f'''
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX proj: <https://nobatek.inef4.com/renovation/project#>
    PREFIX bldg: <https://nobatek.inef4.com/renovation/building#>
    PREFIX intv: <https://nobatek.inef4.com/renovation/intervention#>
    '''

def insert_data(data):
    """Function to insert the data into the SPARQL database."""

    # Check if the request body contains all the necessary parameters
    # Check Parameters
    all_parameters = ["euroregion", "sh.layout", "sh.fuel", "vent.system", "u.envelope", "floorarea", "ndwellings", "type.window", "u.roofs"]
    for key in all_parameters:
        if key not in data['data']['Parameters']:
            raise Exception(f"Parameters {key} not found in the request body")
    
    # Check Surfaces
    if "Surfaces" not in data['data']:
        raise Exception(f"Parameters surfaces not found in the request body")
    else:
        # Check if each surface contains the necessary parameters
        surfaceParameters = ["type", "orientation", "area", "name"]
        for key in surfaceParameters:
            for surface in data['data']['Surfaces']:
                if key not in surface:
                    raise Exception(f"Parameters {key} not found in Surface {surface} in the request body")
                if surface["type"] == "roof":
                    if "area.pv" not in surface:
                        raise Exception(f"Parameter area.pv not found in Surface {surface} in the request body")
    
    # Building
    mapping = Mapping()

    queryContent = f"""
    tst:pjct{data['data']['project_id']} rdf:type proj:Project ;
        {mapping.mapping_dict['project_id']} {data['data']['project_id']} ;
        {mapping.mapping_dict['euroregion']} proj:{mapping.get_euroregion_name(data['data']['Parameters']['euroregion'])} .

    tst:batiment-{data['data']['project_id']} rdf:type bldg:Building .

    tst:pjct{data['data']['project_id']} proj:building tst:batiment-{data['data']['project_id']} ;
        proj:targetThermal 1.0, 0.7, 0.5, 0.3 ;
        proj:targetElectricity 1.0, 0.7, 0.5, 0.3 .
    """

    # Facades
    
    facade_statements = []
    maxFacadeArea = 0
    roofArea = 0
    roofInsulation = 0

    for surface in data['data']['Surfaces']:
        # Type Wall
        if surface['type'] == "wall":
            orientation = mapping.get_orientation(int(surface['orientation']))
            facade_area = float(surface['area'])
            facade_statement = f"""
    tst:batiment-{data['data']['project_id']} bldg:hasFacade [
        bldg:area "{facade_area}"^^xsd:double ;
        bldg:orientation "{orientation}" ;
        bldg:facadeInsulation "{mapping.get_level(float(data['data']['Parameters']['u.envelope']))}" ;
    ] .
    """
            facade_statements.append(facade_statement)

            if facade_area > maxFacadeArea:
                maxFacadeArea = facade_area
        # Type Roof
        elif surface['type'] == "roof":
            roofArea = float(surface['area'])
            roofInsulation = mapping.get_level(float(data['data']['Parameters']['u.roofs']))

    queryContent += "".join(facade_statement for facade_statement in facade_statements)

    # Parameters
    
    queryContent += f"""
    tst:batiment-{data['data']['project_id']}"""

    for key, value in data['data']['Parameters'].items():
        if key in mapping.mapping_dict and key != "euroregion":
            # Check if the value need to be a double, a string or an integer
            if "dwellings" in key:
                queryContent += f"""
        {mapping.mapping_dict[key]} {value} ;"""
            elif value.replace('.', '', 1).isdigit():
                queryContent += f"""
        {mapping.mapping_dict[key]} "{value}"^^xsd:double ;"""
            else:
                queryContent += f"""
        {mapping.mapping_dict[key]} "{value}" ;"""
                
    queryContent += f"""
        bldg:maxFacadeArea "{maxFacadeArea}"^^xsd:double ;
        bldg:roofArea "{roofArea}"^^xsd:double ;
        bldg:roofInsulation "{roofInsulation}" ."""


    # Query construction

    query = f"""
    {_get_prefix() + "PREFIX tst: <https://nobatek.inef4.com/renovation/test#>" + "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>"}

    INSERT DATA 
    {{
        {queryContent}
    }}
    """
    SPARQLInsert.method= 'POST'
    SPARQLInsert.setQuery(query)
    result = SPARQLInsert.query()
    return result.response.code


def get_baseline():
     query = f"""   
        {_get_prefix()}

        SELECT ?str_type_intv ?scen (group_concat(?str_intv; separator=" | ") as ?intvs) ?label WHERE {{
            ?scen a [rdfs:subClassOf* proj:BaselineScenario];
                     rdfs:label ?label ;
                     proj:isMadeOf ?intv .
            ?intv intv:refines ?type_intv ;
                  rdfs:label ?str_intv.
            BIND(strafter(str(?type_intv), '#') as ?str_type_intv)
        }} GROUP BY ?str_type_intv ?scen ?label
    """
     return _format_basic(_execute(query), "baseline")


def get_nZeB():
    query = f"""   
        {_get_prefix()}

        SELECT ?str_type_intv ?scen (group_concat(?str_intv; separator=" | ") as ?intvs) ?label WHERE {{
            ?scen a [rdfs:subClassOf* proj:nZeBScenario];
                     proj:isMadeOf ?intv ;
                     rdfs:label ?label .
            ?intv intv:refines ?type_intv ;
                  rdfs:label ?str_intv.
            BIND(strafter(str(?type_intv), '#') as ?str_type_intv)
        }} GROUP BY ?str_type_intv ?scen ?label
        """
    return _format_basic(_execute(query), "nZeB")

def get_Ensnare_Passive():
    query = f"""   
        {_get_prefix()}

        SELECT ?scen_passive ?intvs_passive ?scen_active (group_concat(DISTINCT ?active_desc; separator=" && ") as ?intvs_active) ?lbl_passive ?lbl_active
        WHERE {{
            ?scen_active a [rdfs:subClassOf* proj:EnsnareScenario_Active];
                proj:refines ?scen_passive ;
                rdfs:label ?lbl_active .
            ?intv_active intv:scenario ?scen_active ;
                         intv:needed_surface ?surface ;
                         intv:facade [bldg:orientation ?orientation] ;
                         a ?intv_type .
            
            BIND(concat(strafter(str(?intv_type), 'needed_'), '_', str(?orientation), ':', str(?surface)) as ?active_desc)
            {{SELECT ?scen_passive (group_concat(DISTINCT ?res; separator=" || ") as ?intvs_passive) ?lbl_passive {{
              ?scen_passive a [rdfs:subClassOf* proj:EnsnareScenario_Passive];
                       a ?type ; proj:isMadeOf ?intv ;
                       rdfs:label ?lbl_passive .
              ?intv intv:refines ?type_intv ;
                    rdfs:label ?intv_desc .
                    BIND(concat(strafter(str(?type_intv), '#'), ':', ?intv_desc) as ?res)
              FILTER(?type_intv IN (intv:InsulateFacade, intv:InsulateRoof, intv:ChangeWindows))
             }} group by ?scen_passive ?lbl_passive}}
          }} group by ?scen_active ?scen_passive ?intvs_passive ?lbl_active ?lbl_passive
        """
    return _format_ensnare(_execute(query))


def _execute(query):
    """Function to execute a SPARQL query. Returns the resulting bindings.
    @:param query: a string for the SPARQL query to execute.
    @:returns a list of bindings."""
    SPARQLQuery.setReturnFormat(JSON)
    SPARQLQuery.setQuery(query)
    try:
        result = SPARQLQuery.queryAndConvert()
        results = result['results']['bindings']
        return results  # {k: results[k]['value'] for k in results.keys()}
    except Exception as e:
        print(e)

def _format_basic(scenario, name):
    """Function to format a simple scenario. The input scenario should result from a SPARQL query on either
    baseline or nZeB scenarios. Produces a dictionary.
    @:param scenario: the scenario resulting from a SPARQL query.
    @:param name: the name of the scenario. Should be either 'baseline' or 'nZeB'
    @:returns a dictionary formatting the results in a friendly and comprehensive way, to produce a JSON file"""
    desc_scenario = {}
    for intv in scenario:
        desc_scenario[intv['str_type_intv']['value']] = intv['intvs']['value']
    desc_scenario["id"] = str(uuid.uuid1())
    if name == "baseline":
        desc_scenario["description"] = "Baseline scenario - low ambitions, no renewable"
    elif name == "nZeB":
        desc_scenario["description"] = "Positive scenario - high ambitions, as many renewable as possible"
    return {name : desc_scenario}

def _format_ensnare(scenarios):
    """Function to format the resulting ENSNARE scenarios."""
    results = []
    passive = {}
    active = {}
    labels = {}
    # print(scenarios)
    for scenario in scenarios:
        # format passive
        id_passive = scenario['scen_passive']['value']
        desc_passive = scenario['lbl_passive']['value']
        labels[id_passive] = desc_passive
        if id_passive not in passive.keys():
            passive[id_passive] = _format_passive(scenario['intvs_passive'])
        # add active scenarios
        if id_passive not in active:
            active[id_passive] = []
        active[id_passive].append(_format_active(scenario['intvs_active'], scenario['lbl_active']['value']))

    # create the final JSON file
    for id_passive in passive.keys():
        for passive_scen in passive[id_passive]:
            format_scenario =  {'id': str(uuid.uuid1()), 'description': labels[id_passive]}
            for it in passive_scen:
                intervention, material = it.split(':')
                format_scenario[intervention] = material
                format_scenario['active'] = active[id_passive]
            results.append(format_scenario)
    return {"ensnare_scenarios" : results}

def _format_passive(intvs_passive):
    intvs = intvs_passive['value'].split('||')
    # create dictionary of intervention
    passive_ = {}
    for intv in intvs:
        action, material = intv.strip().split(':')
        if action in passive_.keys():
            passive_[action].append(intv.strip())
        else:
            passive_[action] = [intv.strip()]
    passive__ = list(map(lambda x: list(passive_[x]), passive_.keys()))
    # compute all combinations
    return list(itertools.product(*passive__))

def _format_active(intvs_active, description):
    intvs = intvs_active['value'].split('&&')
    # create dictionary of intervention
    facades = {"description": description}
    for intv in intvs:
        action, surface = intv.strip().split(':')
        system, facade = action.split('_')
        if facade not in facades:
            facades[facade] = {}
        facades[facade][system+'_area'] = float(surface)
    return facades

def remove_data():
    SPARQLRemove.setReturnFormat(JSON)
    SPARQLRemove.setMethod('POST')
    SPARQLRemove.setQuery('CLEAR ALL')
    return SPARQLRemove.query()