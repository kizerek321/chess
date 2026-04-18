import pygame
import sys
from constants import screen, fps, timer, big_font, font
from main import local_main
from client import client_run

WIDTH = 1000

def draw_menu():
    screen.fill('azure')
    
    title = big_font.render("CHESS MULTIPLAYER", True, 'black')
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
    
    # Przycisk: Gra Lokalna
    pygame.draw.rect(screen, 'black', [300, 400, 400, 80])
    pygame.draw.rect(screen, 'gold', [300, 400, 400, 80], 3)
    loc_text = font.render("Local Game", True, 'white')
    screen.blit(loc_text, (350, 425))

    # Przycisk: Gra Sieciowa
    pygame.draw.rect(screen, 'black', [300, 520, 400, 80])
    pygame.draw.rect(screen, 'gold', [300, 520, 400, 80], 3)
    net_text = font.render("Online Multiplayer", True, 'white')
    screen.blit(net_text, (360, 545))

    pygame.display.flip()

def get_ip_screen():
    """Prosty ekran do wpisania adresu IP"""
    ip_text = "127.0.0.1"
    active = True
    
    while active:
        screen.fill('azure')
        title = big_font.render("Enter Server IP:", True, 'black')
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 300))
        
        # Pole tekstowe
        pygame.draw.rect(screen, 'white', [300, 400, 400, 60])
        pygame.draw.rect(screen, 'black', [300, 400, 400, 60], 3)
        ip_render = font.render(ip_text, True, 'black')
        screen.blit(ip_render, (310, 415))
        
        info = font.render("Press ENTER to connect", True, 'gray')
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 500))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return ip_text
                elif event.key == pygame.K_BACKSPACE:
                    ip_text = ip_text[:-1]
                else:
                    # Dodaj literę/cyfrę do IP (limit 15 znaków dla IPv4)
                    if len(ip_text) < 15:
                        ip_text += event.unicode

def main_menu():
    run = True
    while run:
        timer.tick(fps)
        draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                
                # Kliknięcie w Local Game
                if 300 <= x <= 700 and 400 <= y <= 480:
                    local_main()  # Uruchamia tryb lokalny
                    # Po zakończeniu gry lokalnej (return) wróci do pętli menu
                    
                # Kliknięcie w Online Multiplayer
                if 300 <= x <= 700 and 520 <= y <= 600:
                    ip_address = get_ip_screen() # Pobiera IP
                    if ip_address:
                        client_run(ip_address) # Uruchamia klienta
                        # Po zakończeniu gry sieciowej wróci do menu

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()