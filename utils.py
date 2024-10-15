import re

def extract_prompts(input_string):
    return re.findall(r'"(.*?)"', input_string)
