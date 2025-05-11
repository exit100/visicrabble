class ScrabbleScoring:
    def __init__(self):
        self.letter_scores = {
            'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
            'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
            'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
            'Y': 4, 'Z': 10, '_': 0
        }

    def calculate_word_score(self, word, start_pos, board, horizontal=True):
        """Calculate the score for a word placed at a specific position."""
        if not word:
            return 0
            
        score = 0
        word_multiplier = 1
        row, col = start_pos

        for i, letter in enumerate(word):
            # Get the current position
            current_row = row if horizontal else row + i
            current_col = col + i if horizontal else col
            
            # Get letter score
            letter_score = self.letter_scores[letter]
            
            # Apply letter multiplier if it's a new tile
            bonus = board.get_bonus(current_row, current_col)
            if bonus:
                bonus_type, _ = bonus
                if bonus_type == 'DL':
                    letter_score *= 2
                elif bonus_type == 'TL':
                    letter_score *= 3
                elif bonus_type == 'DW':
                    word_multiplier *= 2
                elif bonus_type == 'TW':
                    word_multiplier *= 3
            
            score += letter_score

        return score * word_multiplier

    def calculate_turn_score(self, placed_tiles, board):
        """Calculate the score for a turn based on placed tiles."""
        if not placed_tiles:
            return 0

        # Get positions of placed tiles
        positions = [(tile.placed_cell[0], tile.placed_cell[1]) for tile in placed_tiles]
        
        # Determine if the word is horizontal or vertical
        rows = [pos[0] for pos in positions]
        cols = [pos[1] for pos in positions]
        horizontal = len(set(rows)) == 1
        
        # Sort positions to get the start of the word
        if horizontal:
            positions.sort(key=lambda x: x[1])  # Sort by column
        else:
            positions.sort(key=lambda x: x[0])  # Sort by row
            
        start_pos = positions[0]
        
        # Get the main word
        main_word = board.get_word_at(start_pos[0], start_pos[1], horizontal)
        if not main_word:
            return 0
            
        # Calculate score for the main word
        score = self.calculate_word_score(main_word, start_pos, board, horizontal)
        
        # Check for crossing words
        for tile in placed_tiles:
            row, col = tile.placed_cell
            # Check perpendicular word
            cross_word = board.get_word_at(row, col, not horizontal)
            if len(cross_word) > 1 and cross_word != main_word:
                # Find the start position of the crossing word
                if not horizontal:
                    # For vertical main word, find horizontal crossing word start
                    c = col
                    while c >= 0 and board.grid[row][c]:
                        c -= 1
                    cross_start = (row, c + 1)
                else:
                    # For horizontal main word, find vertical crossing word start
                    r = row
                    while r >= 0 and board.grid[r][col]:
                        r -= 1
                    cross_start = (r + 1, col)
                
                score += self.calculate_word_score(cross_word, cross_start, board, not horizontal)

        return score

    def calculate_rack_score(self, rack):
        """Calculate the score value of tiles in a rack."""
        return sum(self.letter_scores[tile.letter] for tile in rack)

    def calculate_bonus(self, placed_tiles_count):
        """Calculate any bonus points (e.g., for using all tiles)."""
        if placed_tiles_count == 7:  # Bingo bonus
            return 50
        return 0 