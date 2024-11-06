import tkinter as tk
from tkinter import messagebox
import random
from typing import List, Tuple, Optional

from game import BattleshipGame
from ship import Ship
from ai import BattleshipAI

class BattleshipGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Battleship Game")
        
        # Initialize variables
        self.setup_new_game()
        
        # Create main game frame
        self.game_frame = tk.Frame(master)
        self.game_frame.pack(padx=20, pady=20)
        
        # Create control frame
        self.control_frame = tk.Frame(master)
        self.control_frame.pack(pady=10)
        
        # Create board frames
        self.create_board_frames()
        
        # Create status label
        self.status_label = tk.Label(master, text="Place your ships!", font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # Create ship status frames
        self.create_ship_status_frames()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Start ship placement phase
        self.start_ship_placement()
    
    def setup_new_game(self):
        """Initialize all game variables for a new game"""
        self.player_game = BattleshipGame()
        self.ai = BattleshipAI()
        self.ai_game = BattleshipGame()
        
        # Clear existing ship positions
        self.player_game.board = self.player_game.board = [[' ' for _ in range(10)] for _ in range(10)]
        self.player_game.ships = []
        
        # Game state variables
        self.is_player_turn = True
        self.game_over = False
        self.setup_phase = True
        
        # Ship placement variables
        self.ships_to_place = [
            ("Carrier", 5),
            ("Battleship", 4),
            ("Cruiser", 3),
            ("Submarine", 3),
            ("Destroyer", 2)
        ]
        self.current_ship_index = 0
        self.is_horizontal = True
        self.placement_preview = set()  # Store cells being previewed
    
    def create_board_frames(self):
        # Player's board frame
        self.player_frame = tk.LabelFrame(self.game_frame, text="Your Board", padx=10, pady=10)
        self.player_frame.grid(row=0, column=0, padx=20)
        
        # AI's board frame
        self.ai_frame = tk.LabelFrame(self.game_frame, text="AI's Board", padx=10, pady=10)
        self.ai_frame.grid(row=0, column=1, padx=20)
        
        # Create board buttons
        self.player_buttons = []
        self.ai_buttons = []
        
        for i in range(10):
            player_row = []
            ai_row = []
            for j in range(10):
                # Player's board buttons - increased width for probability numbers
                p_btn = tk.Button(self.player_frame, width=5, height=1)
                p_btn.grid(row=i+1, column=j+1)
                p_btn.bind('<Enter>', lambda e, x=i, y=j: self.preview_ship_placement(x, y))
                p_btn.bind('<Leave>', lambda e: self.clear_ship_preview())
                p_btn.bind('<Button-1>', lambda e, x=i, y=j: self.place_ship(x, y))
                p_btn.bind('<Button-3>', lambda e: self.toggle_ship_orientation())
                player_row.append(p_btn)
                
                # AI's board buttons
                ai_btn = tk.Button(self.ai_frame, width=4, height=1)
                ai_btn.grid(row=i+1, column=j+1)
                ai_btn.configure(state='disabled')  # Disabled during setup
                ai_row.append(ai_btn)
            
            self.player_buttons.append(player_row)
            self.ai_buttons.append(ai_row)
        
        # Add row/column labels
        for i in range(10):
            # Row labels
            tk.Label(self.player_frame, text=str(i)).grid(row=i+1, column=0)
            tk.Label(self.ai_frame, text=str(i)).grid(row=i+1, column=0)
            
            # Column labels
            tk.Label(self.player_frame, text=str(i)).grid(row=0, column=i+1)
            tk.Label(self.ai_frame, text=str(i)).grid(row=0, column=i+1)
    
    def create_ship_status_frames(self):
        # Create frames for ship status
        self.player_ships_frame = tk.LabelFrame(self.master, text="Your Ships", padx=10, pady=5)
        self.player_ships_frame.pack(side=tk.LEFT, padx=20)
        
        self.ai_ships_frame = tk.LabelFrame(self.master, text="AI Ships", padx=10, pady=5)
        self.ai_ships_frame.pack(side=tk.RIGHT, padx=20)
        
        # Add ship status labels
        self.player_ship_labels = {}
        self.ai_ship_labels = {}
        
        for ship_name, length in self.ships_to_place:
            label = tk.Label(self.player_ships_frame, 
                           text=f"{ship_name} ({length}): Not Placed", 
                           fg="orange")
            label.pack(anchor="w")
            self.player_ship_labels[ship_name] = label
    
    def create_control_buttons(self):
        # Create restart button (initially disabled)
        self.restart_button = tk.Button(self.control_frame, 
                                      text="Restart Game", 
                                      command=self.restart_game,
                                      state='disabled')
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        # Create reset placement button
        self.reset_placement_button = tk.Button(self.control_frame, 
                                              text="Reset Placement", 
                                              command=self.reset_placement)
        self.reset_placement_button.pack(side=tk.LEFT, padx=5)
    
    def start_ship_placement(self):
        """Start the ship placement phase"""
        self.setup_phase = True
        self.current_ship_index = 0
        self.is_horizontal = True
        self.update_placement_status()
        
        # Enable player board, disable AI board
        for i in range(10):
            for j in range(10):
                self.player_buttons[i][j]['state'] = 'normal'
                self.ai_buttons[i][j]['state'] = 'disabled'
    
    def toggle_ship_orientation(self):
        """Toggle ship orientation between horizontal and vertical"""
        self.is_horizontal = not self.is_horizontal
        self.status_label.configure(
            text=f"Placing {self.ships_to_place[self.current_ship_index][0]} "
                 f"({'Horizontal' if self.is_horizontal else 'Vertical'})"
        )
    
    def preview_ship_placement(self, x: int, y: int):
        """Preview ship placement when hovering over cells"""
        if not self.setup_phase or self.current_ship_index >= len(self.ships_to_place):
            return
        
        self.clear_ship_preview()
        ship_name, ship_length = self.ships_to_place[self.current_ship_index]
        
        # Calculate ship positions
        positions = self.get_ship_positions(x, y, ship_length)
        if not positions:  # Invalid placement
            return
        
        # Show preview
        self.placement_preview = set(positions)
        for px, py in positions:
            self.player_buttons[px][py].configure(bg="lightgray")
    
    def clear_ship_preview(self):
        """Clear the ship placement preview"""
        for x, y in self.placement_preview:
            if self.player_game.board[x][y] == ' ':
                self.player_buttons[x][y].configure(bg="SystemButtonFace")
        self.placement_preview.clear()
    
    def get_ship_positions(self, x: int, y: int, length: int) -> List[Tuple[int, int]]:
        """Get list of positions for ship placement, or empty list if invalid"""
        positions = []
        if self.is_horizontal:
            if y + length > 10:  # Out of bounds
                return []
            positions = [(x, y + i) for i in range(length)]
        else:
            if x + length > 10:  # Out of bounds
                return []
            positions = [(x + i, y) for i in range(length)]
        
        # Check for overlapping ships
        for px, py in positions:
            if self.player_game.board[px][py] != ' ':
                return []
            
            # Check adjacent cells
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = px + dx, py + dy
                    if (0 <= nx < 10 and 0 <= ny < 10 and 
                            self.player_game.board[nx][ny] != ' ' and 
                            (nx, ny) not in positions):
                        return []
        
        return positions
    
    def place_ship(self, x: int, y: int):
        """Place a ship at the specified position"""
        if not self.setup_phase or self.current_ship_index >= len(self.ships_to_place):
            return
        
        ship_name, ship_length = self.ships_to_place[self.current_ship_index]
        positions = self.get_ship_positions(x, y, ship_length)
        
        if not positions:
            return
        
        # Place the ship
        ship = Ship(ship_name, ship_length)
        ship.positions = positions
        self.player_game.ships.append(ship)
        
        for px, py in positions:
            self.player_game.board[px][py] = ship_name[0]
            self.player_buttons[px][py].configure(bg="gray")
        
        # Update ship status
        self.player_ship_labels[ship_name].configure(
            text=f"{ship_name} ({ship_length}): Active",
            fg="green"
        )
        
        # Move to next ship
        self.current_ship_index += 1
        if self.current_ship_index >= len(self.ships_to_place):
            self.finish_setup()
        else:
            self.update_placement_status()
    
    def update_placement_status(self):
        """Update status label during ship placement"""
        if self.current_ship_index < len(self.ships_to_place):
            ship_name = self.ships_to_place[self.current_ship_index][0]
            self.status_label.configure(
                text=f"Place your {ship_name} "
                     f"({'Horizontal' if self.is_horizontal else 'Vertical'})\n"
                     "Right-click to rotate"
            )
    
    def finish_setup(self):
        """Finish the setup phase and start the game"""
        self.setup_phase = False
        self.is_player_turn = True
        
        # Enable AI board for attacks
        for i in range(10):
            for j in range(10):
                self.ai_buttons[i][j].configure(state='normal')
                self.ai_buttons[i][j].configure(
                    command=lambda x=i, y=j: self.handle_player_move(x, y)
                )
        
        # Initialize AI ships display
        for ship in self.ai_game.ships:
            label = tk.Label(self.ai_ships_frame, 
                           text=f"{ship.name} ({ship.length}): Active", 
                           fg="green")
            label.pack(anchor="w")
            self.ai_ship_labels[ship.name] = label
        
        # Update status
        self.status_label.configure(text="Your turn! Click on AI's board to attack")
        self.reset_placement_button.configure(state='disabled')
    
    def reset_placement(self):
        """Reset the ship placement phase"""
        # Clear board
        self.player_game.board = [[' ' for _ in range(10)] for _ in range(10)]
        self.player_game.ships = []
        
        # Reset buttons
        for i in range(10):
            for j in range(10):
                self.player_buttons[i][j].configure(bg="SystemButtonFace")
        
        # Reset ship labels
        for ship_name, length in self.ships_to_place:
            self.player_ship_labels[ship_name].configure(
                text=f"{ship_name} ({length}): Not Placed",
                fg="orange"
            )
        
        # Restart placement
        self.current_ship_index = 0
        self.update_placement_status()
    
    def restart_game(self):
        """Restart the entire game"""
        # Clear AI ships frame
        for widget in self.ai_ships_frame.winfo_children():
            widget.destroy()
        
        # Reset game state
        self.setup_new_game()
        
        # Reset all buttons
        for i in range(10):
            for j in range(10):
                self.player_buttons[i][j].configure(
                    bg="SystemButtonFace",
                    state='normal'
                )
                self.ai_buttons[i][j].configure(
                    bg="SystemButtonFace",
                    state='disabled'
                )
        
        # Reset ship labels
        for ship_name, length in self.ships_to_place:
            self.player_ship_labels[ship_name].configure(
                text=f"{ship_name} ({length}): Not Placed",
                fg="orange"
            )
        
        # Enable reset placement button
        self.reset_placement_button.configure(state='normal')
        
        # Disable restart button
        self.restart_button.configure(state='disabled')
        
        # Start placement phase
        self.start_ship_placement()
    
    def handle_player_move(self, x: int, y: int):
        if not self.is_player_turn or self.game_over:
            return
        
        # Check if cell was already hit
        if self.ai_buttons[x][y]['state'] == 'disabled':
            return
        
        # Process player's move
        is_hit = self.ai_game.check_hit(x, y)
        self.ai_buttons[x][y]['state'] = 'disabled'
        
        if is_hit:
            self.ai_buttons[x][y].configure(bg="red")
            # Find hit ship and update status
            for ship in self.ai_game.ships:
                if (x, y) in ship.positions:
                    ship.hits.add((x, y))
                    if ship.is_sunk():
                        self.ai_ship_labels[ship.name].configure(
                            text=f"{ship.name} ({ship.length}): Sunk", 
                            fg="red"
                        )
        else:
            self.ai_buttons[x][y].configure(bg="blue")
        
        # Check for game over
        if all(ship.is_sunk() for ship in self.ai_game.ships):
            self.game_over = True
            messagebox.showinfo("Game Over", "Congratulations! You won!")
            return
        
        # Switch turns
        self.is_player_turn = False
        self.status_label.configure(text="AI's turn...")
        
        # Update probability heatmap before AI's move
        self.update_probability_heatmap()
        
        self.master.after(1000, self.handle_ai_move)
    
    def update_probability_heatmap(self):
        """Update the player's board visualization with AI's probability numbers"""

        print(self.ai.probability_map)
        print("=======================")
        for i in range(10):
            for j in range(10):
                # Skip cells that have been hit
                if self.player_buttons[i][j]['bg'] in ['red', 'blue']:
                    continue
                    
                # Get probability and format it
                prob = self.ai.probability_map[i][j]
                if prob == 0:
                    text = ""  # Empty text for zero probability 
                else:
                    # Format to 2 decimal places
                    text = f"{prob * 100:.2f}"
                
                # Update button text
                self.player_buttons[i][j].configure(text=text)
    
    def handle_ai_move(self):
        if self.game_over:
            return
        
        # Get AI's move
        x, y = self.ai.get_next_target()
        is_hit = self.player_game.check_hit(x, y)
        
        # Find hit ship if it's a hit
        hit_ship = None
        if is_hit:
            for ship in self.player_game.ships:
                if (x, y) in ship.positions:
                    ship.hits.add((x, y))
                    hit_ship = ship
                    if ship.is_sunk():
                        self.player_ship_labels[ship.name].configure(
                            text=f"{ship.name} ({ship.length}): Sunk", 
                            fg="red"
                        )
                    break
        
        # Update AI's game state
        self.ai.update_game_state(x, y, is_hit, hit_ship)
        
        # Update visual representation
        self.player_buttons[x][y].configure(
            bg="red" if is_hit else "blue"
        )
        
        # Check for game over
        if all(ship.is_sunk() for ship in self.player_game.ships):
            self.game_over = True
            messagebox.showinfo("Game Over", "AI won! Better luck next time!")
            return
        
        # Switch turns
        self.is_player_turn = True
        self.status_label.configure(text="Your turn! Click on AI's board to attack")

def main():
    root = tk.Tk()
    app = BattleshipGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()