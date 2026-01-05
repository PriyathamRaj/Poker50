
"""
----------------------------------------------------------------------------
PRIYATHAM TOOK CS50P
Thanks to Prof. Malan and the staff, great course and even greater teaching

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~Poker50: The Monte Carlo Poker Engine~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below is a project in poker that I started in November of 2025 in parallel with the course.

THE MAIN FUNCTION STARTS FROM LINE 440. PRIOR TO THAT ARE ALL THE CLASSES REQUIRED TO RUN THE POKER TABLE

There are comments everywhere, original and updated ones, all containing my ideas while I was attempting
to solve all the challenges, or even defining them and their scope to begin with.
These may come of use to beginners who are interested to attempt such a project. Please reach out to me for any
clarifications or potential mistakes, shall be happy to discuss.
Intermediate/Advanced programmers may brush through the comments and review the code and share feedback if possible.
Thanks.
----------------------------------------------------------------------------
"""

"""
Nov 2, 2025
Implement Texas Holdem variant of Poker in python, for fun, in an interactive way
Goal is to be able to conduct the game and evaluate hands, later to run simulations and test some hypotheses I have in mind
Ultimate goal is to build a bot player that can play, to win
Learnings goals - Python, OOPS, system/structured/forward thinking, Poker randomness theory
"""

import random

# Phase 1 - Identify and create objects
# Usual suspects are - Card, Deck, Player, Round, HandRank, HandEvaluation

# --------------CARD--------------
# Begin with card. Creation will happen in Deck class, here its just initiation. Rank and Suit to be passed in.
# Ranks: A, 2 to 10, J, Q, K, A again - skip the first A for now, can handle it in hand evaluation for straights
# Suits: Spade, Heart, Diamond, Club - first letters can be used as they're unique
# Should be able to print the cards in a neat way (AH, KC, or maybe Ah, Kc for better clarity)
# Should also be able to return the value of the card
class Card:
    values = {str(n): n for n in range(2,10)}
    values.update({'T':10,'J':11,'Q':12,'K':13,'A':14})
    
    suits = ['s','h','d','c']

    def __init__(self, rank:str, suit:str):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank}{self.suit.lower()}"
    
    def value(self):
        return self.values[self.rank]
    
    @property
    def rank(self):
        return self._rank
    
    @rank.setter
    def rank(self, rank):
        normalized_rank = str(rank).upper()
        if normalized_rank not in Card.values:
            raise ValueError("Invalid Value")
        self._rank = normalized_rank

    @property
    def suit(self):
        return self._suit
    
    @suit.setter
    def suit(self, suit):
        normalized_suit = str(suit).lower()
        if normalized_suit not in Card.suits:
            raise ValueError("Invalid Suit")
        self._suit = normalized_suit

    def __eq__(self, other):
        return (isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit)

    def __hash__(self):
        return hash((self.rank, self.suit))

"""
card1 = Card('5','h')
card2 = Card('J','s')
print(card1, card2)
"""

# --------------DECK--------------
# Creation: Use the class Card to create 52 instances of cards.
#   First declare the ranks and suits in lists, use them to create the deck
#   Suits: Spade, Heart, Diamond, Club - first letters can be used as they're unique
# Usage: Shuffle, pop(x cards)

class Deck:
    def __init__(self):
        self.ranks = [str(i) for i in range(2,10)]
        self.ranks.extend(['T','J','Q','K','A'])
        self.suits = ['s','h','d','c']
        self.cards = [Card(i,j) for i in self.ranks for j in self.suits]

    def __repr__(self):
        return f"Deck: {' '.join(str(c) for c in self.cards)}"
    
    def __len__(self):
        return len(self.cards)
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self,n):
        out = [self.cards.pop() for _ in range(n)]
        return out
        #return random.sample(self.cards,k=n)

    def deal_wo_pop(self,n):
        return random.sample(self.cards,k=n)
    
    def burn(self,n):
        for _ in range(n):
            self.cards.pop()

    def remove_cards(self,cards):
        for card in cards:
            self.cards.remove(card)
    
    def add_cards(self,cards):
        for card in cards:
            self.cards.append(card)

    def deal_specific(self,cards):
        return [card for card in self.cards if card in cards]

