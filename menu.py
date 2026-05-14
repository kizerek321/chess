import pygame
import sys
import socket
import json
import time
import threading

from constants import screen, fps, timer, big_font, font, HEIGHT, WIDTH
from local_game import local_main
from multiplayer_game import client_run



discovered_servers = {}

def listen_for_servers():
    """Background thread listening for UDP packets from servers"""
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # SO_REUSEADDR allows for many clients on a single pc
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        udp_sock.bind(('', 8001))
    except Exception:
        pass #socket occupied
        
    udp_sock.settimeout(0.5)
    
    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            server_info = json.loads(data.decode('utf-8'))
            #save server with acctual time
            server_info['last_seen'] = time.time()
            server_key = f"{server_info['ip']}:{server_info['port']}"
            discovered_servers[server_key] = server_info
        except socket.timeout:
            pass
        except Exception:
            pass

#Listen in the background after start
udp_listener_thread = threading.Thread(target=listen_for_servers, daemon=True)
udp_listener_thread.start()

def draw_menu():
    screen.fill('azure')
    
    title = big_font.render("CHESS MULTIPLAYER", True, 'black')
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
    
    #button - local game
    pygame.draw.rect(screen, 'black', [300, 400, 400, 80])
    pygame.draw.rect(screen, 'gold', [300, 400, 400, 80], 3)
    loc_text = font.render("Local Game", True, 'white')
    screen.blit(loc_text, (350, 425))

    #button - multiplayer
    pygame.draw.rect(screen, 'black', [300, 520, 400, 80])
    pygame.draw.rect(screen, 'gold', [300, 520, 400, 80], 3)
    net_text = font.render("Browse Servers (LAN)", True, 'white')
    screen.blit(net_text, (350, 545))

    pygame.display.flip()

def server_browser_screen():
    run = True
    while run:
        screen.fill('azure')
        title = big_font.render("Available LAN Servers", True, 'black')
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        current_time = time.time()
        active_servers = [s for s in discovered_servers.values() if current_time - s['last_seen'] < 3]
        
        y_offset = 150
        rects = []
        
        if not active_servers:
            info = font.render("Searching for servers...", True, 'gray')
            screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 200))
        else:
            for srv in active_servers:
                rect = pygame.Rect(200, y_offset, 600, 60)
                pygame.draw.rect(screen, 'white', rect)
                pygame.draw.rect(screen, 'black', rect, 3)
                
                text = f"{srv['name']} - Players: {srv['players']}/2"
                render_text = font.render(text, True, 'black')
                screen.blit(render_text, (220, y_offset + 15))
                
                rects.append((rect, srv['ip'], srv['port']))
                y_offset += 80
                
        info_back = font.render("Press ESC to return", True, 'black')
        screen.blit(info_back, (WIDTH // 2 - info_back.get_width() // 2, HEIGHT - 100))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                for rect, ip, port in rects:
                    if rect.collidepoint(x, y):
                        return ip, port


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
                
                #click into local game
                if 300 <= x <= 700 and 400 <= y <= 480:
                    local_main()  #run local
                    #should come back to menu
                    
                #click into multi
                if 300 <= x <= 700 and 520 <= y <= 600:
                    result = server_browser_screen() #get ip
                    if result:
                        ip_address, port = result
                        client_run(ip_address, port) #run client
                        #should come back to menu

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()