import csv
import random
import re
import os.path
import xml.etree.cElementTree as ET


class Link:
    def __init__(self, link):
        self.link = link

        tmp_diff = link.split(',')
        property_value = tmp_diff[1]
        property_value = property_value[:-1]

        self.property_name = tmp_diff[0]
        self.property_value = property_value


class Agent:
    def __init__(self):
        self.model = []
        self.polygon = ['pyramid', 'block', 'cylinder']
        self.exclude_link_dict = {}
        self.examples = []

    # load examples from csv file and exclude links from xml
    def load_examples(self):
        tree = ET.parse('exclude_links.xml')
        root = tree.getroot()
        for child in root:
            values = []
            for e in child:
                values.append(e.text)
            self.exclude_link_dict[child.tag] = values

        with open("example.csv", "r") as file:
            reader = csv.reader(file, delimiter=',')
            self.examples = list(reader)

    # save model into csv
    def save_model(self):
        with open('model.csv', 'w') as file:
            write = csv.writer(file, delimiter=',')
            write.writerow(self.model)
            print('The model has been successfully saved to the model.csv file\n')

    # load model from model.csv
    def load_model(self):
        with open('model.csv') as f:
            reader = csv.reader(f, delimiter=',')
            tmp = list(reader)
            self.model = tmp[0]

    # find first positive example, set as model
    def find_first_positive_example(self):
        for example in self.examples:
            if 'true' in example:
                self.model = example
                self.model.pop(len(self.model) - 1)
                self.examples.remove(example)

                print('First positive example found:')
                print(self.model)
                print("\n")
                break

    # return differences between model and example
    # d1 contains links which miss in model
    # d2 contains links which miss in example
    def compare_model_example(self, example):
        tmp_model = []

        for link in self.model:
            if link.startswith('must-be-'):
                tmp_model.append(link[len('must-be-'):])
            elif link.startswith('must-not-be-'):
                tmp_model.append(link[len('must-not-be-'):])
            else:
                tmp_model.append(link)

        d1 = [link for link in example if link not in tmp_model and 'color' not in link and 'shape' not in link]

        d2 = [link for link in self.model if link not in example]
        d2 = [link for link in d2 if
              'must-be' not in link and 'must-not-be' not in link and 'color' not in link and 'shape' not in link]

        return d1, d2

    # compare models, make required or forbidden link
    def specialization(self, example):
        # diff1 and diff2 differences between both model and example, what is missing in one and other
        diff1, diff2 = self.compare_model_example(example)
        if diff2:
            print('Required link:')
            for link in diff2:
                self.model = list(map(lambda x: x.replace(link, 'must-be-' + link), self.model))
        elif diff1:
            print('Forbidden link:')
            for link in diff1:
                self.model.append('must-not-be-' + link)

    # create number interval link
    def make_interval(self, l1, example):
        for link in example:
            if l1.property_name in link:
                e_property_value = link_get_value(link)

                if l1.property_value < e_property_value:  # Interval settings up, according to the values
                    self.model = list(
                        map(lambda x: x.replace(l1.link, 'must-be-' + l1.property_name + ',' + l1.property_value
                                                + '-' + e_property_value + ')'), self.model))
                elif l1.property_value > e_property_value:
                    self.model = list(map(lambda x: x.replace(l1.link, 'must-be-' + l1.property_name +
                                                              ',' + e_property_value
                                                               + '-' + l1.property_value + ')'), self.model))
                break

    # change values in interval link
    def edit_interval(self, l1, example):
        values = l1.property_value.split('-')

        for link in example:
            if l1.property_name in link:  # If the property is in the example link
                e_property_value = link_get_value(link)  # Get value from link

                if values[1] < e_property_value:
                    # Compare the values from the values[0] and values[1] interval of the model and adjust the new
                    # interval
                    self.model = list(map(lambda x: x.replace(l1.link,
                        'must-be-' + l1.property_name + ',' + values[0] + '-' + e_property_value + ')'), self.model))
                elif values[0] > e_property_value:
                    self.model = list(map(lambda x: x.replace(l1.link, 'must-be-' + l1.property_name + ',' +
                                                               e_property_value + '-' + values[1] + ')'), self.model))
                print(self.model)
                break

    # test created model with random example
    def test_model(self):
        example = random.choice(self.examples)
        self.examples.remove(example)

        example_result = example[-1]
        example = example[:-1]

        print('Model: ')
        print(self.model)

        print('Random test example:')
        print(example)
        print('************************************************************')
        print('Example should be: ' + example_result)

        model2 = self.model.copy()

        for m in model2:
            if m.startswith('must-not-be-'):
                if m[len('must-not-be-'):] in example:
                    return False
                else:
                    model2.remove(m)

        for m in self.model:
            l1 = Link(m)
            l1.property_name = l1.property_name[len('must-be-'):]
            for e in example:
                if e in l1.link:
                    model2.remove(l1.link)
                    break
                elif l1.property_name in e:
                    ex = Link(e)
                    if '∪' in l1.property_value:
                        values = l1.property_value.split('∪')
                        if values[0] == ex.property_value or values[1] == ex.property_value:
                            model2.remove(l1.link)
                            break
                    elif 'polygon' in l1.property_value:
                        if ex.property_value in agent.polygon:
                            model2.remove(l1.link)
                            break
                    elif ex.property_value.isnumeric():
                        values = l1.property_value.split('-')
                        if values[0] <= ex.property_value <= values[1]:
                            model2.remove(l1.link)
                            break

        if not model2:
            return True
        else:
            return False


