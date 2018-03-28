import re
import subprocess as sp

def main():
    with open('branches.txt', 'r') as branches, open('actual_cran_package_names.txt','r') as actual_cran_name:
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

def change_maintainers(lines):
    change_1 = [re.sub(r"Johanneskoester", "johanneskoester", line) for line in lines]
    change_2 = [re.sub(r"Bgruening", "bgruening", line) for line in change_1]
    change_3 = [re.sub(r"Daler", "daler", line) for line in change_2]
    return [re.sub(r"Jdblischak", "jdblischak", line) for line in change_3]

def adding_missing_home(lines, actual_cran_name):
    return [re.sub(r"home: (https|http)\n", "home: https://cran.r-project.org/web/packages/" + actual_cran_name[0:-1] + "/index.html\n", line) for line in lines]


if __name__=="__main__":
    main()
