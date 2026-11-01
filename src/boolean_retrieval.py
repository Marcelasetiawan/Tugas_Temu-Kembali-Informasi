"""
Boolean Retrieval (exact match, tanpa ranking).

Operator: AND, OR, NOT (huruf besar) dan tanda kurung.
Prioritas: NOT > AND > OR. Dua term berurutan tanpa operator dianggap AND.

Langkah:
    1. Query dipecah menjadi term dan operator; setiap term diproses dengan
       preprocessing yang sama dengan dokumen.
    2. Notasi infix diubah ke postfix (algoritma shunting-yard).
    3. Postfix dievaluasi dengan operasi himpunan pada postings list:
       AND = irisan, OR = gabungan, NOT = komplemen terhadap seluruh dokumen.
"""

import re

PRECEDENCE = {"NOT": 3, "AND": 2, "OR": 1}


class BooleanRetrieval:
    def __init__(self, index, preprocessor):
        self.index = index
        self.pre = preprocessor
        self.all_docs = set(index.doc_len)

    def parse(self, query):
        tokens = []
        for raw in re.findall(r"\(|\)|[^\s()]+", query):
            if raw in PRECEDENCE or raw in ("(", ")"):
                item = raw
            else:
                terms = self.pre.preprocess(raw)
                item = ("TERM", terms[0] if terms else raw.lower())
            # AND implisit: "term term", "term (", "term NOT", ") term"
            if tokens:
                prev = tokens[-1]
                if (isinstance(prev, tuple) or prev == ")") and \
                        (isinstance(item, tuple) or item in ("(", "NOT")):
                    tokens.append("AND")
            tokens.append(item)
        return tokens

    @staticmethod
    def to_postfix(tokens):
        output, stack = [], []
        for tok in tokens:
            if isinstance(tok, tuple):
                output.append(tok)
            elif tok == "(":
                stack.append(tok)
            elif tok == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                if stack:
                    stack.pop()
            else:
                while (stack and stack[-1] != "(" and
                       (PRECEDENCE[stack[-1]] > PRECEDENCE[tok] or
                        (PRECEDENCE[stack[-1]] == PRECEDENCE[tok] and tok != "NOT"))):
                    output.append(stack.pop())
                stack.append(tok)
        while stack:
            output.append(stack.pop())
        return output

    def search(self, query):
        stack = []
        for tok in self.to_postfix(self.parse(query)):
            if isinstance(tok, tuple):
                stack.append(set(self.index.postings(tok[1])))
            elif tok == "NOT":
                stack.append(self.all_docs - (stack.pop() if stack else set()))
            else:
                right = stack.pop() if stack else set()
                left = stack.pop() if stack else set()
                stack.append(left & right if tok == "AND" else left | right)
        result = stack.pop() if stack else set()
        return sorted(result, key=lambda d: int(re.sub(r"\D", "", d) or 0))
