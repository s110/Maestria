class Solution:
    def maxNumberOfBalloons(self, text: str) -> int:
        text_dict = dict({'b': 0, 'a': 0, 'l': 0, 'o': 0, 'n': 0})
        text_dict_word = dict({'b': 1, 'a': 1, 'l': 2, 'o': 2, 'n': 1})
        for x in text:
            if x in text_dict and x in 'ban':
                text_dict[x] += 1
            elif x in text_dict and x in 'ol':
                text_dict[x] += 1 / 2
        if int(min(text_dict.values())) > 0:
            return int(min(text_dict.values()))
        return 0