"""
deck = Deck()
print(deck)

deck.shuffle()
print(deck)
c1 = deck.deal(2)
print(c1)
"""

# --------------PLAYER--------------
# Creation: player shall have a pot of a fixed amount for now and will bet (if first to bet) or call at every CTA
# There won't be any raise/fold for now. All hands will go to showdown.
# What other methods are required?
# Assign cards and reset cards

class Player:
    def __init__(self, name, pot = 1000):
        self.name = name
        self.pot = pot
        self.current_bet = 20 #bet_amount
        self.cards = []
    
    def __repr__(self):
        return f"Player Name: {self.name} | Cards: {self.cards} | Pot: {self.pot}"

    def bet(self):
        self.pot -= self.current_bet
        return self.current_bet
    
    def call(self):
        return self.current_bet
    
    def receive_cards(self,cards):
        self.cards = cards

    def reset_cards(self):
        self.cards = []

"""
p1 = Player('Charles',1000,20)
p1.receive_cards(deck.deal(2))
print(p1)
"""

# --------------HandRank--------------
# used to declare the order of strength of hands, high card being the lowest to royal flush being the highest
# better to start from the best and then cover all possibilities and then let the high card be determined at the end
# There's multiple aspects to ranking - one is category, then comes strength of it, then the kicker.
# Category is the one pair/3 of a kind/straight/flush/full house etc
# Its strength is the rank of the cards forming that category (a king pair vs a 4 pair)
# Then comes kicker for comparison
# Input will be a pair of cards belonging to a player, and the 5 cards on the table (called community cards apparently)
# need to create a list of all 7 cards, and evaluate all possible combinations 
# update - the strength method needs to contain reference to all the possible hand ranks, and within it it should just check
#   ..against all those and return the winning hand, that's it
#   Strengths method cant become the 300 line monster with all patterns coded inside it.
#   Let each pattern be inside a is_two_pair(self): kind of structure

# Update - renamed the class from handrank to HandAnalyzer. This will just detect the 10 different best 5 card patterns in poker.
# The true hand rank class will determine the value-rank of the hand among the 10 possible winning hands, and also output the
# primary winning cards and kickers so that the hand-comparison class can take over.

