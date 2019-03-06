# ![](https://raw.githubusercontent.com/francibm97/slidenotes/master/slidenotes/static/favicon/favicon-32x32.png) Slidenotes
![POSTSCRIPT](https://img.shields.io/badge/PostScript-2-red.svg)
![PYTHON 3.6](https://img.shields.io/badge/Python-3.6-blue.svg)
![AGPL v3](https://img.shields.io/badge/License-AGPL_v3-green.svg)

Slidenotes è un piccolo programma, una sorta di prototipo basato su [GhostScript](https://www.ghostscript.com/),
che serve per impaginare secondo una disposizione più efficace le diapositive in PDF fornite dai docenti universitari.

Per maggiori informazioni e per una demo funzionante, si può consultare direttamente [slidenotes.app](https://slidenotes.app).

## Descrizione generale del codice sorgente
### Backend in PostScript
Il nucleo fondamentale è costituito da [alcuni script](https://github.com/francibm97/slidenotes/tree/master/slidenotes/gs)
scritti in PostScript, un linguaggio di programmazione proposto da Adobe e utilizzato per la descrizione di documenti.
GhostScript è un programma diffusissimo e in grado di interpretare e convertire file in formato PDF o PostScript; la sezione stessa
di quel programma che interpreta i PDF è scritta in PostScript.
Quindi GhostScript, interpretando gli script in PostScript di questo programma, elabora e modifica il PDF in ingresso contenente le 
diapositive e produce in uscita un nuovo PDF contenente da una a tre diapositive per foglio disposte sul lato sinistro.

In particolare:
 - __slidenotes_include.ps__, che viene richiamato dagli script successivi, contiene alcune funzioni di libreria di GhostScript 
 leggermente modificate che servono per l'interpretazione dei pdf 
 - __slidenotes-strings.ps__ contiene alcune funzioni per la manipolazione di stringe Unicode contenute nei metadati dei PDF
 - __slidenotes_impose.ps__ è lo script fondamentale, quello che effettua l'impaginazione
 - __slidenotes_cut_in_half.ps__ è quello script che viene richiamato quando il PDF in ingresso contiene due slide per pagina:
 per ogni pagina, lui dice a GhostScript di produrne due, una ricavata dalla metà superiore del foglio e una dalla metà inferiore.
 Così facendo però si ottiene molto spazio bianco attorno alle diapositive, perchè queste sono sempre un po' più piccole della metà
 del foglio, e la loro posizione precisa varia da PDF a PDF (in genere questi PDF vengono prodotti con PowerPoint).
 Di conseguenza, quando si usa questo script, a GhostScript non si specifica `pdfwrite` come dispositivo di output, perché non
 si vuole ottenere un PDF, ma si seleziona il dispostivo di test `bbox`, che restituisce per ogni pagina le coordinate del rettangolo
 in cui sono effettivamente presenti scritte e immagini: in questa maniera si possono ottenere le coordinate precise di ogni diapositiva.
 
### Backend in Python
Teoricamente basterebbero i file indicati sopra per convertire i PDF. Ad esempio, per convertire la maggior parte dei PDF, ottenendo
tre slide per pagina, basta inserire nella shell
`gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sFILE=input.pdf -sOutputFile=output.pdf slidenotes_impose.ps`.
(Tutti i file slidenote_*.ps devono essere nella current working directory e deve essere stato installato ghostscript).
Dato che una soluzione web, oltre a essere molto più comoda, è l'unica via possibile se si vogliono convertire slide usando computer
su cui non è possibile installare ghostscript, come quelli del centro stampa, ho scritto un piccolo backend in python che si occupa
di automatizzare alcuni processi.
Questo non è scritto da zero ma si basa principalmente su
 - flask, libreria python per la gestione del server applicativo
 - celery, libreria python per la gestione delle conversioni in background
 
### Frontend
Per il frontend ho utilizzato la grafica di [https://designrevision.com/downloads/shards/](https://designrevision.com/downloads/shards/)

## Istruzioni per l'installazione
Le istruzioni sono valide per Ubuntu Server 18.04. Slidenotes dovrebbe funzionare su ogni distribuzione linux ma non è stato testato
né su windows né su macos.

Innanzitutto installare le varie dipendenze:

    sudo apt install ghostscript python3 python3-pip rabbitmq-server
    
Installare virtualenv:

    sudo pip3 install virtualenv

Clonare questo repository nella propria home:

    cd ~ && git clone https://github.com/francibm97/slidenotes

Creare un ambiente virtuale python nella propria home:

    virtualenv -p python3 ~/slidenotes_venv

Attivare l'ambiente virtuale:

    . ~/slidenotes_venv/bin/activate
    
Dopo aver dato il comando precedente, il prompt della shell dovrebbe iniziare con (slidenotes_venv).

Installare quindi dentro l'ambiente virtuale le librerie di python:

    cd ~/slidenotes && pip3 install -r requirements.txt
    
## Esecuzione

Innanzitutto avviare rabbitmq (teoricamente dovrebbe già essere attivo):

    sudo systemctl start rabbitmq-server

Aprire due nuove shell e in ciascuna di esse attivare l'ambiente virtuale e spostarsi nella cartella del progetto,
eseguendo in entrambe:

    . ~/slidenotes_venv/bin/activate
    cd ~/slidenotes
    
Nella prima shell far partire celery, grazie a cui sarà effettuata la conversione dei pdf in background:

    celery -A slidenotes.celery worker
    
Nella seconda shell far partire il server applicativo

    python3 run.py
    
A questo punto su http://localhost:5000 sarà possibile utilizzare slidenotes.
