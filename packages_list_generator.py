from enum import Enum
from bioconda_utils import utils
import requests
import sys
import re
import csv

bio_tools_pkg_url = 'https://www.bio.tools/api/tool'

#toolType = {'Workbench', 'Desktop application', 'Web application', 'Plug-in', 'Suite', 'Database portal', 'SPARQL endpoint', 'Command-line tool', 'Workflow', 'Ontology', 'Library', 'Web API', 'Web service', 'Script'}
# {'Perl', 'Shell', 'Fortran', 'C', 'Python', 'Java', 'R', 'PHP', 'C++', 'Ruby', 'MATLAB'}

class Keys(Enum):
    TOOLTYPE = "toolType"
    LANGUAGE = "language"

class ToolTypes(Enum):
        WORKBENCH = "Workbench"
        DESKTOP_APPLICATION = "Desktop application"
        WEP_APPLICATION = "Web application"
        PLUG_IN = "Plug-in"
        SUITE = "Suite"
        DATABASE_PORTAL = "Database portal"
        SPARQL_ENDPOINT = "SPARQL endpoint"
        COMMAND_LINE_TOOL = "Command-line tool"
        WORKFLOW = "Workflow"
        ONTOLOGY = "Ontology"
        LIBRARY = "Library"
        WEB_API = "Web API"
        WEB_SERVICE = "Web service"
        SCRIPT = "Script"
    
class Language(Enum):
        PERL = "Perl"
        SHELL = "Shell"
        FORTRAN = "Fortran"
        C = "C"
        PYTHON = "Python"
        JAVA = "Java"
        R = "R"
        PHP = "PHP"
        CPP = "C++"
        RUBY = "Ruby"
        MATLAB = "MATLAB"

prefixList = [
    "bioconductor-",
    "r-",
    "perl-",
    "python-"
]


def filterPackageList(packages, filters = {}):

    '''
    {toolType: (bool, ['Workbench', 'Desktop application', 'Web application'])}
    '''
    filteredList = []
    for pkg in packages:
        matches = True
        for pkgFilterKey, pkgFilterValues in filters.items():
            if len(pkgFilterValues) == 0:
                if len(pkg[pkgFilterKey]) == 0:
                    continue
                else:
                    matches = False
                    break
            elif not any(pkgFilterValue in pkg[pkgFilterKey] for pkgFilterValue in pkgFilterValues):
                matches = False
                break
        if matches:
            filteredList.append(pkg)
    return filteredList

def getCondaChannelPackages(channel):
        return utils.get_channel_repodata(channel)[0]['packages']

def write_package_list(packageList, csv_name):
    with open(csv_name + ".csv", "w") as file:
        for pkg in packageList:
            file.write(pkg+"\n")


def getBiotoolsPackages():
    page = 1
    packages = []
    while page < 5000:
        r = requests.get(bio_tools_pkg_url+'?page='+str(page))
        if r.status_code != 200:
            print("Error: Got response: " + str(r.status_code))
            break
        
        tools_list = r.json()['list']        
        packages.extend(tools_list)
        print('Number of packages: {}, page = {}'.format(len(packages), page))
        page += 1
    return packages

def compareCondaAndBiotools(conda_packages, biotools_packages):
    result = []
    print("test")
    for biotools_pkg in biotools_packages:
        if biotools_pkg["id"].lower() in conda_packages:
            result.append(biotools_pkg)
    return result

def removePrefix(condaPackages):
    result = []
    for pkg in condaPackages:
        if pkg == "r-base":
            continue
        for prefix in prefixList:
            if pkg.startswith(prefix):
                pkg = re.sub(prefix, "", pkg)
        result.append(pkg)

    return result
'''
TODO: Extract extra information from bioconda packages to get the biotools id
def updateMapping(fileName, bioconda, biotools):
    updatedMapping = []
    with open(fileName, 'r') as mapping:
'''




def generateOverview():
    biotoolsPackages = getBiotoolsPackages()
    filters = {
        Keys.TOOLTYPE.value: [ToolTypes.COMMAND_LINE_TOOL.value, ToolTypes.LIBRARY.value, ToolTypes.SCRIPT.value, ToolTypes.DESKTOP_APPLICATION.value, ToolTypes.SUITE.value]
        }
    filteredList = filterPackageList(biotoolsPackages, filters)
    filteredNamesList = [pkg["id"] for pkg in filteredList]
    bioconda_packages = getCondaChannelPackages('bioconda')
    bioconda_packages = set([pkg['name'] for pkg in bioconda_packages.values()])
    with open('mapping.csv', 'r') as csvfile:
        overlaps = 0
        mapping = csv.reader(csvfile, delimiter=',')
        for row in mapping:
            if row[0] != 'null' and (len(row) == 3 or row[3] != 'NV'):
                overlaps += 1
        print(
        """
        # of packages on bio.tools: {} \n
        # of relevant packages on bio.tools: {} \n
        # of packages on bioconda: {} \n
        # of packages that overlap: {}
        """.format(len(biotoolsPackages), len(filteredNamesList), len(bioconda_packages), overlaps))

    

if __name__=="__main__":
    generateOverview()