class HandAnalyzer:

    def __init__(self,hole,community):
        self.hole = hole
        self.community = community
        self.all_cards = hole + community

    def card_values(self):
        return [card.value() for card in self.all_cards]
    
    def find_straight(self, cards_list):
        # After few iterations: tricky due to multiple reasons. Ace can be both 1 and 14. Do we need highest value card to be definitely from 
        # player's pot if it exists? Update - maybe not. Just the best 5 are required. Can independently check community cards if needed
        # What do we need ultimately? Need the five cards that make up a straight. Not just the values. That's what I got earlier and had to scrap.
        # Finally: First, obtain all unique values, but map each unique value to a card.
        # Then obtain values from this dict
        # Then, the tricky part - need to consider ace as one if it exists, make sure the modifications hold true post evaluation
        # Then check for the straight, and obtain the range of values
        # Using these values, fetch cards from the value-card mapping - how are cards fetched in case of multiple cards?
        # Return True, the cards, and the highest(first as its sorted in descending order) card
        
        # Modified to take cards_list separately to allow checking flush cards to solve for straight flush
        # first check whether there's at least 5 cards received as input
        if not cards_list or len(cards_list) < 5:
            return {'Hand': None, 'Cards': None, 'Values': None}
        
        unique_values = {}
        for card in sorted(cards_list, key = lambda c: c.value(), reverse=True):
            unique_values.setdefault(card.value(), card) #setdefault will initiate a key only once
        
        # fetch values
        vals = sorted(unique_values.keys(), reverse=True)

        # handle ace
        if 14 in vals:
            vals.append(1)
            # update the corresponding value's (which is a key in unique_values dict) value in unique_values dict
            unique_values[1] = unique_values[14] #same card goes and sits there
            
        # now the straight logic
        for i in range(len(vals)-4): 
            # minus 4 is to iterate through all items that can form a 5 card sequence, which does not need last 4 elements
            window = vals[i:i+5]
            if window[0] == window[-1]+4:
                cards = [unique_values[v] for v in window]
                return {'Hand':'Straight', 'Cards':cards, 'Values':[card.value() for card in cards]}
            
        return {'Hand':None, 'Cards':None, 'Values':None}
    
    def is_straight(self):
        return self.find_straight(self.all_cards)
    
    def is_flush(self):
        # build a dict of suits and counts
        suits = {x:0 for x in ['s','h','d','c']}
        for card in self.all_cards:
            suits[card.suit] += 1
        for suit, val in suits.items():
            if val >= 5:
                cards = sorted([card for card in self.all_cards if card.suit == suit],
                                      key = lambda c: c.value(),
                                      reverse = True)
                return {'Hand':'Flush', 'Cards':cards, 'Values':[card.value() for card in cards]}
                # modified to return all possible cards so that they can be sent to is_straight
                # # before, it was top 5. but straight flushes below the highest card were missing
        return {'Hand':None, 'Cards':None, 'Values':None}
    
    def is_multiples(self):
        # count counts of each unique value and store in a dict.
        # If both 2 and 3 (or 3 and 3) are present in it, then its a full house.
        # return the two cards in descending order of count and then value

        # Updated this method to evaluate all possibilities where there's multiple occurrences of any one card
        # Initially was supposed to be only for Full House. But the counts dict can be used to obtain Quads too
        # Hence extended it to Three of a kind and a pair/two pairs too in the same method. Multiple birds with one stone

        counts = {}
        for card in self.all_cards:
            v = card.value()
            counts[v] = counts.get(v,0) + 1
        
        # Quads
        if 4 in counts.values():
            quads = [v for v,c in counts.items() if c == 4]
            quad = max(quads)
            cards = [card for card in self.all_cards if card.value() == quad]
            cards.append(sorted([card for card in self.all_cards if card.value() != quad],
                                 key = lambda c:c.value(), 
                                 reverse = True)[0])
            return {'Hand':'Four of a Kind', 'Cards':cards, 'Values':[card.value() for card in cards]}
        
        # Full house, Three of a Kind, Two Pair, One Pair, High Card
        trips = [v for v,c in counts.items() if c == 3]
        pairs = [v for v,c in counts.items() if c >= 2]
        if trips:
            trip = max(trips)
            remaining_cards = [v for v in pairs if v != trip]
            if remaining_cards:
            # pairs has all cards with 2 or more occurrences. Remaining cards is pairs, with the highest trips excluded.
            # even if there's one more card value with 3 occurrences, since its the second highest, only 2 of them will be
            # considered to build the full house
            # if remaining cards is non empty, it means there's at least one card value other than the trips card
                pair = max(remaining_cards)
                cards = [card for card in self.all_cards if card.value() == trip]
                cards.extend([card for card in self.all_cards if card.value() == pair][:2])
                return {'Hand':'Full House', 'Cards':cards, 'Values':[card.value() for card in cards]}
            else: # remainigng_cards is empty --> there's only one card value with more than one count, and that's trips
                cards = [card for card in self.all_cards if card.value() == trip]
                cards.extend(sorted([card for card in self.all_cards if card.value() != trip], 
                                     key = lambda c:c.value(), 
                                     reverse = True)[:2])
                return {'Hand':'Three of a Kind', 'Cards':cards, 'Values':[card.value() for card in cards]}
        elif pairs:
            x = len(pairs)
            if x == 1:
                pair = max(pairs)
                cards = sorted([card for card in self.all_cards if card.value() == pair],
                               key = lambda c:c.value(),
                               reverse=True)
                cards.extend(sorted([card for card in self.all_cards if card.value() != pair], 
                                     key = lambda c:c.value(), 
                                     reverse = True)[:3])
                return {'Hand':'One Pair', 'Cards':cards, 'Values':[card.value() for card in cards]}
            elif x >= 2:
                two_pairs = sorted(pairs, reverse=True)[:2]
                cards = sorted([card for card in self.all_cards if card.value() in two_pairs],
                               key = lambda c:c.value(),
                               reverse=True)
                cards.append(sorted([card for card in self.all_cards if card.value() not in two_pairs],
                                 key = lambda c:c.value(), 
                                 reverse = True)[0])
                return {'Hand':'Two Pairs', 'Cards':cards, 'Values':[card.value() for card in cards]}
        else:
            cards = sorted([card for card in self.all_cards], key = lambda x: x.value(), reverse=True)[:5]
        return {'Hand':'High Card', 'Cards':cards, 'Values':[card.value() for card in cards]}
    
