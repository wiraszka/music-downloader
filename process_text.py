import re


def center_text(longer, shorter, amount, order):
    half = int(round(amount / 1.5))
    shorter = ' '*half + shorter
    if order:
        centered = longer + '\n' + shorter
    else:
        centered = shorter + '\n' + longer
    return centered


def remove_extra_info(split_text):
    mod_text = []
    for line in split_text:
        if len(line) > 68:  # 69 characters fit into display space
            if '(' in line:
                # Remove all characters between () and []
                line = re.sub("[\(\[].*?[\)\]]", "", line)
        mod_text.append(line)
    #print(mod_text)
    return mod_text


def modify_text(display_text):
    split_text = display_text.split('\n')
    split_text = remove_extra_info(split_text)
    len_line1 = len(split_text[0])
    len_line2 = len(split_text[1])
    amount = abs(len_line1 - len_line2)
    if len_line1 > len_line2:
        order = True
        centered = center_text(split_text[0], split_text[1], amount, order)
    elif len_line2 > len_line1:
        order = False
        centered = center_text(split_text[1], split_text[0], amount, order)
    elif len_line1 == len_line2:
        centered = display_text
    return centered
