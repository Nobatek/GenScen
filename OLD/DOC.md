GenScen - Generating renovation scenarios
===

### Structure of the repository

The repository is made of different files:
* `GenScen.ttl` is the TBox - contains concepts related to energy renovation scenarios, the different criterias used, the different elements impacted...
* A set of inference rules files:
    * `rules.dlog` contains inference rules that are generic to renovation scenarios. A first step towards guiding the end user towards actions to be made on the building
    * `baseline.dlog`: based on the knowledge inferred by `rules.dlog`, the inference rules it contains are used to generate baseline scenarios.
    * `utils.dlog` contains another set of inference rules that are typically transitive rules, reflexive...
* `TestProject.ttl` is a sample project used to test the rules created.

The `start.rdfox` file contains command lines to be used to run RDFox on this use case.

### GenScen: concepts and relations
The `GenScen.ttl` file is the core ontology used in the project. It contains all the concepts and relations that are needed to formalize renovation scenarios.
* A `RenoProject` is made of different prooperties that are associated to it through the `rscen:forProject` relation, which domain is `rscen:Criterion`. Such criteria can be of different kind, such as Building conditions, Climate conditions, or Financial constraints.
* A `RenoScenario` which is related to a `RenoProject`, and is made of of different `RenoAction`.
* Then a hierarchical structure with:
    * `RenoApproach` the more generic concept to describe a renovation acts to be performed in the building. Those are typically 'façade insulation', 'change windows'...
    * `RenoAlternative` which are refined approaches; for instance, 'external façade insulation', 'change windows for double glazed windows'...
    * `RenoAction`: which are the most detailed level: 'external façade insulation with 14cm mineral wool', 'install double glazed windows with wooden frame'...

### Run the project
Run under your terminal: `path/tp/rdfox/RDFox sandbox`

to open the RDFOx command terminal.
Type the following commands:
`endpoint start` - to launch the endpoint\
`dstore create reno_scen` - create a datastore called reno_scen\
`active reno_scen` - activate the datastore\
`import +p GenScen.ttl` - import the TBox file\
`set output out` - to ensure results of queries are displayed in the command terminal\
`import utils.dlog`\
`import rules.dlog`\
`import baseline.dlog` to import all the datalog rule files needed\
`import +p TestProject.ttl` to import the sample project.\
`select ?s where {?s rscen:forProject <https://nobatek.inef4.com/data-models/renovation-scenario/test#pjct3> }` 
