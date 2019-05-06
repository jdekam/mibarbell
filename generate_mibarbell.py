import csv
import os
import math
import shutil
import collections
from jinja2 import FileSystemLoader, Environment
from jinja2 import select_autoescape, TemplateError

def calc_sinclair(total, weight, gender):
    # check wikipedia for what these terms mean
    A_M = 0.751945030 
    A_F = 0.783497476 
    B_M = 175.508
    B_F = 153.655
    
    # calculate sinclair score
    if gender == 'M':
        coefficient = 10 ** (A_M * ((math.log10(weight / B_M) ** 2)))
        return round(total * coefficient, 1)
    if gender == 'F':
        coefficient = 10 ** (A_F * ((math.log10(weight / B_F) ** 2)))
        return round(total * coefficient, 1)

def gen_results():
    # lists used with HTML template
    all_results = []
    females = []
    males = []

    # get all files and sort in descending order
    files = os.listdir(os.getcwd() + '/resources/results')
    files.sort(reverse = True)
    for file_name in files:
        file = open(os.getcwd() + '/resources/results/' + file_name, 'r+')
        data = csv.DictReader(file)
        results = [row for row in data]
        
        meet = (' '.join(file_name.split()[1:])).split('.')[0]

        # calculate total and sinclair per row
        for row in results:
            best_sn = int(max(row['snatch1'], row['snatch2'], row['snatch3']))
            best_cj = int(max(row['cj1'], row['cj2'], row['cj3']))

            # if they bombed one of the lifts, no total and no sinclair
            if best_cj < 0 or best_sn < 0:
                row['total'] = 'n/a'
                row['sinclair'] = 0
            else:
                row['total'] = best_sn + best_cj
                row['sinclair'] = calc_sinclair(int(row['total']), int(row['weight']), row['gender'])

            row['meet'] = meet
            if row['gender'] == 'M':
                males.append(row)
            else:
                females.append(row)

        all_results.append((meet, results))
        file.close()

    # order by sinclair
    males.sort(key = lambda i : i['sinclair'], reverse = True)
    females.sort(key = lambda i : i['sinclair'], reverse = True) 
    
    # generate results page
    try:
        template_env = Environment(loader=FileSystemLoader('templates/jinja'), autoescape=select_autoescape(['html', 'xml']))
        template = template_env.get_template('results.jinja')
        rendered_template = template.render(data = all_results, bestMales = males[:3], bestFemales = females[:3])
    except TemplateError:
        print('Error_Jinja: invalid/unfound Jinja2 templates')
        exit(1)

    # write new file
    new_file = open('mibarbell/results.html', 'w+')
    new_file.write(rendered_template)
    new_file.close()

def gen_roster():
    # open roster file
    file = open(os.getcwd() + '/resources/roster/roster.csv', 'r+')
    data = csv.DictReader(file)
    roster = [row for row in data]
    file.close()

    # generate roster page
    try:
        template_env = Environment(loader=FileSystemLoader('templates/jinja'), autoescape=select_autoescape(['html', 'xml']))
        template = template_env.get_template('roster.jinja')
        rendered_template = template.render(data = roster)
    except TemplateError:
        print('Error_Jinja: invalid/unfound Jinja2 templates')
        exit(1)

    # write new file
    new_file = open('mibarbell/roster.html', 'w+')
    new_file.write(rendered_template)
    new_file.close()

def copy_files():
    # remove old directory
    if os.path.isdir(os.getcwd() + '\\mibarbell\\') == True:
        shutil.rmtree(os.getcwd() + '\\mibarbell\\')
    # copy all files over to new directory
    shutil.copytree(os.getcwd() + '\\templates\\html\\', os.getcwd() + '\\mibarbell\\')
    shutil.copytree(os.getcwd() + '\\resources\\static\\', os.getcwd() + '\\mibarbell\\static\\')

def main():
    copy_files()
    # overwrite results.html and roster.html with correct versions
    gen_results()
    gen_roster()

if __name__ == "__main__":
    main()
