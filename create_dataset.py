import re
import Levenshtein
import nltk
import pandas as pd
from tqdm import tqdm

from wikiedits.wiki_edit_extractor import WikiEditExtractor

wiki_dump = "wiki.xml"
output_df = "corrections.csv"


w = WikiEditExtractor(wiki_dump, lang="english")


class Edit:
    """ just interface to wikiedits outputs 
    
        ([(original, idited), ...], 
        {'id': int,
        'timestamp': iso8661-time,
        'contributor': {'username': username, 'id': int},
        'comment': comment,
        'page': {'title': title, 'id': int}}
    
    """

    def __init__(self, data):
        self.edits = [(edit[0], edit[1]) for edit in data[0]]
        self.meta = data[1]

    def find_grammar(self):
        a, b = [[nltk.word_tokenize(j) for j in i] for i in zip(*self.edits)]
        res = []
        for l, r in zip(a, b):
            if len(l) == len(r):
                for w1, w2 in zip(l, r):
                    if w1.lower() == w2.lower():
                        continue
                    elif (
                        Levenshtein.distance(w1.lower(), w2.lower()) <= 3
                        and len(w1) > 4
                        and len(w2) > 4
                    ):
                        res.append((w1, w2))
                    else:
                        break
        return res, self.meta["id"]


edits = w.extract_edits()

with open(output_df, "a+") as file:
# pd.DataFrame(columns=["original", "corrected", "id"]).to_csv(output_df, index=False)
    file.write("original,corrected,id\n")
    for i in tqdm(edits, desc="Searching for corrections..."):
        ed = Edit(i)
        cors, id = ed.find_grammar()
        for c in cors:
            file.write(c[0] + ',' + c[1] + ',' + str(id) + '\n')
            # pd.DataFrame({"original": [c[0]], "corrected": [c[1]], "id": [id]}).to_csv(
            #     file, header=False, index=False
            # )
