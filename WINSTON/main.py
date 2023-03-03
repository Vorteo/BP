import csv
import re
import os.path
import xml.etree.cElementTree as ET

polygon = ['pyramid', 'block', 'cylinder']

generalization_tree = {'polygon-pillar': ['block', 'cylinder', 'pyramid', 'cube'],
                       'polygon-roof': ['pyramid', 'block', 'cube', 'cylinder']}

exclude_link_dict = {}

model = []


class Link:
    def __init__(self, link):
        self.link = link

        tmp_diff = link.split(',')
        property_value = tmp_diff[1]
        property_value = property_value[:-1]

        self.property_name = tmp_diff[0]
        self.property_value = property_value


def load_examples():
    tree = ET.parse('exclude_links.xml')
    root = tree.getroot()

    for child in root:
        values = []
        for e in child:
            values.append(e.text)
        exclude_link_dict[child.tag] = values

    with open("example.csv", "r") as file:
        reader = csv.reader(file, delimiter=';')
        return list(reader)


def save_model():
    with open('model.csv', 'w') as file:
        write = (csv.writer(file))
        write.writerow(model)
        print('THE MODEL HAS BEEN SUCCESSFULLY SAVED TO THE CSV FILE')


def find_positive_example(examples):
    global model

    for example in examples:
        if 'true' in example:
            model = example
            model.pop(len(model) - 1)
            examples.remove(example)

            print('A POSITIVE EXAMPLE WAS FOUND:')
            print(model)
            print("\n")
            return model


def specialization(example):
    global model

    diff1, diff2 = compare_models(example)
    if diff2:
        print('REQUIRED LINK:')
        for link in diff2:
            model = list(map(lambda x: x.replace(link, 'must-be-' + link), model))
    elif diff1:
        print('FORBIDDEN LINK:')
        for link in diff1:
            model.append('must-not-be-' + link)
    return model


def find_differences(example):
    tmp_model = temp_model()

    diff_values_links = set(tmp_model) - set(example) - set(
        [link for link in tmp_model if link.startswith('must-not-be-')])

    return diff_values_links


def temp_model():
    tmp_model = []
    for link in model:
        if link.startswith('must-be-'):
            tmp_model.append(link[len('must-be-'):])
        else:
            tmp_model.append(link)
    return tmp_model


def compare_models(example):
    tmp_model = []

    for link in model:
        if link.startswith('must-be-'):
            tmp_model.append(link[len('must-be-'):])
        elif link.startswith('must-not-be-'):
            tmp_model.append(link[len('must-not-be-'):])
        else:
            tmp_model.append(link)

    d1 = [link for link in example if link not in tmp_model and 'color' not in link and 'shape' not in link]

    d2 = [link for link in model if link not in example]
    d2 = [link for link in d2 if
          'must-be' not in link and 'must-not-be' not in link and 'color' not in link and 'shape' not in link]

    return d1, d2


def exclude_values(link, example_link_value):

    for ex in exclude_link_dict:
        ex_split = ex.split('-')
        if ex_split[0] in link.property_name and ex_split[1] in link.property_name:
            if link.property_value in exclude_link_dict[ex] and example_link_value in exclude_link_dict[ex]:
                return True

    return False


def link_get_value(link):
    link_split = link.split(',')
    link_value = link_split[1]
    link_value = link_value[:-1]

    return link_value


def check_miss_link(l1, example):
    for link in example:
        if l1.property_name in link:
            return False

    return True


def make_interval(l1, example):
    global model

    for link in example:
        if l1.property_name in link:
            e_property_value = link_get_value(link)

            if l1.property_value < e_property_value:  
                model = list(map(lambda x: x.replace(l1.link, 'must-be-' + l1.property_name + ',' + l1.property_value
                                                     + '-' + e_property_value + ')'), model))
            else:
                model = list(map(lambda x: x.replace(l1.link,
                                                     'must-be-' + l1.property_name + ',' + e_property_value
                                                     + '-' + l1.property_value + ')'), model))
            break


def edit_interval(l1, example):
    global model

    values = l1.property_value.split('-')

    for link in example:
        if l1.property_name in link:  
            e_property_value = link_get_value(link)  

            if values[1] < e_property_value:  
                model = list(map(lambda x: x.replace(l1.link,
                                                     'must-be-' + l1.property_name + ',' + values[
                                                         0] + '-' + e_property_value + ')'), model))
            elif values[0] > e_property_value:
                model = list(map(lambda x: x.replace(l1.link, 'must-be-' + l1.property_name + ',' +
                                                     e_property_value + '-' + values[1] + ')'), model))
            print(model)
            break


def main():
    global model

    examples = load_examples()                                      
    model = find_positive_example(examples)                          

    for example in examples:
        if 'false' in example:                                     
            example = example[:-1]
            model = specialization(example)                   
            print(model)
            print('\n')

        elif 'true' in example:                                     
            example = example[:-1]
            diff_values_links = find_differences(example)     

            for diff in diff_values_links:                           
                l1 = Link(diff)

                miss = check_miss_link(l1, example)         

                if miss:                                        
                    print('DROP LINK:')
                    model.remove(diff)

                elif re.match('^\d+-\d+$', l1.property_value):     
                    print('INTERVAL LINK:')
                    edit_interval(l1, example)

                elif l1.property_value.isnumeric():        
                    print('NUMBER LINK:')
                    make_interval(l1, example)

                elif not miss:
                    print('GENERALIZE WITH TREE, ENLARGE-LIST OR REMOVE:')
                    e_property_value = str()
                    for link in example:
                        if l1.property_name in link:
                            e_property_value = link_get_value(link)
                            break

                    if e_property_value in polygon and l1.property_value != 'polygon' and l1.property_value in polygon:   
                        model = list(
                            map(lambda x: x.replace(diff, 'must-be-' + l1.property_name + ',' + 'polygon' + ')'), model))

                    elif (l1.property_value in polygon or l1.property_value == 'polygon') and e_property_value not in polygon:     
                        model = list(map(lambda x: x.replace(diff,
                                                             'must-be-' + l1.property_name + ',' + l1.property_value + ' ∪ '
                                                             + e_property_value + ')'), model))

                    elif exclude_values(l1, e_property_value):         
                        model.remove(l1.link)

                print(model)
                print('\n')


if __name__ == '__main__':
    if os.path.isfile('model.csv'):
        print('MODEL IS ALREADY CREATED')
    else:
        main()
        print('A GENERAL MODEL WAS FOUND!')
        save_model()
