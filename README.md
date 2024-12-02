# AstolatCardGame
 a card game project intended to personally learn developing ai for card-based games using Python 
# Game Setup

## Players

The game is designed for a single player facing off against an AI opponent. It can be played with a regular deck of cards.

## Deck Composition

- **Standard Suits**: Hearts, Diamonds, Spades, and Clubs.
- **Card Range**: Each suit includes cards from Ace to 10.
- **Special Cards**: Two Jesters (one red, one black) are included.

## Starting Hand

Each player starts the game with **5 cards**, drawn randomly from the shuffled deck.

## Top Cards

Each player has a stack of three face cards, placed face-up in front of them:

- **Jack** (15 health)
- **Queen** (25 health)
- **King** (40 health)

*Face Cards must be defeated in sequence for a player to win.*

---

# Gameplay Mechanics

## Turn Structure

1. **Draw Phase**: At the start of each turn, draw one card from the deck.
   - If the deck is empty, reshuffle the discard pile to form a new draw deck.
2. **Action Phase**: Play one card from your hand to:
   - **Attack** the opponent’s current top card.
   - **Activate** a special ability.
3. **Discard Phase**: After playing a card, move it to the discard pile.

## Card Functions and Special Abilities

### Hearts

- **Attack**: Use the card’s value as attack damage.
- **Heal**: Restore health equal to the card's value to your current face card (up to its starting health).

### Clubs

- **Double Damage**: Automatically deal double their face value in damage when used for an attack.

### Spades

- **Combined Attack**: Combine their attack value with another card from your hand for a single powerful attack.
  - *Note*: The secondary card’s ability does not activate.

### Diamonds

- **Attack**: Use the card’s value as attack damage.
- **Defense**: Subtract the card's value from the damage of the next attack from the opponent.

### Jesters

- **Hand Refresh**: Discard your current hand and draw until your hand is full (5 cards).
- *Jesters are not moved to the discard pile when used; instead, turn them face-down to indicate they have been used.*

---

# Winning the Game

Defeat all three of your opponent’s Top Cards to win.

This requires careful management of your hand and strategic use of card abilities to:

- **Maximize Damage**
- **Minimize Losses** from AI attacks

---

# Difficulty Levels

## Easy

- The AI makes slower decisions and may not always use card abilities optimally.

## Medium

- The AI balances attack and defense with more strategic decisions.

## Hard

- The AI plays aggressively, anticipates player actions, and optimally uses card abilities.

---

**Enjoy the game!**