"""
placeholder

"""

class HandRanker:
    def __init__(self, hole, community):
        # Call the HandAnalyzer here
        self.analyzer = HandAnalyzer(hole,community)
        # declare a dict of hand ranks and zeroes, and update to one if any logic is met
        self.strengths = {'High Card':1,         # done
                          'One Pair':2,          # done
                          'Two Pairs':3,         # done
                          'Three of a Kind':4,   # done
                          'Straight':5,          # done
                          'Flush':6,             # done
                          'Full House':7,        # done
                          'Four of a Kind':8,    # done
                          'Straight Flush':9,    # done
                          'Royal Flush':10       # done
                          }

    def strength(self):        
        multiples = self.analyzer.is_multiples()
        straight = self.analyzer.is_straight()
        flush = self.analyzer.is_flush()

        # update: in addition to returning the 'Hand' name and 'Cards', will also return the numerical rank of the hand,
        # the primary winners, and the kickers, so that they can be used by HandComparator

        # update: built the initial version which returns hand name and best 5 cards
        # some research with chatgpt on how to best generate and store this data to be used for comparisons easily, found this effin
        # amazing ability of lists and tuples to do lexicographical comparison. Will be returning all numerical stuff in that
        # along with the pretty printing of hand name and the best 5 cards.
        ####################
        # Returning in tuples will allow direct numerical and ordered comparison of hands. 
        # Order - Rank, Primary Winners, Kickers
        ####################
        # also found it useful to create a tuple creator helper function

        def rank_tuple(code, primary, kickers=()):
            return (code, tuple(primary), tuple(kickers))

        if flush['Cards']:
            straight_flush = self.analyzer.find_straight(flush['Cards'])
            if straight_flush['Cards']:
                high = straight_flush['Cards'][0].value()
                # No kickers for straight and royal flushes. basically no kickers if all 5 cards are required to form the hand rank
                if high == 14:
                    return {'Hand':'Royal Flush', 'Cards':straight_flush['Cards'], 'RankTuple':rank_tuple(10,(high,),())}
                else:
                    return {'Hand':'Straight Flush', 'Cards':straight_flush['Cards'], 'RankTuple':rank_tuple(9,(high,),())}
        if multiples['Hand'] == 'Four of a Kind':
            multiples['RankTuple'] = rank_tuple(8,(multiples['Values'][0],),(multiples['Values'][-1],))
            return multiples
        elif multiples['Hand'] == 'Full House':
            multiples['RankTuple'] = rank_tuple(7,(multiples['Values'][0],multiples['Values'][3]),)
            return multiples
        elif flush['Cards']:
            flush['Cards'] = flush['Cards'][:5]
            flush['Values'] = flush['Values'][:5]
            flush['RankTuple'] = rank_tuple(6,flush['Values'][:5],)
            return flush
        elif straight['Cards']:
            straight['RankTuple'] = rank_tuple(5,(straight['Values'][0],),)
            return straight
        elif multiples['Hand'] == 'Three of a Kind':
            multiples['RankTuple'] = rank_tuple(4,(multiples['Values'][0],),multiples['Values'][-2:])
            return multiples
        elif multiples['Hand'] == 'Two Pairs':
            multiples['RankTuple'] = rank_tuple(3,(multiples['Values'][0],multiples['Values'][2]),(multiples['Values'][-1],))
            return multiples
        elif multiples['Hand'] == 'One Pair':
            multiples['RankTuple'] = rank_tuple(2,(multiples['Values'][0],),multiples['Values'][-3:])
            return multiples
        elif multiples['Hand'] == 'High Card':
            multiples['RankTuple'] = rank_tuple(1,multiples['Values'],)
            return multiples
    
    def strength_pretty_print(self):
        print(self.strength()['Hand'], self.strength()['Cards'])


