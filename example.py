# This is a comment. Python ignores it, just like your cat ignores you.

# Constants are typically in SCREAMING_SNAKE_CASE
MAX_LIVES = 3  # Because three is a magic number

# Variables use snake_case (yes, Python loves snakes)
player_score = 0
is_game_over = False

def calculate_high_score(current_score, bonus_points):
    """This is a function. It does things and (hopefully) returns stuff."""
    # If statement: because sometimes we need to make decisions
    if bonus_points > 100:
        print("Wow, someone's been practicing!")
    
    return current_score + bonus_points

# While loop: keeps going until something happens
while not is_game_over:
    # For loop: when you need to do something a specific number of times
    for life in range(MAX_LIVES):
        print(f"Life {life + 1} of {MAX_LIVES}")
        
        # Another if statement, because why not
        if player_score > 9000:
            print("It's over 9000!")
            is_game_over = True
            break  # Exit the loop early
    
    # If we didn't break early, this will run
    if not is_game_over:
        player_score = calculate_high_score(player_score, 50)
        is_game_over = True  # End the game (and this example)

print(f"Final Score: {player_score}") 