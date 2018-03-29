import re
import subprocess as sp
import csv
import packages_list_generator as generator
import requests as req
import os
def main():
    bio_url = 'https://bio.tools/api/tool/'
    with open('mapping.csv', 'r') as mapping:
        pkg_reader = csv.reader(mapping, delimiter=',')
        counter = 0
        batch_nr = 1
        sp.call(['git checkout master'], shell=True)
        sp.call(['git checkout -b biotools_annotation_batch_' + str(batch_nr)], shell=True)
        for row in pkg_reader:
            if counter == 10:
                sp.call(['git commit -m \"Added biotools identifiers\"'], shell=True)
                sp.call(['git push origin master'], shell=True)
                break
                batch_nr += 1
                sp.call(['git checkout master'], shell=True)
                sp.call(['git checkout -b biotools_annotation_batch_' + batch_nr], shell=True)
                counter = 0
            if row[1] == 'emboss':
                continue
            if row[0] != 'null' and row[0] != 'Biotools ID':
                print(row[0])
                biotools_meta_data = req.get(bio_url+ row[0]).json()
                doi = None
                publications = biotools_meta_data['publication']
                for publication in publications:
                    if publication['doi'] != None:
                        doi = publication['doi']
                        break
                
                bio_tools_id = biotools_meta_data['id']
                
                directory = '../PycharmProjects/bioconda-recipes/recipes/' + row[1] 
                if os.path.isdir(directory):
                    for subdirectory in os.walk(directory):
                        if os.path.isfile(subdirectory[0] + '/meta.yaml'):
                            with open(subdirectory[0] + '/meta.yaml', 'r') as meta_file:
                                lines = list(meta_file.readlines())
                                lines = add_biotools_id(lines, bio_tools_id, doi)
                            with open('{}/meta.yaml'.format(subdirectory[0]), 'w+') as new:
                                out = ''.join(lines)
                                new.write(out)
                counter += 1
 
                
        

        
        
        
        
        
        
        
    '''
    for line, actual_cran_name in zip(branches.readlines(), actual_cran_name.readlines()):
        try:
            sp.call(['git checkout master'], shell=True)
            sp.call(['git checkout ' + line], shell=True)
            lines = []
            with open('recipes/' + line[0:-1] + '/meta.yaml') as file:
                lines = list(file.readlines())
                #lines = change_maintainers(lines)
                lines = adding_missing_home(lines,actual_cran_name)

            with open('recipes/' + line[0:-1] + '/meta.yaml', 'w') as file:
                out = "".join(lines)
                file.write(out)

            sp.call(["git add recipes/" + line + '/meta.yaml'], shell=True)
            sp.call(["git commit -m \"added home url\""], shell=True)
            sp.call(["git push origin " + line], shell=True)

        except Exception as e:
            print(e)
    '''

def add_biotools_id(lines, tools_id, doi):
    has_extra = False
    extra_line_index = 0
    for line in lines:
        if 'identifiers:' in line:
            print('hello')
            return lines
        if line.startswith('extra:'):
            has_extra = True
        extra_line_index += 1
    if not has_extra:
        lines.append('extra:\n')
        extra_line_index = len(lines)-1
    lines.insert(extra_line_index + 1, '  identifiers:\n')
    lines.insert(extra_line_index + 2, '    - biotools:' + tools_id + '\n')
    if not doi is None:
        lines.insert(extra_line_index + 3, '    - doi:' + doi + '\n')
    return lines
    

def change_maintainers(lines):
    change_1 = [re.sub(r"Johanneskoester", "johanneskoester", line) for line in lines]
    change_2 = [re.sub(r"Bgruening", "bgruening", line) for line in change_1]
    change_3 = [re.sub(r"Daler", "daler", line) for line in change_2]
    return [re.sub(r"Jdblischak", "jdblischak", line) for line in change_3]

def adding_missing_home(lines, actual_cran_name):
    return [re.sub(r"home: (https|http)\n", "home: https://cran.r-project.org/web/packages/" + actual_cran_name[0:-1] + "/index.html\n", line) for line in lines]


if __name__=="__main__":
    main()
