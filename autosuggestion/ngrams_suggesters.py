from typing import Sequence, Generator, Dict, List
import Levenshtein as levenshtein


# Edge n grams. An edge n-gram is Elastic Search parlance for an n-gram that starts at the beginning of the string,
# i.e. a prefix. So all the edge n-grams of “search” are [“s”, “se”, “sea”, “sear”, “searc”, “search”]

class EdgeNGramSuggester(object):
    """A simple suggester that keeps a dictionary from prefixes to suggestions.
    """
    def __init__(self):
        self.data = {}

    def index(self, suggestions: Sequence[str]) -> None:
        """Add the set of suggestions to the index.
        """
        for s in suggestions:
            for i in range(len(s)):
                ngram = s[0:i + 1]
                if ngram not in self.data:
                    self.data[ngram] = [s]
                else:
                    self.data[ngram].append(s)

    def search(self, prefix: str) -> Generator[str, None, None]:
        """Find suggestions that match the given prefix
        """
        if prefix in self.data:
            for s in self.data[prefix]:
                yield s
        else:
            return None


# Fuzzy search (n grams) => achieve a great deal of typo tolerance

def ngrams(text: str, size: int, sentinel: str = "_") -> Generator[str, None, None]:
    """Generate ngrams of the given size with sentinels padded at the begining, e.g.
    ngrams("foo", 2) -> ["_f", "fo", "oo"]
    Args:
        - text (str)
        - size (int)
        - sentinel (str): The sentinel to use for padding n-grams at the begining of the text.
    """
    padding = sentinel * (size - 1)
    text = padding + text
    length = len(text)
    end = length - size + 1
    for i in range(end):
        yield text[i:i + size]


class NGramSuggester(object):
    """A typo-tolerant suggester powered by an n-gram index.
    """
    def __init__(self, ngram_size: int = 2) -> None:
        self.data: Dict[str, List[str]] = {}
        self.ngram_size = ngram_size

    def index(self, suggestions: Sequence[str]) -> None:
        """Add the set of suggestions to the index.
        """
        for s in suggestions:
            for ngram in ngrams(s, self.ngram_size):
                if ngram not in self.data:
                    self.data[ngram] = [s]
                else:
                    self.data[ngram].append(s)

    def search(self, prefix: str, match_percentage: float = 0.9) -> Generator[str, None, None]:
        """Find suggestions that match the given prefix.
        Args:
            - prefix (str)
            - match_percentage (float): [0-1] the minimum percentage of n-grams that need to match for
              a suggestion to be returned. Lower values mean more fuzziness.
        """
        suggestions: dict = {}
        grams = list(ngrams(prefix, self.ngram_size))
        total_grams = len(grams)

        for ngram in grams:
            for s in self.data.get(ngram, []):
                if s in suggestions:
                    suggestions[s] += 1
                else:
                    suggestions[s] = 1

        for s, gram_count in suggestions.items():
            percentage = gram_count * 1.0 / total_grams
            if percentage > match_percentage:
                yield s

    def search_leveinshtein(self, prefix: str,
                            match_percentage: float = 0.9,
                            max_leveinshtein_distance: int = 3) -> Generator[str, None, None]:
        """Find suggestions that match the given prefix.
        Args:
            - prefix (str)
            - match_percentage (float): [0-1] the minimum percentage of n-grams that need to match for
              a suggestion to be returned. Lower values mean more fuzziness.
            - max_leveinshtein_distance (int): maximum levenshtein distance between suggestion and prefix
        """
        suggestions: dict = {}
        grams = list(ngrams(prefix, self.ngram_size))
        total_grams = len(grams)

        for ngram in grams:
            for s in self.data.get(ngram, []):
                if s in suggestions:
                    suggestions[s] += 1
                else:
                    suggestions[s] = 1

        for s, gram_count in suggestions.items():
            percentage = gram_count * 1.0 / total_grams
            if percentage > match_percentage:
                distance = levenshtein.distance(prefix, s[0:len(prefix)])
                if distance < max_leveinshtein_distance:
                    yield s
