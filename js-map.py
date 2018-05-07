from flask import Flask, render_template
import pymongo
import json

app = Flask(__name__)


@app.route('/')
def index():

    client = pymongo.MongoClient("mongodb+srv://admin:serhienko_world$@worldbank-qmvdt.mongodb.net/test")
    cursor = client.world_bank.world.find({})

    code3_with_sum = {}
    code3_with_projects = {}
    objects_list_clear = []
    objects_list_errors = []
    global_list = []

    class MapObj:
        def __init__(self, project_name, country_name, country_code_2, country_code_3, lend_project_cost):
            self.project_name = project_name
            self.country_name = country_name
            self.country_code_2 = country_code_2
            self.country_code_3 = country_code_3
            self.lend_project_cost = lend_project_cost

    countries_json_file = open('file/countries.json', 'r')  # File with mapping (different codes for countries)
    countries_json = json.load(countries_json_file)
    countries_json_file.close()

    def give_name(code_2, name_in_json):  # Find name of country in mapping file
        for c in countries_json:
            if code_2 in c.values():
                return c['name']
        return name_in_json

    def give_3_code(code_2):  # Find 3 symbols code of country im mapping file
        for c in countries_json:
            if code_2 in c.values():
                return c['alpha-3']
        return "CodeNotFound"

    for doc in cursor:
        mo = MapObj(
            doc['project_name'].title(),
            give_name(doc['countrycode'], doc['country_namecode']),
            doc['countrycode'],
            give_3_code(doc['countrycode']),
            doc['lendprojectcost']
        )
        if mo.country_code_3 != "CodeNotFound":
            objects_list_clear.append(mo)
        elif mo.country_code_3 == "CodeNotFound":
            objects_list_errors.append(mo)
        else:
            objects_list_errors.append(mo.country_code_2 + " : other error")

    # 1 create list of sums

    for o in objects_list_clear:
        if o.country_code_3 not in code3_with_sum.keys():
            code3_with_sum[o.country_code_3] = o.lend_project_cost
        elif o.country_code_3 in code3_with_sum.keys():
            code3_with_sum[o.country_code_3] += o.lend_project_cost
        else:
            print("Error in #2")

    # 2 create dictionary of key:value (country code: list of projects)

    for o1 in objects_list_clear:
        if o1.country_code_3 not in code3_with_projects.keys():
            code3_with_projects[o1.country_code_3] = "<br>" + o1.project_name + ": " + str(o1.lend_project_cost)
        elif o1.country_code_3 in code3_with_projects.keys():
            code3_with_projects[o1.country_code_3] += "<br>" + o1.project_name + ": " + str(o1.lend_project_cost)
        else:
            print("Error in #2")

    # 3 create list for JavaScript ([[CountryCode, Sum, [Project1, Project2]]])

    for k, v in code3_with_sum.items():
        short_list = [k, v]
        for k1, v1 in code3_with_projects.items():
            if k == k1:
                projects_list = [v1]
                short_list.append(projects_list)
        global_list.append(short_list)

    return render_template('index.html', global_list=global_list)