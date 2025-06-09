class Solution:
    def decodeMessage(self, key: str, message: str) -> str:
        vocabulary='abcdefghijklmnopqrstuvwxyz'
        decoder={' ':' '}
        i=0
        for letter in key:
            if letter not in decoder:
                decoder[letter]=vocabulary[i]
                i+=1
        decoded_message=[decoder[letter] for letter in message]
        return ''.join(decoded_message)