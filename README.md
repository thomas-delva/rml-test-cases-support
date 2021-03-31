# RML Test-Cases support

Test the capabilities of your RML engine with the [RML test cases](http://rml.io/test-cases). Use the resources provided in this repository to automatically generate an EARL report with your results. Go to the [RML implementation report](http://github.com/RMLio/rml-implementation-report) repository to see how to include the generated report.

**IMPORTANT INFORMATION ABOUT THE RML TEST CASES SUPPORT:** 
- This repository does NOT include any engine report
- The support resources provided here can be: forked, downloaded or cloned but no PR with the report is needed. A recommendation to maintain up-to-date the resources of this repository is to add a submodule directly to your github repo. 
- Read carefully the documentation provided, and open an issue if you have any question or doubt.

## Requirements for creating the EARL implementation report:

- Linux based OS
- Docker and docker-compose
- Python
- Java

## RDBMS coverage and properties info:

- MySQL (`port = 3306`)
- PostgreSQL (`port = 5432`)
- SQLServer (not suppor at this moment)

Connection properties for any RDBMS are: `database = rml, user = rml, password = rml`.

For testing purposes, **mapping path is invariable, it is always `./mapping.ttl`**


## Steps to generate the results from the R2RML test-cases:

1. Create a submodule (recommended) or fork/clone/download this repository.
2. Include a way to run your engine with the resources of this folder.
3. Install the requirements of the script `python3 -m pip install -r requirements.txt`
4. Modify the config.ini file with your information. For the correspoding configurating of your R2RML engine, remember that the path of the **mapping file is always ./mapping.ttl**. For example:

```
[tester]
tester_name: David Chaves # tester name
tester_url: https://dchaves.oeg-upm.net/ # tester homepage
tester_contact: dchaves@fi.upm.es # tester contact

[engine]
test_date: 2021-01-07 # engine test-date (YYYY-MM-DD)
engine_version: 3.12.5 # engine version
engine_name: SDM-RDFizer # engine name
engine_created: 2019-12-01 # engine date created (YYYY-MM-DD)
engine_url: https://github.com/SDM-TIB/SDM-RDFizer # URL of the engine (e.g., GitHub repo)


[properties]
database_system: csv,xml,json,mysql,postgresql,sqlserver,sparql # select from 1 to all
output_results: ./output.nq # path to the result graph of your engine
output_format: ntriples # output format of the results from your engine
engine_command: python3 rdfizer/run_rdfizer.py config.ini # command to run your engine
```

5. Run the script `python3 test.py config.ini`
6. Your results will appear in `results.ttl` in RDF and in `results.csv` in CSV.
7. Upload or update the obtained results the access point you have provided in the configuration step.
8. For each new version of your engine, repeat the process from step 4 to 7.


Overview of the testing steps:
![Testing setp](misc/test.png?raw=true "Testing setp")

