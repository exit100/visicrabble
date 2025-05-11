import random
import pygame
from board import ScrabbleBoard
from tilebag import TileBag
from tilerack import TileRack
from scoring import ScrabbleScoring
from tile import Tile

class AIPlayer:
    def __init__(self, board, tile_bag, scoring):
        self.board = board
        self.tile_bag = tile_bag
        self.scoring = scoring
        self.tile_rack = TileRack()
        self.score = 0
        self.MAX_DEPTH = 2  # Maximum depth for minimax search
        
    def fill_rack(self):
        """Fill the AI's rack with tiles."""
        while len(self.tile_rack.tiles) < 7:
            tile = self.tile_bag.draw_tile()
            if tile:
                self.tile_rack.add_tile(tile)
            else:
                break

    def get_all_possible_moves(self):
        """Get all possible moves for the current state."""
        moves = []
        
        # First, try to find all possible positions where we can place tiles
        valid_positions = []
        for row in range(15):
            for col in range(15):
                if self.board.can_place(row, col):
                    # Check if this position is adjacent to any existing tile
                    has_adjacent = False
                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        r, c = row + dr, col + dc
                        if 0 <= r < 15 and 0 <= c < 15 and self.board.grid[r][c]:
                            has_adjacent = True
                            break
                    if has_adjacent:
                        valid_positions.append((row, col))
        
        # If no valid positions found, allow placing on the center tile for first move
        if not valid_positions and not any(self.board.grid[r][c] for r in range(15) for c in range(15)):
            valid_positions = [(7, 7)]  # Center position
        
        # Try placing combinations of tiles
        for start_row, start_col in valid_positions:
            # Try horizontal placement
            self._try_place_word(start_row, start_col, True, moves)
            # Try vertical placement
            self._try_place_word(start_row, start_col, False, moves)
        
        return moves

    def _try_place_word(self, start_row, start_col, horizontal, moves):
        """Try placing a word starting at the given position."""
        # Get all tiles from the rack
        rack_tiles = self.tile_rack.tiles.copy()
        
        # Try placing 1 to min(7, len(rack_tiles)) tiles
        for num_tiles in range(1, min(8, len(rack_tiles) + 1)):
            # Try all combinations of num_tiles tiles
            for tiles in self._get_tile_combinations(rack_tiles, num_tiles):
                # Try placing the tiles
                placed_tiles = []
                valid_placement = True
                
                for i, tile in enumerate(tiles):
                    if horizontal:
                        row, col = start_row, start_col + i
                    else:
                        row, col = start_row + i, start_col
                    
                    # Check if position is valid
                    if not (0 <= row < 15 and 0 <= col < 15 and self.board.can_place(row, col)):
                        valid_placement = False
                        break
                    
                    # Place the tile
                    if self.board.place_tile(tile, row, col):
                        placed_tiles.append(tile)
                    else:
                        valid_placement = False
                        break
                
                if valid_placement:
                    # Check if it forms a valid word
                    valid, _ = self.board.validate_current_turn()
                    if valid:
                        # Calculate score for this move
                        score = self.scoring.calculate_turn_score(self.board.current_turn_tiles, self.board)
                        moves.append((placed_tiles, start_row, start_col, score, horizontal))
                
                # Remove placed tiles
                for tile in placed_tiles:
                    self.board.remove_tile(tile)

    def _get_tile_combinations(self, tiles, n):
        """Get all possible combinations of n tiles from the given tiles."""
        if n == 0:
            return [[]]
        if not tiles:
            return []
        
        result = []
        for i in range(len(tiles)):
            current = tiles[i]
            remaining = tiles[:i] + tiles[i+1:]
            for combo in self._get_tile_combinations(remaining, n-1):
                result.append([current] + combo)
        return result

    def evaluate_position(self, player_score, ai_score):
        """Evaluate the current position."""
        # Simple evaluation: difference between AI and player scores
        return ai_score - player_score

    def minimax(self, depth, alpha, beta, is_maximizing, player_score, ai_score):
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return self.evaluate_position(player_score, ai_score)

        if is_maximizing:
            max_eval = float('-inf')
            moves = self.get_all_possible_moves()
            
            for tile, row, col, score in moves:
                # Make move
                self.board.place_tile(tile, row, col)
                new_ai_score = ai_score + score
                
                # Recursive evaluation
                eval = self.minimax(depth - 1, alpha, beta, False, player_score, new_ai_score)
                
                # Undo move
                self.board.remove_tile(tile)
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                    
            return max_eval
        else:
            min_eval = float('inf')
            moves = self.get_all_possible_moves()
            
            for tile, row, col, score in moves:
                # Make move
                self.board.place_tile(tile, row, col)
                new_player_score = player_score + score
                
                # Recursive evaluation
                eval = self.minimax(depth - 1, alpha, beta, True, new_player_score, ai_score)
                
                # Undo move
                self.board.remove_tile(tile)
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                    
            return min_eval

    def find_best_move(self, player_score):
        """Find the best move by evaluating all possible moves."""
        best_score = float('-inf')
        best_move = None
        moves = self.get_all_possible_moves()
        
        # If we have valid moves, find the one with highest score
        for tiles, start_row, start_col, score, horizontal in moves:
            if score > best_score:
                best_score = score
                best_move = (tiles, start_row, start_col, score, horizontal)
        
        # If no moves found, try to find any valid move
        if not best_move:
            for tile in self.tile_rack.tiles:
                for row in range(20):  # Updated to 20
                    for col in range(20):  # Updated to 20
                        if self.board.can_place(row, col):
                            # Try placing the tile
                            if self.board.place_tile(tile, row, col):
                                # Check if it forms a valid word
                                valid, _ = self.board.validate_current_turn()
                                if valid:
                                    score = self.scoring.calculate_turn_score(self.board.current_turn_tiles, self.board)
                                    if score > best_score:
                                        best_score = score
                                        best_move = ([tile], row, col, score, True)  # Default to horizontal
                                # Remove the tile to try next position
                                self.board.remove_tile(tile)
        
        return best_move

    def make_move(self, player_score):
        """Make the best move found."""
        best_move = self.find_best_move(player_score)
        
        if best_move:
            tiles, start_row, start_col, score, horizontal = best_move
            # Place all tiles
            success = True
            for i, tile in enumerate(tiles):
                if horizontal:
                    row, col = start_row, start_col + i
                else:
                    row, col = start_row + i, start_col
                
                if not self.board.place_tile(tile, row, col):
                    success = False
                    break
                self.tile_rack.remove_tile(tile)
            
            if success:
                # Update score
                self.score += score
                # End the turn to commit the move
                success, message, placed_tiles_count = self.board.end_turn()
                if success:
                    print(f"AI made move: {len(tiles)} tiles for {score} points")
                    # Fill the AI's rack with new tiles
                    for _ in range(placed_tiles_count):
                        new_tile = self.tile_bag.draw_tile()
                        if new_tile:
                            self.tile_rack.add_tile(new_tile)
                    return True, score
                else:
                    # If the move was invalid, undo it
                    for tile in tiles:
                        self.board.remove_tile(tile)
                        self.tile_rack.add_tile(tile)
                    self.score -= score
                    print(f"AI move failed: {message}")
                    return False, 0
        
        # If no valid move found, try to exchange tiles
        if len(self.tile_rack.tiles) > 0:
            print("AI exchanging tiles")
            # Return all tiles to the bag
            old_tiles = self.tile_rack.tiles.copy()
            self.tile_rack.tiles.clear()
            for tile in old_tiles:
                self.tile_bag.return_tile(tile)
            # Draw new tiles
            while len(self.tile_rack.tiles) < 7:
                tile = self.tile_bag.draw_tile()
                if tile:
                    self.tile_rack.add_tile(tile)
            return True, 0
            
        print("AI could not make a move")
        return False, 0

    def draw(self, surface):
        """Draw the AI's rack."""
        # Draw AI's rack above the board
        rack_width = 7 * (45 + 8) - 8
        x = (1200 - rack_width) // 2
        y = 10
        
        # Draw rack background
        rack_rect = pygame.Rect(x - 10, y - 10, rack_width + 20, 45 + 20)
        pygame.draw.rect(surface, (220, 220, 220), rack_rect, border_radius=10)
        pygame.draw.rect(surface, (180, 180, 180), rack_rect, width=2, border_radius=10)
        
        # Draw tiles
        for i, tile in enumerate(self.tile_rack.tiles):
            tile.rect.x = x + (i * (45 + 8))
            tile.rect.y = y
            tile.draw(surface)
        
        # Draw AI's score
        font = pygame.font.SysFont(None, 30)
        score_text = font.render(f"AI Score: {self.score}", True, (0, 0, 0))
        surface.blit(score_text, (x - 150, y + 10)) 