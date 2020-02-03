import re
import pandas as pd
from nltk.tag import pos_tag
import re
import enchant
d = enchant.Dict("en_US")

def make_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def parser(text, first_names=False):
    email_rgx = r'(?:\.?)([\w\-_+#~!$&\'\.]+(?<!\.)(@|[ ]?\(?[ ]?(at|AT)[ ]?\)?[ ]?)(?<!\.)[\w]+[\w\-\.]*\.[a-zA-Z-]{2,3})(?:[^\w])'
    matches = re.findall(email_rgx, text)
    emails = list(map(lambda x: x[0], matches))
    if first_names:
        recipients = re.findall(r'(?:Mr\.|Mrs\.|Ms\.) [a-zA-Z]+[ ][a-zA-Z]+', text)
    else:
        recipients = re.findall(r'(?:Mr\.|Mrs\.|Ms\.) [a-zA-Z]+', text)
    more_recipients = re.findall(r'[a-zA-Z]+[,][ ][a-zA-Z]+', text)
    recipients = recipients + list(map(lambda x: x.split(", ")[1] + " " + x.split(", ")[0], more_recipients))
    recipients = make_unique(recipients)
    return pd.DataFrame(list(zip(recipients, emails)))

def emails_only(text):
    email_rgx = r'[a-zA-Z]+@[a-zA-Z.]+'
    email_rgx = r'(?:\.?)([\w\-_+#~!$&\'\.]+(?<!\.)(@|[ ]?\(?[ ]?(at|AT)[ ]?\)?[ ]?)(?<!\.)[\w]+[\w\-\.]*\.[a-zA-Z-]{2,3})(?:[^\w])'
    matches = re.findall(email_rgx, text)
    emails = list(map(lambda x: x[0], matches))
    return make_unique(emails)

def names_only(text, first_names=False):
    if first_names:
        recipients = re.findall(r'(?:Mr\.|Mrs\.|Ms\.) [a-zA-Z]+[ ][a-zA-Z]+', text)
    else:
        recipients = re.findall(r'(?:Mr\.|Mrs\.|Ms\.) [a-zA-Z]+', text)
    more_recipients = re.findall(r'[a-zA-Z]+[,][ ][a-zA-Z]+', text)
    recipients = recipients + list(map(lambda x: x.split(", ")[1] + " " + x.split(", ")[0], more_recipients))
    recipients = make_unique(recipients)
    return recipients

def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))

def valid_name(string):
    return ("/" not in string) and (not hasNumbers(string))

def get_names(fname):
    text = open(fname, "r").read().replace("\t", " a ").replace("\n", " a ").replace("  ", " a ")

    tagged_text = pos_tag(text.split())
    prev = False
    prev_word = ""
    multi_prev = False
    names = []


    for word in tagged_text:
        if word[1] in set(["NNP", "NN"]) and valid_name(word[0]):
            if not prev:
                if (not d.check(word[0].lower())):
                    prev = True
                    prev_word = word[0]
                else:
                    prev = False
            else:
                if (not d.check(word[0].lower())):
                    prev_word = prev_word + " " + word[0]
                    multi_prev = True
                elif not multi_prev:
                    names.append(prev_word + " " + word[0])
                    prev = False
                    multi_prev = False
        else:
            prev = False
            if multi_prev:
                names.append(prev_word)
                multi_prev = False
    if multi_prev:
        names.append(prev_word)

    seen_names = set()
    unique_names = []
    for name in names:
        if name not in seen_names:
            unique_names.append(name)
        seen_names.add(name)

    return unique_names

def match(names, emails):
    names2 = []
    for email in emails:
        for name in names:
            if name.split()[1].lower() in email:
                names2.append(name)
                break
        else:
            names2.append("")
    return pd.DataFrame(list(zip(names2, emails)))

if __name__ == "__main__":
    print("Please paste the string below")
    text = input()
    print("Do the names on the page include first names (ie Mr. Adam Smith instead of Mr. Smith)? (y/n)")
    first_names = (input() == "y")
    parser(text, first_names)