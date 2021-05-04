import pygame
import pickle
from network import Network
from game import Card, Trick, Player, Game
from settings import *

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

pygame.font.init()
my_font = pygame.font.SysFont('calibri', 25)


class Button:
    def __init__(self, text, top_left, bottom_right, is_visible):
        self.text = text
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.is_visible = is_visible
        self.width = self.bottom_right[0] - self.top_left[0]
        self.height = self.bottom_right[1] - self.top_left[1]

    def draw_button(self, win):
        button_surface = pygame.Surface((self.width, self.height))
        button_surface.fill((0, 0, 0))
        button_text = my_font.render(self.text, False, (255, 255, 255))
        button_surface.blit(button_text, (0, 0))
        win.blit(button_surface, self.top_left)

    def pos_in_button(self, pos):
        if self.top_left[0] <= pos[0] <= (self.top_left[0] + self.width) and \
                (self.bottom_right[1] - self.height) <= pos[1] <= self.bottom_right[1]:
            return True
        else:
            return False


#########################################################################################
# Drawing functions
#########################################################################################


def draw_main_screen(win, game, player):
    win.fill((255, 255, 255))
    player_text_surface_string = f'Player {player + 1}'
    if game.current_player == player:
        player_text_surface_string += ' - It is your turn'
    player_text_surface = my_font.render(player_text_surface_string, False, (0, 0, 0))
    score_text_surface = my_font.render(f'Current points: {game.players[player].score}', False, (0, 0, 0))
    win.blit(player_text_surface, (5, 5))
    win.blit(score_text_surface, (200, 550))

    for i, card in enumerate(game.players[player].hand):
        win.blit(card.draw(), (i * 35 + 15, 500))
    draw_trick(win, player, game.current_trick.cards)


def draw_trick(win, player, cards):
    trick_positions = [(285, 315), (255, 285), (285, 255), (315, 285)]
    if len(cards) > 0:
        initial_player = cards[0].player
        offset = initial_player - player
        for i, card in enumerate(cards):
            win.blit(card.draw(), trick_positions[(offset + i) % 4])


def draw_score_screen(win, game):
    win.fill((255, 255, 255))
    scores_text = [f'Player {i} has {game.players[i].score} points' for i in range(4)]
    scores_text_surfaces = [my_font.render(score_text, False, (0, 0, 0)) for score_text in scores_text]
    for i in range(4):
        win.blit(scores_text_surfaces[i], (200, 200 + 30 * i))


def draw_game_over_screen(win, game):
    win.fill((255, 255, 255))
    game_over_text = f'Player {game.winner} wins!'
    game_over_surface = my_font.render(game_over_text, False, (0, 0, 0))
    win.blit(game_over_surface, (250, 300))


#########################################################################################
# Helper functions
#########################################################################################


def pos_in_square(pos, square):
    if square[0][0] <= pos[0] <= square[1][0] and square[0][1] <= pos[1] <= square[1][1]:
        return True
    else:
        return False


#########################################################################################
# Main function
#########################################################################################


def main():
    run = True
    n = Network()
    player_number = n.get_number()
    view_scores = False
    button_list = [Button('View scores', (475, 0), (600, 30), True),
                   Button('Return to game', (440, 0), (600, 30), False)]

    game = n.ping_server()
    hand_length = len(game.players[player_number].hand)

    key_index = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
                 pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9, pygame.K_q: 10, pygame.K_w: 11, pygame.K_e: 12,
                 pygame.K_r: 13}

    card_index = [[(i * 35 + 15, 500), (i * 35 + 45, 530)] for i in range(hand_length)]

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN and event.key in key_index:
                card_number = key_index[event.key]

                game = n.send(game.players[player_number].hand[card_number - 1])

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if 500 <= pos[1] <= 530:
                    for i, square in enumerate(card_index):
                        if pos_in_square(pos, square):
                            game = n.send(game.players[player_number].hand[i])
                            hand_length = len(game.players[player_number].hand)
                            card_index = [[(i * 35 + 15, 500), (i * 35 + 45, 530)] for i in range(hand_length)]
                elif 0 <= pos[1] <= 30:
                    for i, button in enumerate(button_list):
                        if i == 0:
                            if button.is_visible and button.pos_in_button(pos):
                                view_scores = True
                        elif i == 1:
                            if button.is_visible and button.pos_in_button(pos):
                                view_scores = False

        game = n.ping_server()
        hand_length = len(game.players[player_number].hand)
        card_index = [[(i * 35 + 15, 500), (i * 35 + 45, 530)] for i in range(hand_length)]

        # this section decides which screen needs to be displayed
        if game.winner == 'no winner':
            if view_scores:
                draw_score_screen(window, game)
                button_list[0].is_visible = False
                button_list[1].is_visible = True

            else:
                draw_main_screen(window, game, player_number)
                button_list[0].is_visible = True
                button_list[1].is_visible = False
        else:
            draw_game_over_screen(window, game)
            button_list[0].is_visible = False
            button_list[1].is_visible = False

        for button in button_list:
            if button.is_visible:
                button.draw_button(window)

        pygame.display.update()


main()
