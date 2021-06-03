'''
Davide Denicolò
N° matricola 0000879677
Traccia Numero 2 Progetto di Programmazione a oggetti.
Si immagini di dover realizzare un Web Server in Python per
una azienda ospedaliera. I requisiti del Web Server sono i
seguenti:
• Il web server deve consentire l’accesso a più utenti in contemporanea
• La pagina iniziale deve consentire di visualizzare la lista
dei servizi erogati dall’azienda ospedaliera e per ogni
servizio avere un link di riferimento ad una pagina
dedicata.
• L’interruzione da tastiera (o da console) dell’esecuzione
del web server deve essere opportunamente gestita in
modo da liberare la risorsa socket.
• Nella pagina principale dovrà anche essere presente un
link per il download di un file pdf da parte del browser
• Come requisito facoltativo si chiede di autenticare gli
utenti nella fase iniziale della connessione.
'''


import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime
import pytz
import feedparser

#Creazione dell'Handler per gestire le richieste GET dal client.
class Serv(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            if self.path == '/notizie.html':
                feed_creator()
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            print("E' arrivata una richiesta al server")
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))


# Indica la porta ove lavorare, di default sarà la 8081.
if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8081


#Varie variabili HTML.
footer = """
    </body>
</html>
"""

header_html = """
<html>
    <head>
        <style>
            h1 {
                text-align: center;
                margin: 0;
            }
            p {
                text-align: center;
            }
            td {
                text-align: center;
                padding: 25px;
            }
            .nav {
  		        overflow: hidden;
  		        color: white;
  		        background-color: gray;
  		    }
        </style>
    </head>
    <body>
        <title>Sezione notizie salute</title>
"""

navigation_bar = """
<meta charset="UTF-8">
<meta http-equiv="Content-type" content="text/html; charset=UTF-8">

        <br>
        <br>
        <br>
        <br><br>
        <table align="center">
""".format(port=port)


#Funzione che mi permette di aggiungere le informazioni riguardo a un singolo RSS in una variabile messaggio.
#Ci andrò poi ad aggiungere dei tag html poiche finirà in un file HTML apposito.
def add_element(i, message, title, desc, link, info):
    if i == 0:
        now_italy = pytz.timezone('Europe/Rome')
        current_time = datetime.now(now_italy)
        message = "<h1>" + current_time.strftime("%H:%M:%S") + "<h1>"
    message = message \
              + "<br><h1>" + title + "</h1><br>" \
              + "<p>" + desc + "<br>" \
              + "<a href=" + link + ">" + link + "</a><br>" \
              + info + "</p><br>"
    return message


#Creo ufficialmente la pagina che espone le notizie.
def home_creator(message):
    f = open('notizie.html', 'w', encoding="utf-8")
    f.write(header_html + "<br><br><h1> <div class=""nav""> Notizie | <a href="'index.html'"> Home </a></div></h1>"
            + navigation_bar + "</table>" + message + footer)
    f.close()
    
#Funzione che permette di prendere le RSS dal corriere
#Mano a mano che leggo le notizie le formatto in un formato HTML e le scrivo sul file html Notizie.html.
def feed_creator():
    feed = feedparser.parse("https://xml2.corriereobjects.it/rss/salute.xml")

    message = ''
    i = 0
    for entry in feed.entries:
        article_title = entry.title
        article_desc = entry.description
        article_link = entry.link
        article_info = entry.category

        message = add_element(i, message, article_title, article_desc, article_link, article_info)
        if i == 0:
            i += 1

    f = open('notizie.html', 'w', encoding="utf-8")
    f.write(message)
    f.close()

    home_creator(message)

#Gestione del segnale di uscita, quando si preme CTRL-C si deallocheranno le risorse.
def signal_handler(signal, frame):
    print('Exiting http server (Ctrl+C pressed)')
    try:
        if server:
            server.server_close()
    finally:
        sys.exit(0)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Gestisco le richieste in un altro thread."""

#Eseguo il main.
if __name__ == '__main__':
    server = ThreadedHTTPServer(('localhost', port), Serv)
    print('Starting server, use <Ctrl-C> to stop')
    signal.signal(signal.SIGINT, signal_handler)
    feed_creator()
    server.serve_forever()