# --------------Round--------------
# The main action!
# Shuffle deck, deal hands to n players. Woah, wait. First need to setup the table of players.
# Create another class of table above, taking player count, pot amount, bet amount etc.
# Anyway, the order is - take table, start a round, keep round count, assign dealer, small and big blinds, 
#   shuffle cards, deal cards to n players, take initial bets
#   burn card, deal flop, take bets
#   burn card, deal turn, take bets
#   burn card, deal river, take bets
#   showdown (send to evaluation)
# Maybe better to first build handrank and handevaluation classes first. This can be the final class.
# Or maybe the main program itself.

# Update - back to this after building the HandAnalyzer and HandRanker classes.
# Before I worry about whether this should be a class or the main program, I will first run a heads-up game for fun and check if I'm able to 
# find winners

class Round:
    def __init__(self):
        # what all are required to conduct a round?
        # A Deck, list of players, dealer position,
        pass
        # put on hold for now.

# check point   


"""
----------------------------------------------------
PRIYATHAM TOOK CS50P
Thanks to Prof. Malan and the staff, great course
----------------------------------------------------
"""

# Below code written to satisfy CS50P's requirement of having a main and 3 functions (not cooked up, but required per the idea of what to build)
# The rest of the project to be completed on my own system/personal project. This version is good for submission.

# Idea is to enable a user interaction. Let the user pick any card they want. Describe the number of players they want to play against.
# Have checks and balances for these steps.
# Then, let the user describe how many hands they want to simulate. Then show the results of their hand.
# Can this be made more fun? Like let the user guess if they've won the hand or not, for a given particular hand? May be.
# Maybe I'll let the user define the # of opponent hands they want to build themselves (from 0 to all)
# That way the user has the ability to check how their hands perform in all variations of randomness - 
# - Random/defined pick of their own hand x random/defined pick of their opponent(s)
# Lets go.

def main():
    deck = Deck()
    #print(f"Deck Length: {len(deck)}")
    
    print()
    player_hand = Get_Player_Hand(deck)
    print(f"Player Hand: {player_hand}")
    print()
    #print(f"Deck Length: {len(deck)}")

    deck.shuffle()
    
    opponents_hands = Get_Opponents_Hand(deck)
    print(f"Opponents Hands: {opponents_hands}")
    print()
    #print(f"Deck Length: {len(deck)}")

    sim_count = Get_Simulation_Count()
    
    hand_strengths, rank_results, winning_ranks\
        , community_cards, winning_ranks_dict = Run_Simulation(player_hand, sim_count, deck, opponents_hands)
    
    #for hand, strength in hand_strengths.items():
    #    print(f"Hand: {hand}, Strength: {strength}")
    
    player_wins = 0
    split_wins = 0
    opponent_wins = 0
    opponents = {tuple(op):0 for op in opponents_hands}

    winner = None
    for sim, winning_hand in rank_results.items():
        if player_hand in winning_hand:
            if len(winning_hand) > 1:
                winner = 'Split'
                split_wins += 1
            else:
                winner = 'Player'
                player_wins += 1
        else:
            if len(winning_hand) > 1:
                winner = 'Split'
                split_wins += 1
            else:
                winner = f"Opponent {opponents_hands.index(winning_hand[0])+1}"
                opponent_wins += 1
                opponents[tuple(winning_hand[0])] += 1


        # Uncomment the below line to see results of each simulation
        #print(f"Simulation #: {sim}, Winning Hand: {winning_hand}, Community: {community_cards[sim-1]}, Winner: {winner}, Winning Hand Strength: {winning_ranks[sim-1]}")
    
    #print(f"Player Hand: {player_hand}")
    #print(f"Opponents Hands: {opponents_hands}")
    #print()

    print('------------------------------------------------------------')
    print()
    print(f"Simulations: {sim_count}, Player Wins: {player_wins}, Opponent Wins: {opponent_wins}, Split: {split_wins}")
    print()
    print(f"Player Win %: {round(player_wins/sim_count*100,2)}")
    print(f"Opponent Wins %: {round(opponent_wins/sim_count*100,2)}")
    print(f"Split Wins %: {round(split_wins/sim_count*100,2)}")
    print()
    print('------------------------------------------------------------')
    print(f"Opponents Wins: {opponents}")
    print()
    print(f"Winning Hand Strength Summary: {winning_ranks_dict}")
    print('------------------------------------------------------------')
    print()
    
    

