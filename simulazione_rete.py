import http.server
import socket
import ssl
import threading
import time

# Costanti di configurazione
PORTA_DNS = 5053
PORTA_HTTPS = 4443
IP_SERVER = "127.0.0.1"
DOMINIO = "www.mioesercizio.local"


# ==========================================
# STEP 1: Simulazione DHCP
# ==========================================
def passaggio_dhcp():
    print("\n--- [STEP 1: DHCP] ---")
    print("[Client] Invio richiesta DHCP Discover...")
    time.sleep(0.5)
    print(f"[DHCP Server] Assegnato IP Client: 192.168.1.50")
    print(f"[DHCP Server] Configurato IP Server DNS: {IP_SERVER}")
    print("-----------------------\n")


# ==========================================
# STEP 2: Server DNS (Simulazione UDP)
# ==========================================
def avvia_server_dns():
    # Creiamo un socket UDP per il DNS
    sock_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_dns.bind((IP_SERVER, PORTA_DNS))

    print(f"[DNS Server] Attivo sulla porta {PORTA_DNS}...")

    while True:
        # Riceve la richiesta dal client
        dati, indirizzo = sock_dns.recvfrom(512)
        print(f"\n--- [STEP 2: DNS Request] ---")
        print(
            f"[DNS Server] Ricevuta richiesta di risoluzione per: '{DOMINIO}' da {indirizzo}"
        )

        # Simula una risposta DNS elementare (restituisce l'IP del server HTTPS)
        risposta = IP_SERVER.encode()
        sock_dns.sendto(risposta, indirizzo)
        print(f"[DNS Server] Risposto con IP: {IP_SERVER}")
        print("-----------------------------\n")


# ==========================================
# STEP 3: Server HTTPS
# ==========================================
def avvia_server_https():
    # Gestore delle richieste HTTP
    class GestoreSemplice(http.server.SimpleHTTPRequestHandler):

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            risposta_html = "<h1>Esercizio Completato! Connessione HTTPS Protetta e Funzionante.</h1>"
            self.wfile.write(risposta_html.encode("utf-8"))

    # Configurazione del server HTTP standard
    server_http = http.server.HTTPServer((IP_SERVER, PORTA_HTTPS), GestoreSemplice)

    # Avvolgiamo il server con il layer SSL/TLS (HTTPS)
    contesto_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    contesto_ssl.load_cert_chain(certfile="server.pem")
    server_http.socket = contesto_ssl.wrap_socket(
        server_http.socket, server_side=True
    )

    print(f"[HTTPS Server] Attivo in modo sicuro sulla porta {PORTA_HTTPS}...")
    server_http.serve_forever()


# ==========================================
# Client che esegue le richieste
# ==========================================
def esegui_client():
    time.sleep(2)  # Lasciamo il tempo ai server di avviarsi

    # 1. Ottiene IP dal DHCP
    passaggio_dhcp()

    # 2. Interroga il DNS per sapere l'IP di www.mioesercizio.local
    print("[Client] Chiedo al DNS l'IP di " + DOMINIO)
    sock_client_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_client_dns.sendto(DOMINIO.encode(), (IP_SERVER, PORTA_DNS))

    ip_risolto, _ = sock_client_dns.recvfrom(512)
    ip_risolto = ip_risolto.decode()
    print(f"[Client] DNS Risolto! L'IP di {DOMINIO} e' {ip_risolto}")

    # 3. Effettua la richiesta HTTPS (Simulata via Socket SSL per vedere l'handshake)
    print(f"\n--- [STEP 3: HTTPS Connection] ---")
    print(
        f"[Client] Inizio Handshake TCP/SSL verso {ip_risolto}:{PORTA_HTTPS}..."
    )

    contesto_client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Disabilitiamo la verifica del certificato solo perché è autofirmato per il test
    contesto_client.check_hostname = False
    contesto_client.verify_mode = ssl.CERT_NONE

    with socket.create_connection((ip_risolto, PORTA_HTTPS)) as sock_tcp:
        with contesto_client.wrap_socket(
            sock_tcp, server_hostname=DOMINIO
        ) as sock_ssl:
            print("[Client] Connessione SSL cifrata stabilita con successo!")

            # Invio richiesta HTTP GET
            richiesta_http = f"GET / HTTP/1.1\r\nHost: {DOMINIO}\r\nConnection: close\r\n\r\n"
            sock_ssl.sendall(richiesta_http.encode())

            # Ricezione risposta dal server
            risposta = sock_ssl.recv(1024).decode()
            print("\n[Client] Risposta ricevuta dal Server HTTPS:")
            print(risposta)
    print("----------------------------------\n")


# ==========================================
# Main: Avvio dei Thread
# ==========================================
if __name__ == "__main__":
    # Avviamo il Server DNS in un thread separato
    thread_dns = threading.Thread(target=avvia_server_dns, daemon=True)
    thread_dns.start()

    # Avviamo il Server HTTPS in un thread separato
    thread_https = threading.Thread(target=avvia_server_https, daemon=True)
    thread_https.start()

    # Avviamo il client nel thread principale
    esegui_client()
