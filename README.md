# Poker50
#### Project Overview:
"Poker50 - The Monte Carlo TexasHoldem Poker Engine" is a Texas Hold'em simulation tool built for my CS50P final project. The main goal is to simulate poker hands for one or more players to study the randomness of hand ranks without the distraction of betting. I started this project to practice Object-Oriented Programming (OOP) and to build a foundation for a future poker bot. By running simulations and studying the results, the program can help strengthen "poker intuition" with hard data. This project was developed in late 2025 as a way to combine my interest in game theory with the Python skills I gained throughout the course.

#### Project Outline

Summary: Simulating poker hands to study rank randomness and probability.
Flexibility: You can play solo to check hand frequencies or against multiple opponents to see win rates.
Customization: You can define specific cards for any player to test "what-if" scenarios or let them be assigned randomly.
Simulation: Community cards are dealt randomly for each trial to calculate win probabilities based on the remaining deck.

#### Code Structure
The project is organized into modular classes and functions to ensure the code is easy to read and maintain:

##### Classes:
1. Building Blocks:
Card: Represents a single card with rank and suit validation. It uses properties and setters to ensure no "impossible" cards enter the deck.
Deck: Manages a standard 52-card set. It includes methods for shuffling, dealing with "pop," and dealing without removing cards for simulation purposes.

2. Pattern Matching:
HandAnalyzer: Evaluates 7 cards (2 hole cards + 5 community cards) to find the best 5-card combination. It uses frequency maps for pairs and sliding windows for sequences.
HandRanker: Converts the analyzer's findings into a numerical Rank Tuple for easy comparison between players.

##### B. Main Function Flow
The main function coordinates the user experience through four primary steps:
1. Get Player Hand: The user decides whether to define their starting cards or receive random ones from the deck.
2. Get Opponents Hand: You can set the number of opponents (up to 22) and choose how many of their hands you want to manually define.
3. Get Simulation Count: The user chooses how many trials to run. The program is currently capped at 1,000 simulations to balance speed and accuracy.
4. Run Simulation: The engine deals random community cards and determines winners for every trial, tracking wins, losses, and split pots.


#### Hand Strength Logic:
The engine recognizes all ten standard poker hand ranks. To break ties, it uses lexicographical comparison of rank tuples,comparing the rank of the pattern first, then the primary winning card values, then the kickers (remaining high cards).

10: Royal Flush (A, K, Q, J, T of the same suit)

9: Straight Flush (Five cards in a row of the same suit)

8: Four of a Kind	(Four cards of the same rank)

7: Full House (Three of a kind plus a pair)

6: Flush (Any five cards of the same suit)

5: Straight (Five cards in a numerical sequence)

4: Three of a Kind (Three cards of the same rank)

3: Two Pairs (Two different pairs in one hand)

2: One Pair (Two cards of the same rank)

1: High Card (The highest single card held)