def Get_Player_Hand(d):
    while True:
        try:
            chois = int(input("Do you want to define your hand (0) or receive a random hand (1): "))
            if not chois in [0,1]:
                raise ValueError("Choice not in [0,1]")
        except ValueError:
            print("Invalid Input 1")
            continue
        else:
            break
    
    if chois == 1:
        d.shuffle()
        return d.deal(2)
    else:
        while True:
            try:
                c1v = input('Enter card 1 value: ')
                c1s = input('Enter card 1 suit: ')

                c2v = input('Enter card 2 value: ')
                c2s = input('Enter card 2 suit: ')
                
                card1 = Card(c1v, c1s)
                card2 = Card(c2v, c2s)

                if card1 == card2:
                    raise ValueError("Can't pick the same card twice")

                if card1 not in d.cards:
                    raise ValueError(f"Card {card1} is not in the deck.")
                if card2 not in d.cards:
                    raise ValueError(f"Card {card2} is not in the deck.")
                
                d.remove_cards([card1, card2])
                return [card1, card2]
            
            except ValueError:
                print("Invalid Input 2")
                continue

def Get_Opponents_Hand(d):
    while True:
        try:
            opps = int(input("Enter Number of Opponents (between 0 and 22): "))
            # 52 cards. 5 community, 3 burnt (max), leaving 44 cards -> 22 players at max, mathematically. I'll allow it.
            if not opps in range(23):
                raise ValueError("Choice not in the 0-22 range")
            if opps > 0:
                oppcards = int(input(f"Enter number of Opponents whose cards you want to define (between 0 and {opps}): "))
                if not oppcards in range(opps+1):
                    raise ValueError(f"Opponent Hands definition choice not in the 0-{opps} range")
        except ValueError:
            print("Invalid Input 3")
            continue
        else:
            break
    
    opponents_hand = []

    if opps > 0:        # 5 for example
        if oppcards > 0:        # 2 for example
            for i in range(oppcards):
                while True:
                    try:
                        c1v = input('Enter card 1 value: ')
                        c1s = input('Enter card 1 suit: ')

                        c2v = input('Enter card 2 value: ')
                        c2s = input('Enter card 2 suit: ')
                        
                        card1 = Card(c1v, c1s)
                        card2 = Card(c2v, c2s)

                        if card1 == card2:
                            raise ValueError("Can't pick the same card twice")

                        if card1 not in d.cards:
                            raise ValueError(f"Card {card1} is not in the deck.")
                        if card2 not in d.cards:
                            raise ValueError(f"Card {card2} is not in the deck.")
                        
                        d.remove_cards([card1, card2])
                        opponents_hand.append([card1,card2])
                        print(opponents_hand)
                        break

                    except ValueError:
                        print("Invalid Input 4")
                        continue
                        
            if opps - oppcards > 0:
               for i in range(opps-oppcards):
                   opponents_hand.append(d.deal(2))
        else:
            for i in range(opps):
                opponents_hand.append(d.deal(2))
    return opponents_hand


