class Dictionary:
    def __init__(self, dictionary_file='7letterdictionary.txt'):
        self.words = set()
        self.load_dictionary(dictionary_file)
    
    def load_dictionary(self, filename):
        try:
            with open(filename, 'r') as f:
                for line in f:
                    word = line.strip().lower()
                    if word:  # Skip empty lines
                        self.words.add(word)
        except FileNotFoundError:
            print(f"Warning: Dictionary file {filename} not found. Word validation will be disabled.")
    
    def is_valid_word(self, word):
        return word.lower() in self.words 