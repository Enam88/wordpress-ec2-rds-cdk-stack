# lib/utils.py

def replace_all_substrings(words_array, text):
    for word_dict in words_array:
        for key, value in word_dict.items():
            text = text.replace(key, value)
    return text