def Get_Simulation_Count():
    # lets allow any count between 1 and 1000 for now
    max_sim = 1000
    while True:
        try:
            sim_count = int(input(f"Enter simulation count, between 1 and {max_sim}: "))
            if sim_count < 1 or sim_count > max_sim:
                raise ValueError(f"Simulation Count not in the range 1-{max_sim}")
        except ValueError:
            print("Invalid Input 5")
            continue
        else:
            break
    return sim_count


def Run_Simulation(p_hand, s_count, deck, opp_hand=[]):
    hand_strengths = {  'High Card':0,
                        'One Pair':0,
                        'Two Pairs':0,
                        'Three of a Kind':0,
                        'Straight':0,
                        'Flush':0,
                        'Full House':0,
                        'Four of a Kind':0,
                        'Straight Flush':0,
                        'Royal Flush':0
                        }

    hand_ranks = {  'High Card':1,         
                    'One Pair':2,          
                    'Two Pairs':3,         
                    'Three of a Kind':4,   
                    'Straight':5,          
                    'Flush':6,             
                    'Full House':7,        
                    'Four of a Kind':8,    
                    'Straight Flush':9,    
                    'Royal Flush':10
                    }
    # what all do i need? First, two scenarios. One - where there's no opponents. I just need to show the hand's strength metrics.
    # irrespective of # of opponents, I still need to obtain hand wise strengths of each hand (player + opponents)
    # then, in the case of non-zero opponents, i can run the tuple lexicographical comparison thing to obtain a sorted list of winners
    # but, for each simulation, i need to store all these results. what are the result types?
    # Base level: for each hand, there's a hand ranks dictionary that needs to be updated.
    # So a dictionary with n items where n = player(1) + # of opponents. Key = the Hand, Value = the hand_ranks dict of that hand.
    # I also need a dict of Hand : Hand Rank output, where for each hand I get a tuple of hand rank, primary winner values, kickers values
    # need this dict to declare the winner
    # Need a simulation dict too? for each sim #, need to store the winner and show in how many cases the player won, and what hands won the rest
    # and some cool insights on top of it.
    # woah. Okay. Lets do it.

    hand_types = hand_strengths.keys()
    all_hands = [p_hand] + opp_hand

    rank_results = {sim+1:0 for sim in range(s_count)}
    hand_strengths_output = {tuple(h):hand_strengths.copy() for h in all_hands}
    hand_ranks_output = {tuple(h):0 for h in all_hands}
    winning_ranks = []
    community_cards = []
    winning_ranks_dict = hand_strengths.copy()

    for i in range(s_count):
        community = deck.deal_wo_pop(5)
        # now we have all the player's cards and the community cards (for this particular sim) ready
        # next step 1 - for each hand calcualte and update its hand_results dict (results)
        # for each sim - calculate the winner and store it in a separate dict (rankings)
        for hand in all_hands:
            hand_key = tuple(hand)

            hr_output = HandRanker(hand, community).strength()
            hand_strengths_output[hand_key][hr_output['Hand']] += 1
            hand_ranks_output[hand_key] = hr_output['RankTuple']

        sorted_hands = dict(sorted(hand_ranks_output.items(), key = lambda c: c[1], reverse=True))
        winner = max(sorted_hands.values())
        winning_rank_value = winner[0]
        win_rank = [k for k,v in hand_ranks.items() if v == winning_rank_value][0]
        winning_ranks.append(win_rank)
        winners = [list(k) for k, v in sorted_hands.items() if v == winner]
        winning_ranks_dict[win_rank] += 1
        rank_results[i+1] = winners
        community_cards.append(community)

    return hand_strengths_output, rank_results, winning_ranks, community_cards, winning_ranks_dict


if __name__ == '__main__':
    main()