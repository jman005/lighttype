import random
import json

class InvalidCorpusException(Exception):
    pass

class Corpus():
    def __init__(self, name, description, filename):
        self.words = []
        self.name = name
        self.description = description
        with open(filename, "r") as f:
            data = f.read()

        for line in data.split("\n"):
            if " " in line:
                raise InvalidCorpusException("Words in provided corpus %s should not have spaces" % filename)
            self.words.append(line)
        if len(self.words) < 1:
            raise InvalidCorpusException("Provided corpus '%s' is empty" % filename)

    def getRandomWord(self):
        return random.choice(self.words)

with open("lightype/corpi/corpus-index.json", "r") as f:
    _corpus_data = json.loads(f.read())

Corpi = {}
for corpus in _corpus_data.keys():
    Corpi[corpus] = Corpus(_corpus_data[corpus]['name'],
                           _corpus_data[corpus]['description'],
                           _corpus_data[corpus]['location'])

