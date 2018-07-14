import yaml
import requests
import sys
import hashlib
import os
import subprocess as sp


bio_tools_pkg_url = 'https://www.bio.tools/api/tool'


def getAttributes(metaData):
    name = metaData['name']
    version = metaData['version'] if metaData['version'] is not None else 1.0
    url = metaData['download'][0] if len(metaData['download']) > 0 else ""
    fn = url.split('/')[-1] if url != "" else ""
    sha = ""
    home = metaData['homepage']
    summary = metaData['description']
    biotool_id = metaData['id']
    doi = ""
    for pub in metaData['publication']:
        if pub['doi'] is not None:
            doi = pub['doi']
            break

    return [name.lower(), version, fn, url, sha, home, summary, biotool_id, doi, name]
            
    

if __name__ == '__main__':

    r = requests.get(bio_tools_pkg_url+'/' + sys.argv[1])
    if r.status_code != 200:
        print('Package does not exist')
        sys.exit()

    sp.call(['git checkout master'], shell=True)
    sp.call(['git checkout -b' + sys.argv[1]], shell=True)

    document = """package:
    name: {0}
    version: {1}  

build:
    number: 0

source:
    url: {3}
    sha256: {4}

requirements:
    build:
        - {{ compile('c') }}

test:
    commands:
        - {9} -h

about:
    home: {5}
    license: file
    license_file: COPYING
    summary: {6}
extra:
    identifiers:
        - biotools:{7}
        - doi:{8}
"""

    document = document.format(*getAttributes(r.json()))
    if not os.path.exists("recipes/" + sys.argv[1].lower()):
        os.makedirs("recipes/" + sys.argv[1].lower())
    
    with open("recipes/"+sys.argv[1].lower() + "/meta.yaml", 'w') as yaml_file:
        yaml_file.write(document)