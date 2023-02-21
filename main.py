import csv
import re

polygon = ['pyramid', 'block', 'cylinder']


class Link:
    def __init__(self, link):
        tmp_diff = link.split(',')
        property_value = tmp_diff[1]
        property_value = property_value[:-1]

        self.property_name = tmp_diff[0]
        self.property_value = property_value


def load_examples():
    with open("example.csv", "r") as file:
        reader = csv.reader(file, delimiter=';')
        return list(reader)


def save_model(model):
    with open('model.csv', 'w') as file:
        write = (csv.writer(file))
        write.writerow(model)
        print('THE MODEL HAS BEEN SUCCESSFULLY SAVED TO THE CSV FILE')


def find_positive_example(examples):
    for example in examples:
        if 'true' in example:
            model = example
            model.pop(len(model) - 1)
            examples.remove(example)
            return model


def specialization(model, example):
    diff1, diff2 = compare_models(model, example)
    if diff2:
        print('REQUIRED LINK')
        for link in diff2:
            model = list(map(lambda x: x.replace(link, 'must-be-' + link), model))
    elif diff1:
        print('FORBIDDEN LINK')
        for link in diff1:
            model.append('must-not-be-' + link)
    return model


def find_differences(model, example):
    tmp_model = temp_model(model)

    diff_values_links = set(tmp_model) - set(example) - set(
        [link for link in tmp_model if link.startswith('must-not-be-')])

    return diff_values_links


def temp_model(model):
    tmp_model = []
    for link in model:
        if link.startswith('must-be-'):
            tmp_model.append(link[len('must-be-'):])
        else:
            tmp_model.append(link)
    return tmp_model


def compare_models(model, example):
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


def main():
    examples = load_examples()                                      # Nacitani prikladu ze souboru
    model = find_positive_example(examples)                         # Nalezeni pocatecniho modelu(hypotezy) z prikladu

    for example in examples:
        if 'false' in example:                                      # **NEGATIVNI PRIKLAD**
            example = example[:-1]
            model = specialization(model, example)                  # Specializace
            print(model)

        elif 'true' in example:                                     # **POZITIVNI PRIKLAD**
            example = example[:-1]
            diff_values_links = find_differences(model, example)    # Seznam linku, ktere jsou rozdilne s prikladem

            for diff in diff_values_links:                          # Prochazet rozdilne linky
                l1 = Link(diff)

                miss = False                                        # Kontrola jestli nechybi v prikladu link z modelu
                for link in example:
                    if l1.property_name in link:
                        miss = True
                        break

                if not miss:                                        # Drop link, odstranit nedulezity link z modelu
                    print('DROP LINK')
                    model.remove(diff)
                    print(model)

                elif re.match('^\d+-\d+$', l1.property_value):      # Kontrola linku na ciselny interval
                    print('INTERVAL LINK')
                    values = l1.property_value.split('-')

                    for link in example:
                        if l1.property_name in link:
                            e_property = link.split(',')
                            e_property_value = e_property[1]
                            e_property_value = e_property_value[:-1]

                            if values[1] < e_property_value:
                                model = list(map(lambda x: x.replace(diff,
                                                                     'must-be-' + l1.property_name + ',' + values[
                                                                         0] + '-' + e_property_value + ')'), model))
                            elif values[0] > e_property_value:
                                model = list(map(lambda x: x.replace(diff,
                                                                     'must-be-' + l1.property_name + ',' + e_property_value
                                                                     + '-' + values[1] + ')'), model))
                            print(model)
                            break

                elif l1.property_value.isnumeric():
                    print('NUMBER LINK')
                    for link in example:
                        if l1.property_name in link:
                            e_property = link.split(',')
                            e_property_value = e_property[1]
                            e_property_value = e_property_value[:-1]

                            if l1.property_value < e_property_value:
                                model = list(map(lambda x: x.replace(diff,
                                                                     'must-be-' + l1.property_name + ',' + l1.property_value
                                                                     + '-' + e_property_value + ')'), model))
                            else:
                                model = list(map(lambda x: x.replace(diff,
                                                                     'must-be-' + l1.property_name + ',' + e_property_value
                                                                     + '-' + l1.property_value + ')'), model))
                            print(model)
                            break

                elif miss:
                    print('GENERALIZE WITH TREE OR ENLARGE-LIST')
                    e_property_value = str()
                    for link in example:
                        if l1.property_name in link:
                            e_property = link.split(',')
                            e_property_value = e_property[1]
                            e_property_value = e_property_value[:-1]
                            break

                    if e_property_value in polygon and l1.property_value != 'polygon' and l1.property_value in polygon:
                        model = list(
                            map(lambda x: x.replace(diff, 'must-be-' + l1.property_name + ',' + 'polygon' + ')'), model))

                    elif (l1.property_value in polygon or l1.property_value == 'polygon') and e_property_value not in polygon:
                        model = list(map(lambda x: x.replace(diff,
                                                             'must-be-' + l1.property_name + ',' + l1.property_value + ' ∪ '
                                                             + e_property_value + ')'), model))
                    print(model)

    return model


if __name__ == '__main__':
    model1 = main()
    print('A GENERAL MODEL WAS FOUND!')
    save_model(model1)
