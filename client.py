import pygame
import pickle
from network import Network
from game import Card, Trick, Player, Game
from settings import *

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

pygame.font.init()
my_font = pygame.font.SysFont('calibri', 25)


def redraw_window(win, game, player, view_score):
    win.fill((255, 255, 255))
    if game.winner == 'no winner':
        if view_score:
            scores_text = [f'Player {i} has {game.players[i].score} points' for i in range(4)]
            scores_text_surfaces = [my_font.render(score_text, False, (0, 0, 0)) for score_text in scores_text]
            for i in range(4):
                win.blit(scores_text_surfaces[i], (200, 200 + 30 * i))
        else:
            player_text_surface_string = f'Player {player + 1}'
            if game.current_player == player:
                player_text_surface_string += ' - It is your turn'
            player_text_surface = my_font.render(player_text_surface_string, False, (0, 0, 0))
            score_text_surface = my_font.render(f'Current points: {game.players[player].score}', False, (0, 0, 0))
            win.blit(player_text_surface, (5, 5))
            win.blit(score_text_surface, (200, 550))

            view_score_surface = pygame.Surface((100, 30))
            view_score_surface.fill((0, 0, 0))
            view_score_text = my_font.render('View scores', False, (255, 255, 255))
            view_score_surface.blit(view_score_text, (0, 0))
            win.blit(view_score_surface, (500, 0))

            for i, card in enumerate(game.players[player].hand):
                win.blit(card.draw(), (i * 35 + 15, 500))
            for i, card in enumerate(game.current_trick.cards):
                win.blit(card.draw(), (i * 35 + 15, 250))
    else:
        game_over_text = f'Player {game.winner} wins!'
        game_over_surface = my_font.render(game_over_text, False, (0, 0, 0))
        win.blit(game_over_surface, (250, 300))
    pygame.display.update()


def draw_text(win, text, position, with_background):
    if with_background:
        background_surface = pygame
    text_surface = my_font.render(text, False, position)
    win.blit(text_surface, position)


def main():
    run = True
    n = Network()
    player_number = n.get_number()
    view_scores = False

    game = n.ping_server()

    key_index = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
                 pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9, pygame.K_q: 10, pygame.K_w: 11, pygame.K_e: 12,
                 pygame.K_r: 13}

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN and event.key in key_index:
                card_number = key_index[event.key]

                game = n.send(game.players[player_number].hand[card_number - 1])
                print(game.current_trick)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if 530 < pos[0] < 600 and 0 < pos[1] < 30:
                    view_scores = True

        game = n.ping_server()

        redraw_window(window, game, player_number, view_scores)


main()
