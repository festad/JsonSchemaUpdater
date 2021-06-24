import json


def _recursive_annihilation_of_dictionary(dictionary):
    for k in dictionary.keys():
        if isinstance(dictionary[k], dict):
            _recursive_annihilation_of_dictionary(dictionary[k])
        elif isinstance(dictionary[k], list):
            for j in dictionary[k]:
                if isinstance(j, dict):
                    _recursive_annihilation_of_dictionary(j)
                else:
                    j = None
        else:
            dictionary[k] = None


def _recursive_cleaning_of_dictionary(dictionary, clean_dictionary={}):
    for k in dictionary.keys():
        if isinstance(dictionary[k], dict):
            clean_dictionary[k] = {}
            _recursive_cleaning_of_dictionary(dictionary[k], clean_dictionary[k])
        elif isinstance(dictionary[k], list):
            clean_dictionary[k] = []
            for j in dictionary[k]:
                if isinstance(j, dict):
                    clean_dictionary[k].append({})
                    _recursive_cleaning_of_dictionary(j, clean_dictionary[k][-1])
        elif dictionary[k] is not None:
            clean_dictionary[k] = dictionary[k]


def _recursive_search_of_key_inside_dictionary(key, dictionary, new_value_of_key=None, list_keys=[]):
    for k in dictionary.keys():
        if isinstance(dictionary[k], dict):
            _recursive_search_of_key_inside_dictionary(key, dictionary[k], new_value_of_key=new_value_of_key,
                                                       list_keys=list_keys)
        elif k == key:
            if new_value_of_key is not None:
                dictionary[key] = new_value_of_key
            list_keys.append(k)


def _list_including_nested_keys_of_dictionary(dictionary, list_keys=[]):
    for k in dictionary.keys():
        list_keys.append(k)
        if isinstance(dictionary[k], dict):
            _list_including_nested_keys_of_dictionary(dictionary[k], list_keys)


def _duplicate_keys_inside_dictionary(dictionary):
    list_keys = []
    _list_including_nested_keys_of_dictionary(dictionary, list_keys)
    return len(list_keys) != len(set(list_keys))


def _recursive_update(old_dictionary, new_dictionary, updated_keys=[]):
    for k in old_dictionary.keys():
        if isinstance(old_dictionary[k], dict):
            _recursive_update(old_dictionary[k], new_dictionary, updated_keys)
        # elif isinstance(old_dictionary[k], list):
        #     for j in old_dictionary[k]:
        #         if isinstance(j, dict):
        #             _recursive_update(j, new_dictionary, updated_keys)
        else:
            _recursive_search_of_key_inside_dictionary(k, new_dictionary, new_value_of_key=old_dictionary[k],
                                                       list_keys=updated_keys)


def elaborate_new_json(old_json, new_schema):
    if _duplicate_keys_inside_dictionary(old_json):
        print('The old json contains duplicate keys')
    if _duplicate_keys_inside_dictionary(new_schema):
        print('The new schema contains duplicate keys')

    _recursive_annihilation_of_dictionary(new_schema)
    # print(f'Annihilated schema: \n{json.dumps(new_schema, indent=4)}\n')

    updated_keys = []
    _recursive_update(old_json, new_schema, updated_keys)
    print(f'Updated keys: {updated_keys}')

    clean_schema = {}
    _recursive_cleaning_of_dictionary(new_schema, clean_schema)
    return clean_schema


def annihilate(dictionary):
    for key in dictionary.keys():
        dictionary[key] = annihilate_element(dictionary[key])
    return dictionary


def annihilate_element(element):
    if isinstance(element, dict):
        for key in element.keys():
            element[key] = annihilate_element(element[key])
        return element
    elif isinstance(element, list):
        for k,el in enumerate(element):
            element[k] = annihilate_element(el)
        return element
    else:
        element = None
        return element


def test_annihilation():
    d = {'id':'a07', 'dict':{'inn':'inner', 'inn_list':[{'num':3}, {'inn_dict':{'x':'xyy'}}, [1,{'a':2},3]]}}
    print(json.dumps(d, indent=4))
    annihilate_element(d)
    print(json.dumps(d, indent=4))


if __name__ == '__main__':
    old_schema = {'identity':
                      {'name': 'string', 'age': 'number'},
                  'hobbies': 'list'
                  }
    print(f'Old schema: \n{json.dumps(old_schema, indent=4)}\n')
    old_json = {'identity':
                    {'name': 'Denis', 'age': 23},
                'hobbies': ['chess', 'go-karting']
                }
    print(f'Old json: \n{json.dumps(old_json, indent=4)}\n')

    new_schema_working = {'table':
                              {'rows':
                                   {'person':
                                        {'name': 'string', 'age': 'number', 'hobbies': 'list'}
                                    }
                               }
                          }
    print(f'New schema working: \n{json.dumps(new_schema_working, indent=4)}\n')
    new_schema_working = elaborate_new_json(old_json, new_schema_working)
    print(f'New json adapted to the new schema:\n{json.dumps(new_schema_working, indent=4)}\n')

    new_schema_not_working = {'table':
                                  {'identity': 'string', 'rows':
                                      {'identity':
                                           {'name': 'string', 'serial_number': 'string'}
                                       },
                                   'age': 'number', 'hobbies': 'string'
                                   },
                              'identity': 'string'
                              }
    print(f'New schema not working: \n{json.dumps(new_schema_not_working, indent=4)}\n')
    new_schema_not_working = elaborate_new_json(old_json, new_schema_not_working)
    print(f'New json adapted to the new schema not working:\n{json.dumps(new_schema_not_working, indent=4)}\n')

    print("Notice how with the old json had an 'identity' field with subfields 'name' and 'age':\n"
          "With the first new schema no problem arose because there was no other 'identity' field,\n"
          "With the second schema the new 'identity' field is set to null because"
          "the recursion is written in such a way that the subfields have the priority,\n"
          "that is, 'name' and 'age'.\n")
