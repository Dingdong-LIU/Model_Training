from load_data import partial_ratio


def substring(string1, string2):
    if len(string2) > len(string1):
        s = string1
        string1 = string2
        string2 = s
    if string1 in string2:
        return True
    pr = partial_ratio(string1, string2)
    if pr > 90:
        return True
    else:
        raise ValueError(f"'{string1}' is not a substring of '{string2}', with partio_ratio {pr}")

def locate_post(list_of_posts, target_post_content):
    try:
        for i,p in enumerate(list_of_posts):
            content = p['content']
            if substring(content, target_post_content):
                return i
    except ValueError as verr:
        print(f"Substring mismatch, {verr}")
    except KeyError as kerr:
        print(f"Key 'content' not found in the post {i}")
    return -1

def create_object(text, name):
    return {name : text}

def insert_object(posts, insert_obj, index, name):
    posts[index][name] = insert_obj
    return posts

def pre_process_prediction(text):
    output = text.split('\n')
    output = [x.strip(',. ') for x in output]
    return output