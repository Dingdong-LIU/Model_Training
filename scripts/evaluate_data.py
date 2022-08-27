from load_data import partial_ratio


def substring(string1, string2, fuzz=False):
    if len(string2) < len(string1):
        s = string1
        string1 = string2
        string2 = s
    if string1 in string2:
        return True
    if fuzz:
        pr = partial_ratio(string1, string2)
        if pr > 90:
            return True
    return False

def locate_post(list_of_posts, target_post_content, start_index=0):
    try:
        for i,p in enumerate(list_of_posts):
            if i < start_index:
                continue
            content = p['content']
            if substring(content, target_post_content, fuzz=True):
                return i
    # except ValueError as verr:
    #     raise ValueError(
    #         f"'{string1}'\n\nis not a substring of\n\n'{string2}', with partio_ratio {pr}")
    #     print(f"Substring mismatch,\n{verr}")
    except KeyError as kerr:
        print(f"Key 'content' not found in the post {i}")
    return -1

def create_objects(text_list):
    return [{'content' : text} for text in text_list]

def insert_objects(posts, insert_objs, index, name):
    for insert_obj in insert_objs:
        posts[index][name].append(insert_obj)
    return posts

def pre_process_prediction(text):
    output = text.split('\n')
    output = [x.strip(',. ') for x in output]
    return output