agent = Agent()


# function removes "must-be-" prefix before links name and return edited copy of model
def temp_model():
    tmp_model = []
    for link in agent.model:
        if link.startswith('must-be-'):
            tmp_model.append(link[len('must-be-'):])
        else:
            tmp_model.append(link)
    return tmp_model


# find differences between model and example
def find_differences(example):
    tmp_model = temp_model()

    diff_values_links = set(tmp_model) - set(example) - set(
        [link for link in tmp_model if link.startswith('must-not-be-')])

    return diff_values_links


# find exclude values between model and example link return True or False
def find_exclude_values(link, example_link_value):
    for ex in agent.exclude_link_dict:
        ex_split = ex.split('-')
        if ex_split[0] in link.property_name and ex_split[1] in link.property_name:
            if link.property_value in agent.exclude_link_dict[ex] and example_link_value in agent.exclude_link_dict[ex]:
                return True

    return False


# get value from link
def link_get_value(link):
    link_split = link.split(',')
    link_value = link_split[1]
    link_value = link_value[:-1]

    return link_value


# check if link is in example
def check_miss_link(l1, example):
    for link in example:
        if l1.property_name in link:
            return False

    return True


# main, loop through all training examples, performing operations to modify the model
def main():
    global agent

    agent.load_examples()  # Loading examples from a file
    agent.find_first_positive_example()  # Finding the initial model from the examples

    for example in agent.examples:
        if 'false' in example:  # Negative example
            example = example[:-1]
            agent.specialization(example)  # Specialization
            print(agent.model)
            print('\n')

        elif 'true' in example:  # Positive example
            example = example[:-1]
            diff_values_links = find_differences(example)  # List of links that are different with current example

            for diff in diff_values_links:  # Browse different links
                l1 = Link(diff)

                miss = check_miss_link(l1, example)  # Check if there is a missing link in the example,which is in model

                if miss:  # Drop link, Remove unnecessary link from the model
                    print('Drop link:')
                    agent.model.remove(diff)

                elif re.match('^\d+-\d+$', l1.property_value):  # Checking the link for the number interval
                    print('Interval link')
                    agent.edit_interval(l1, example)

                elif l1.property_value.isnumeric():  # If the model link contains a numeric value, make an interval
                    print('Number link:')
                    agent.make_interval(l1, example)

                elif not miss:
                    print('Generalize with tree, enlarge-list or remove:')
                    e_property_value = str()
                    for link in example:
                        if l1.property_name in link:
                            e_property_value = link_get_value(link)
                            break

                    # If the values of the model and the example are in a polygon, Generalize to a polygon
                    if e_property_value in agent.polygon and l1.property_value != 'polygon':
                        if l1.property_value in agent.polygon:
                            agent.model = list(
                                map(lambda x: x.replace(diff, 'must-be-' + l1.property_name + ',' + 'polygon' + ')'),
                                    agent.model))

                    # IF they are not in a polygon, add a disjunction
                    elif (
                            l1.property_value in agent.polygon or l1.property_value == 'polygon') and e_property_value not in agent.polygon:
                        agent.model = list(map(lambda x: x.replace(diff,
                                                             'must-be-' + l1.property_name + ',' + l1.property_value + ' ∪ '
                                                             + e_property_value + ')'), agent.model))

                    elif find_exclude_values(l1, e_property_value):  # If the values in links are excluded
                        agent.model.remove(l1.link)

                print(agent.model)
                print('\n')


if __name__ == '__main__':
    if os.path.isfile('model.csv'):
        print('Model is already created')
        agent.load_model()
    else:
        main()
        print('A model was found!')
        agent.save_model()

    # load data again for testing model
    agent.load_examples()
    # Testing the model to see if it identifies a random example as an arch or not
    while agent.examples:
        print(f"The agent identified the example as: {agent.test_model()}")
        print('************************************************************\n\n')

