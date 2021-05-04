import pygame
import random
from settings import *

pygame.font.init()
my_font = pygame.font.SysFont('calibri', 18)


class Card:
    def __init__(self, suit, value, player):
        self.suit = suit
        self.value = value
        self.player = player

    def __str__(self):
        return self.value + self.suit + '-P' + str(self.player)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value and self.player == other.player
        else:
            return False

    # returns a pygame Surface with the cards information to be drawn by the client
    def draw(self):
        background_surface = pygame.Surface((30, 30))
        background_surface.fill((0, 0, 0))
        text_surface = my_font.render(self.value + self.suit, False, (255, 255, 255))
        background_surface.blit(text_surface, (0, 0))
        return background_surface

    def get_card_value(self):
        value_order = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8, '10': 9,
                       'J': 10, 'Q': 11, 'K': 12, 'A': 13}
        return value_order[self.value]


class Trick:
    def __init__(self, initial_player):
        self.initial_player = initial_player
        self.cards = []
        self.suit = False

    # checks if the card is a valid card to be played in the trick, and if so, adds it to the trick
    def add_card(self, card):
        if len(self.cards) == 0:
            self.suit = card.suit
        self.cards.append(card)

    def trick_winner(self):
        if len(self.cards) < 4:
            return 'No winner'
        else:
            initial_suit_cards = [card for card in self.cards if card.suit == self.suit]
            return max(initial_suit_cards, key=lambda p: p.get_card_value()).player

    def draw(self, player_number):
        trick_draw_positions = [(50, 150), (0, 50), (50, 0), (100, 50)]
        background_surface = pygame.Surface((150, 150))
        background_surface.fill((255, 255, 255))
        offset = self.initial_player - player_number
        for card in self.cards:
            background_surface.blit(card.draw(), trick_draw_positions[offset % 4])
        return background_surface

    def count_hearts(self):
        return sum([1 for card in self.cards if card.suit == 'H'])

    def contains_qos(self):
        for card in self.cards:
            if card.suit == 'S' and card.value == 'Q':
                return True
        return False

    def __str__(self):
        suit_string = self.suit if self.suit else 'No suit'
        return str(self.cards) + suit_string


def sort_hand(hand):
    def order(card):
        suit_order = {'H': 1, 'S': 2, 'D': 3, 'C': 4}
        value_order = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7,
                       '9': 8, '10': 9, 'J': 10, 'Q': 11, 'K': 12, 'A': 13}
        return suit_order[card.suit] * 13 + value_order[card.value]

    return sorted(hand, key=order)


class Player:
    def __init__(self, player_number, player_hand, player_score):
        self.player_number = player_number
        self.hand = sort_hand(player_hand)
        self.tricks = []
        self.score = player_score

    # checks whether the player has a card of a particular suit in their hand
    def has_suit(self, suit):
        for card in self.hand:
            if card.suit == suit:
                return True
        return False

    # calculates the score of the player at the end of the round (13 tricks)
    def calculate_scores(self):
        number_of_hearts = sum([trick.count_hearts() for trick in self.tricks])
        queen_of_spades = any(trick.contains_qos() for trick in self.tricks)

        return number_of_hearts + (queen_of_spades * 13)


class Game:
    def __init__(self, prev_scores):
        vals = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['H', 'D', 'S', 'C']
        card_values = []
        for i in vals:
            for j in suits:
                card_values.append((j, i))
        random.shuffle(card_values)

        deck0 = []
        deck1 = []
        deck2 = []
        deck3 = []
        for i, card_val in enumerate(card_values):
            if i % 4 == 0:
                deck0.append(Card(card_val[0], card_val[1], 0))
            elif i % 4 == 1:
                deck1.append(Card(card_val[0], card_val[1], 1))
            elif i % 4 == 2:
                deck2.append(Card(card_val[0], card_val[1], 2))
            else:
                deck3.append(Card(card_val[0], card_val[1], 3))

        self.p0 = Player(0, deck0, prev_scores[0])
        self.p1 = Player(1, deck1, prev_scores[1])
        self.p2 = Player(2, deck2, prev_scores[2])
        self.p3 = Player(3, deck3, prev_scores[3])

        self.players = [self.p0, self.p1, self.p2, self.p3]

        self.total_points = TOTAL_POINTS

        self.trick_count = 0
        self.hearts_dropped = False
        self.end_of_round = False
        self.current_player = 0
        self.current_trick = Trick(0)
        self.winner = 'no winner'

    # checks whether the card given is allowed to be played with the trick, ie by checking whether the player indeed
    # has that card, whether the trick already has 4 cards, and if suits are correct
    def valid_card(self, card):
        if self.current_player == card.player and any(
                [card == hand_card for hand_card in self.players[card.player].hand]):
            if len(self.current_trick.cards) == 0:
                if card.suit != 'H':
                    return True
                else:
                    if self.hearts_dropped:
                        return True
                    else:
                        return False
            elif len(self.current_trick.cards) < 4:
                if card.suit == self.current_trick.suit:
                    return True
                else:
                    if self.players[self.current_player].has_suit(self.current_trick.suit):
                        return False
                    else:
                        return True
            else:
                return False
        return False

    # adds the card to the trick, after checking whether it is allowed to be added
    def add_card(self, card):
        if self.valid_card(card):
            # adds the card to the trick
            self.current_trick.add_card(card)

            # identifies the corresponding card from the players hand and removes it
            server_card = [hand_card for hand_card in self.players[self.current_player].hand if hand_card == card].pop()
            self.players[self.current_player].hand.remove(server_card)

            # changes the turn
            self.change_turn()

            # if the card just played was a heart, set hearts_dropped to true
            if card.suit == 'H':
                self.hearts_dropped = True
            print(self.current_trick)

        # checks if the trick has a winner
        trick_winner = self.current_trick.trick_winner()

        if trick_winner != 'No winner':
            print(f'Player {trick_winner + 1} won that trick!')
            self.players[trick_winner].tricks.append(self.current_trick)

            if sum([len(self.players[i].tricks) for i in range(4)]) == 13:
                self.round_over()
                self.end_of_round = True
            else:
                self.current_trick = Trick(trick_winner)
                self.current_player = trick_winner
                for i in range(4):
                    print(f'Player {i + 1} has won these tricks: {[str(trick) for trick in self.players[i].tricks]}')

    def change_turn(self):
        self.current_player += 1
        self.current_player = self.current_player % 4

    def round_over(self):
        player_heart_scores = [player.calculate_scores() for player in self.players]
        full_scores = [i for i, n in enumerate(player_heart_scores) if n == 26]
        if full_scores:
            full_score_player = full_scores.pop()
            round_scores = [26, 26, 26].insert(full_score_player, 0)
        else:
            round_scores = player_heart_scores
        for i in range(4):
            self.players[i].score += round_scores[i]
        self.winner = self.check_victory()
        if self.winner != 'no winner':
            self.game_over()

    def check_victory(self):
        over_total_points = [(i, self.players[i].score) for i in range(4) if self.players[i].score >= self.total_points]
        if over_total_points:
            return max(over_total_points, key=lambda p: p[1])[0]
        else:
            return 'no winner'

    def game_over(self):
        pass

    def __str__(self):
        return str(self.current_player)
