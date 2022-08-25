from difflib import SequenceMatcher
import glob
import os
import xml.etree.ElementTree as ET
import numpy as np

def find_xml_files(root_path='datasets/change-my-view-modes-master/v1.0'):
    """Find all xml files in given folder

    Args:
        root_path (str, optional): Root path. Can search for XML files under sub folders. Defaults to 'datasets/change-my-view-modes-master/v1.0'.

    Returns:
        list: a list of xml file paths
    """
    xml_files = glob.glob(os.path.join(root_path, '*/*.xml'))
    print(f'Find {len(xml_files)} XML files')
    return xml_files


def load_objects(data_file_path, name, return_list_of_string=False, verbose=False):
    """Input a xml file, return a list of claim or premise/claim-content pairs objects. This function will look for 'OP' and 'reply' tag under 'root tag

    Args:
        data_file_path (str): path of the xml file
        name (str): 'claim' or 'premise'
        return_list_of_claims (bool, optional): Whether return a list or a string for each xml file. Concatenation seperate by '\n' is adopted. Defaults to False.
    Returns:
        list: a list of claim/premise objects, with format (original_text, claim/premise)
    """
    assert name in ['claim', 'premise'], f"name should be one of 'claim' or 'premise', should not be {name}"
    assert os.path.exists(data_file_path), f"path {data_file_path} not exist"
    try:
        root = ET.parse(data_file_path)
    except ET.ParseError as err:
        print(f'Error in path {data_file_path} with error "{err}"')
        return []
    # except:
    #     print(f"Unexpected error in path {data_file_path}")
    #     return []
    all_object_string = []
    for post in root.findall('OP') + root.findall('reply'):
        target_objects = post.findall(name)

        # omit OP or reply with no claim or premise
        if len(target_objects) <= 0:
            continue

        # examime if the post is too long. if so, call special handler
        post_content = ET.tostring(
            post, encoding='utf-8', method='text').decode('utf-8').strip()
        if len(post_content.split()) > 200:
            # print("Too long: ", data_file_path + " " + post.tag)
            ## call long post handler
            try:
                output = handle_long_post(post, name)
                if not return_list_of_string:
                    for i, (x, y) in enumerate(output):
                        output[i] = (x, '\n'.join(y))
                all_object_string.extend(output)
            except ValueError as err:
                print(f'Error: {err} in {post.tag} of file:\n{data_file_path}')
            continue

        # get all target(claim/premise) strings
        object_string = []
        for _, c in enumerate(target_objects):
            object_string.append(c.text)

        # format output
        if not return_list_of_string:
            object_string = '\n'.join(object_string)
            if len(object_string.split()) > 100:
                print(f"Too long in {post.tag} (lenth {len(object_string.split())}) of file:\n{data_file_path}")
        all_object_string.append((post_content,object_string))
    if verbose:
        print(f'Get {len(all_object_string)} {name}s')
    return all_object_string


def load_data(base_dir='datasets/change-my-view-modes-master/v1.0', target='claim', **kwargs):

    assert os.path.exists(base_dir), f"Path {base_dir} not exist"
    assert target in [
        'claim', 'premise'], f"name should be one of 'claim' or 'premise', should not be {target}"
    data_file_paths = find_xml_files(base_dir)
    output = [load_objects(d, name=target, **kwargs) for d in data_file_paths]
    output = sum(output, [])
    return output


def partial_ratio(s1, s2):
    """"Return the ratio of the most similar substring
    as a number between 0 and 100."""

    if len(s1) <= len(s2):
        shorter = s1
        longer = s2
    else:
        shorter = s2
        longer = s1

    m = SequenceMatcher(None, shorter, longer, autojunk=False)
    blocks = m.get_matching_blocks()

    # each block represents a sequence of matching characters in a string
    # of the form (idx_1, idx_2, len)
    # the best partial match will block align with at least one of those blocks
    #   e.g. shorter = "abcd", longer = XXXbcdeEEE
    #   block = (1,3,3)
    #   best score === ratio("abcd", "Xbcd")
    scores = []
    for (_, long_start, _) in blocks:
        long_end = long_start + len(shorter)
        long_substr = longer[long_start:long_end]

        m2 = SequenceMatcher(None, shorter, long_substr, autojunk=False)
        r = m2.ratio()
        if r > .995:
            return 100
        else:
            scores.append(r)

    return max(scores) * 100.0

def fuzz_match(list_of_string, target):
    ratios = [partial_ratio(x, target) for x in list_of_string]
    index = np.argmax(ratios)
    if ratios[index] < 90:
        raise ValueError(f'No good matching with score {ratios[index]} with target "{target}" in list of string {list_of_string}')
    return list_of_string[index]

def exact_match(list_of_string, target):
    for s in list_of_string:
        if target in s:
            return s
    return None


def handle_long_post(root, name):
    paragraphs = ET.tostring(root, encoding='utf-8',
                             method='text').decode('utf-8').strip().split('\n\n')
    # length check
    for p in paragraphs:
        if len(p.split()) > 300:
            raise ValueError(f"Paragraph too long with length {len(p.split())}")
    target_objects = root.findall(name)
    output_dict = {p:[] for p in paragraphs}
    for p in target_objects:
        # try:
        #     belonging = fuzz_match(paragraphs, p.text)
        #     output_dict[belonging].append(p.text)
        # except ValueError as err:
        #     print(f'Error {err}', p.text)
        belonging = exact_match(paragraphs, p.text)
        if belonging is None:
            belonging = fuzz_match(paragraphs, p.text)
        output_dict[belonging].append(p.text)
    return [(x,y) for x,y in output_dict.items() if len(y) > 0]



# def load_claims(root, return_list_of_claims=False):
#     """Get claims

#     Args:
#         root (xml.etree.ElementTree): root of the xml file
#         return_list_of_claims (bool, optional): Whether return a list or a string for each xml file. Concatenation seperate by '\n' is adopted. Defaults to False.

#     Returns:
#         list: list of claims
#     """
#     claims_list = load_objects(root, 'claim')
#     if not return_list_of_claims:
#         claims_list = ['\n'.join(x) for x in claims_list]
#     return claims_list

# def load_premises(root, return_list_of_premises=False):
#     """Get premises

#     Args:
#         root (xml.etree.ElementTree): root of the xml file
#         return_list_of_premises (bool, optional): Whether return a list or a string for each xml file. Concatenation seperate by '\n' is adopted. Defaults to False.

#     Returns:
#         list: list of premises
#     """
#     premises_list = load_objects(root, 'premise')
#     if not return_list_of_premises:
#         premises_list = ['\n'.join(x) for x in premises_list]
#     return premises_list
