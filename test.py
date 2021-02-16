from configparser import ConfigParser, ExtendedInterpolation
from rdflib import Graph, RDF, Namespace, compare, Literal, URIRef
from rdflib_hdt import HDTStore, optimize_sparql
import mysql.connector
import psycopg2
import os
import sys
import csv


def media_type_from_source(source_type):
    if source_type == "csv":
        return "\"text/csv\" ."
    elif source_type == "json":
        return "\"application/json\" ."
    elif source_type == "xml":
        return "\"application/xml\" ."
    elif source_type == "mysql" or source_type == "postgresql":
        return "\"application/sql\" .\n \tFILTER (regex(?test_id,\"" + source_type + "\",\"i\"))"
    else:
        print("Provide a correct source type")
        sys.exit()


def test_from_source_type(source_type):
    database = False
    if source_type == "mysql" or source_type == "postgresql":
        database_up(source_type)
        database = True

    q1 = """SELECT DISTINCT ?test_uri ?test_id WHERE { 
        ?test_uri rdf:type <http://www.w3.org/ns/earl#TestCase> . 
        ?test_uri <http://purl.org/dc/terms/identifier> ?test_id .
        ?test_uri <http://purl.org/dc/terms/hasPart> ?part .
        ?part rdf:type <http://www.w3.org/ns/dcat#Dataset> .
        ?part <http://www.w3.org/ns/dcat#distribution> ?dist .
        ?dist <http://www.w3.org/ns/dcat#mediaType> """ + media_type_from_source(source_type) + """
        
    } ORDER BY ?test_uri"""

    for r in manifest_graph.query(q1):
        test_id = r.test_id
        test_uri = r.test_uri
        os.system("cp ./test-cases/" + test_id + "/* .")
        if database:
            database_load(source_type)
        q2 = """ASK {<""" + test_uri + """> <http://www.w3.org/2006/03/test-description#expectedResults> 
        <http://rml.io/ns/test-case/InvalidRulesError>}"""
        expected_output = not bool(manifest_graph.query(q2))
        run_test(test_id, expected_output, source_type)
    if database:
        database_down(source_type)


def run_test(t_identifier, expected_output, source_type):
    expected_output_graph = Graph()

    if os.path.isfile(config["properties"]["output_results"]):
        os.system("rm " + config["properties"]["output_results"])

    if expected_output:
        expected_output_graph.parse("./output.nq", format="nquads")

    os.system(config["properties"]["engine_command"] + " > test-cases/" + t_identifier + "/engine_output-" + source_type + ".log")

    # if there is output file
    if os.path.isfile(config["properties"]["output_results"]):
        os.system("cp " + config["properties"][
            "output_results"] + " test-cases/" + t_identifier + "/engine_output-" + source_type + ".nq")
        # and expected output is true
        if expected_output:
            output_graph = Graph()
            iso_expected = compare.to_isomorphic(expected_output_graph)
            # trying to parse the output (e.g., not valid RDF)
            try:
                output_graph.parse(config["properties"]["output_results"],
                                   format=config["properties"]["output_format"])
                iso_output = compare.to_isomorphic(output_graph)
                # and graphs are equal
                if iso_expected == iso_output:
                    result = passed
                # and graphs are distinct
                else:
                    result = failed
            # output is not valid RDF
            except:
                result = failed

        # and expected output is false
        else:
            result = failed
    # if there is not output file
    else:
        # and expected output is true
        if expected_output:
            result = failed
        # expected output is false
        else:
            result = passed

    results.append(
        [config["tester"]["tester_name"], config["engine"]["engine_name"], source_type, t_identifier, result])
    print(t_identifier + "," + result)


def database_load(database_type):
    if database_type == "mysql":
        cnx = mysql.connector.connect(user='rml', password='rml', host='127.0.0.1', database='rml')
        cursor = cnx.cursor()
        for statement in open("resource.sql"):
            cursor.execute(statement)
        cnx.commit()
        cursor.close()
        cnx.close()

    elif database_type == "postgresql":
        cnx = psycopg2.connect("dbname='rml' user='rml' host='localhost' password='rml'")
        cursor = cnx.cursor()
        for statement in open("resource.sql"):
            cursor.execute(statement)
        cnx.commit()
        cursor.close()
        cnx.close()


def database_up(database_type):
    if database_type == "mysql":
        os.system("docker-compose -f docker-databases/docker-compose-mysql.yml stop")
        os.system("docker-compose -f docker-databases/docker-compose-mysql.yml rm --force")
        os.system("docker-compose -f docker-databases/docker-compose-mysql.yml up -d && sleep 30")
    elif database_type == "postgresql":
        os.system("docker-compose -f docker-databases/docker-compose-postgresql.yml stop")
        os.system("docker-compose -f docker-databases/docker-compose-postgresql.yml rm --force")
        os.system("docker-compose -f docker-databases/docker-compose-postgresql.yml up -d && sleep 30")


def database_down(database_type):
    if database_type == "mysql":
        os.system("docker-compose -f databases/docker-compose-mysql.yml stop")
        os.system("docker-compose -f databases/docker-compose-mysql.yml rm --force")
    elif database_type == "postgresql":
        os.system("docker-compose -f databases/docker-compose-postgresql.yml stop")
        os.system("docker-compose -f databases/docker-compose-postgresql.yml rm --force")


if __name__ == "__main__":
    config_file = str(sys.argv[1])
    if not os.path.isfile(config_file):
        print("The configuration file " + config_file + " does not exist.")
        print("Aborting...")
        sys.exit(1)

    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_file)
    sources = config["properties"]["sources"].split(",")
    optimize_sparql()
    manifest_graph = Graph(store=HDTStore("./metadata.hdt"))

    results = [["tester", "platform", "source", "testid", "result"]]

    failed = "failed"
    passed = "passed"

    for source in sources:
        test_from_source_type(source)

    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(results)
