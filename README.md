# Simulazione Rete: DHCP, DNS, HTTPS

Script Python didattico che simula, in un unico processo multi-thread, i passaggi fondamentali di una comunicazione di rete:

1. **DHCP** – assegnazione simulata di un indirizzo IP al client.
2. **DNS** – un server UDP locale risolve il dominio `www.mioesercizio.local` nell'IP del server.
3. **HTTPS** – un server HTTP viene avvolto in un layer SSL/TLS e il client effettua una richiesta GET cifrata.

## Requisiti

- Python 3
- Un certificato TLS in formato PEM chiamato `server.pem` nella cartella del progetto (chiave privata + certificato concatenati).

Per generarne uno autofirmato per i test:

```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=www.mioesercizio.local"
cat key.pem cert.pem > server.pem
```

## Esecuzione

```bash
python simulazione_rete.py
```

Lo script avvia il server DNS e il server HTTPS su thread separati, poi esegue il client che:

- simula la richiesta DHCP,
- interroga il DNS,
- apre una connessione HTTPS verso il server e stampa la risposta ricevuta.
