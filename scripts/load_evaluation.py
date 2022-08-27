import os
import json
from glob import glob
from load_data import fuzz_match_within_list, exact_match_within_list


def load_evaluation(base_dir, object_name):
    # input check
    assert object_name in [
        'claim', 'premise'], f'object_name should be one of "claim" and "premise", but your input is {object_name}'

    json_files = find_json_files(base_dir=base_dir)
    raw_data = get_paragraphs_with_objects(json_files, object_name)
    data = []
    for d in raw_data:
        # term = map_paragraph_object(d, return_list_of_string=False)
        term = truncate_paras(d, return_list_of_string=False)
        data.extend(term)
    return data

def get_paragraphs_with_objects(json_files, object_name):
    """Get all paragraphs and claim/premises from all posts in a json data file

    Args:
        json_files (path or str): path to json data file
        object_name (str): should be one in "claim" and "premise". The term to extract.

    Returns:
        list: a list of tuples. Tuples have format (list_of_paras, list_of_objects)
    """
    assert object_name in ['claim', 'premise'], f'object_name should be one of "claim" and "premise", but your input is {object_name}'
    for fl in json_files:
        output = []
        with open(fl, 'r') as fp:
            data_file = json.load(fp)
        for sec in data_file['answers']:
            paras = sec['paragraphs']
            object_list = [x['content'] for x in sec[object_name]]
            output.append((paras, object_list))
    return output


def find_json_files(base_dir='datasets/auto-driving'):
    """Find json files in base direcotry

    Args:
        base_dir (str, optional): base directory of data files. Defaults to 'datasets/auto-driving'.

    Returns:
        list: list of paths of json files
    """
    x = glob(os.path.join(base_dir, '*.json'))
    assert len(x) > 0, "No such json file found in the directory"
    return x


def map_paragraph_object(p_o_pair, return_list_of_string=False):
    """Input a p_o_pair, i.e., a tuple of (<list_of_paras, list_of_claims/premises>), return a list of objects in (text, summary) format. This function works like finding paragraphs for each claim/premise, and therefore not recommended

    Args:
        p_o_pair (tuple): a tuple of (<list_of_paras, list_of_claims/premises>)
        return_list_of_string (bool, optional): Whether summary should be a list of claim/premise, or a whole sentence. Defaults to False.

    Returns:
        list: a list of tuples of format (text, summary)
    """
    paras, text = p_o_pair[0], p_o_pair[1]
    para_collect = {p:[] for p in paras}
    for t in text:
        destiny = exact_match_within_list(paras, t)
        if destiny is None:
            destiny = fuzz_match_within_list(paras, t)
        para_collect[destiny].append(t)
    output = []
    text = ""
    for p in paras:
        if len(para_collect[p]) == 0:
            text = text + '\n' + p
        else:
            text = text + '\n' + p
            text = text.strip()
            output.append((text, para_collect[p]))
            text = ""
    if not return_list_of_string:
        output = [(x,"\n".join(y)) for (x,y) in output]
    return output

def truncate_paras(p_o_pair, return_list_of_string=False):
    """Input a p_o_pair, i.e., a tuple of (<list_of_paras, list_of_claims/premises>), return a list of objects in (text, summary) format. This function will first concate paragraphs to sentences with length < 300, then find corresponding claim/premise. This is recommended.

    Args:
        p_o_pair (_type_): _description_
        return_list_of_string (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    paras, text = p_o_pair[0], p_o_pair[1]
    output = []
    term = ""
    for p in paras:
        new_term = term + '\n' + p
        if len(new_term.split()) > 300:
            # para too long, collect claims
            claims = []
            for t in text:
                if t in new_term:
                    claims.append(t)
            if len(claims) <= 0:
                continue
            if not return_list_of_string:
                claims = "\n".join(claims)
            output.append((term.strip(), claims))
            # update term
            term = p
        else:
            term = new_term
    # handle tailing objects
    if len(term) > 0:
        claims = []
        for t in text:
            if t in new_term:
                claims.append(t)
        if len(claims) <= 0:
            return output
        if not return_list_of_string:
            claims = "\n".join(claims)
        output.append((term.strip(), claims))
    return output
