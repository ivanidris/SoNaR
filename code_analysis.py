import re
import dautil as dl
import pandas as pd


def compile_pattern():
    patterns = ['lambda ', 'yield ', '==', 'def ', 'import ‘, ‘class ']
    return re.compile("|".join(patterns))


def clean_line(line):
    tokens = line.split()
    filtered = [t for t in tokens if not t.isdigit()]

    return " ".join(filtered)

if __name__ == "__main__":
    pattern = compile_pattern()
    corpus = dl.nlp.WebCorpus('sonar_corpus')
    selected = []

    for text in corpus.get_texts():
        for line in text.split("\n"):
            if len(pattern.findall(line)) > 0:
                selected.append(clean_line(line))

    df = dl.nlp.calc_tfidf(selected, ngram_range=(2, 4))
    flag_df = pd.DataFrame(columns=['Flag'])
    pd.concat([df, flag_df]).to_csv('code_keywords.csv')
