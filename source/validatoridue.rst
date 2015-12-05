.. highlight:: python
   :linenothreshold: 15

.. _validatoridue:

.. index::
   single: validatore; validazione automatica
   single: validatore; trasferimento dati
   single: wx.PyValidator; TransferToWindow
   single: wx.PyValidator; TransferFromWindow
   single: validatore; wx.PyValidator.TransferToWindow
   single: validatore; wx.PyValidator.TransferFromWindow
   
Validatori: seconda parte.
============================

.. todo:: una pagina su MCV con molti riferimenti a questa.

Nella :ref:`prima parte <validatori>` di questa analisi, abbiamo parlato dell'uso più naturale dei validatori: convalidare i dati immessi dall'utente. Abbiamo visto che i validatori si inseriscono in un delicato momento della vita della vostra applicazione, quando dovete trasformare i dati "grezzi" inseriti dall'utente nella gui, in dati "puri" (validi, consolidati) nel vostro "model" e, in ultima analisi, nel vostro database o altro sistema di storage permanente. 

I validatori cercano di offrire un servizio completo, per questa fase di lavoro. Non si limitano a convalidare i dati, ma, se volete, si occupano anche di trasferirli avanti e indietro tra il "model" e l'interfaccia grafica. 


Trasferimento dati nei dialoghi con validazione automatica.
-----------------------------------------------------------

Il modo più semplice per illustrare questa possibilità, è vederla applicata nel suo ambiente naturale, dove i validatori danno il meglio di sé: i dialoghi con validazione automatica. 

Per questo motivo abbiamo ampliato l'esempio dei "nomi e cognomi" che abbiamo seguito fin qui, fino a trasformarlo in una applicazione vera e propria, anche se piccola. Il codice è più lungo, ma vale la pena di seguirlo per vedere come i validatori si integrano nella vita di un'applicazione nel mondo reale (o quasi). 

Il nostro programma consente di vedere, modificare e aggiungere dei nomi a un database. Quando fate doppio clic su un nome della lista, il dialogo si apre in modalità "modifica", e quando cliccate sul pulsante "nuovo", lo stesso dialogo vi consente di aggiungere un nuovo elemento. 

.. literalinclude:: /_static/snippets/validator_data_trasfert.py
   :lines: 5-
   :linenos:

Per cominciare, alcune spiegazioni che non riguardano i validatori. Per non scrivere troppo codice "fuori tema", abbiamo dovuto fare un bel po' di semplificazioni: il "database" è in realtà un dizionario ``PEOPLE`` inizializzato alla riga 134. :ref:`Abbiamo visto altrove <wxapp_avanzata>` che un posto intelligente per inizializzare la connessione al database è ``wx.App.OnInit``, e quindi seguiamo questa strada: immaginate soltanto che il dizionario ``PEOPLE`` sia in realtà una connessione aperta, o un riferimento a un ORM. 

La nostra finestra principale ``TopFrame`` ha semplicemente una lista di tutte le persone, e un pulsante per aggiungerne di nuove. Il metodo ``reload_people_list`` (riga 98) si incarica di ricaricare la lista. Anche in questo caso, abbiamo semplificato molto: dovete immaginare una richiesta a un database e un processo di adattamento dei dati al formato di visualizzazione. 

Quando l'utente fa doppio clic su un nome, la nostra semplificazione sconfina nell'errore vero e proprio (riga 111): qui estraiamo l'id della persona selezionata direttamente dalla stringa di testo visualizzata nella lista. Che brutto! Ovviamente non fate mai cose del genere nel mondo reale. Dovreste avere un "model" di qualche tipo collegato alla "view" della lista, e quindi chiedere al "model" quale oggetto-persona corrisponde alla riga selezionata. 

L'id così malamente ricavato ci serve per chiedere al "database" i dati necessari della persona selezionata (riga 112), che vengono memorizzati nella variabile ``self.current_person``. Questo è più simile a ciò che avverrebbe nel mondo reale, in effetti. 

Dopo di che, entra in gioco il ``PersonDialog`` che è il cuore della nostra applicazione, e che esaminiamo nel dettaglio tra poco. Iniziamo però a notare che ``PersonDialog``, in qualche modo per ora misterioso, ha la facoltà di modificare il valore di ``self.current_person``. E quindi, se l'utente ha chiuso il dialogo con ``wx.ID_OK``, a noi non resta che aggiornare il database con il ``self.current_person`` modificato, e quindi chiamare ``reload_people_list`` per aggiornare la lista mostrata (righe 115-117). 

Se invece l'utente fa clic sul pulsante "nuovo", la procedura è identica, salvo che adesso ``self.current_person`` è ovviamente un dizionario vuoto (riga 121). Di nuovo, quando l'utente chiude il dialogo, a noi non resta che aggiornare il database e rinfrescare la lista. L'unica piccola variante è che questa volta dobbiamo calcolarci un nuovo id per il database (riga 126: questo ovviamente nel mondo reale non sarebbe necessario... i database sanno regolarsi da soli). 

Il dialogo ``PersonDialog``, a prima vista sembra completamente magico. Ha solo un ``__init__`` per disegnare la gui, ma non si vede nessun codice per gestire tutte le operazioni di cui è incaricato. Parte della magia, ormai, dovrebbe essere chiara: alle righe 60 e 61 creiamo due pulsanti con Id predefiniti, che si occupano di chiudere il dialogo, e (il pulsante "conferma") di validare i dati. Se non vi è chiaro perché, rileggete :ref:`la prima parte <validatori_validazioneautomatica>` di questa analisi, e anche :ref:`la pagina sugli Id <idpredefiniti>`. 

Ma la vera magia sta nei validatori. Ciascun widget del nostro dialogo ha un validatore assegnato (righe 54-59). Incidentalmente, notate che ``wx.SpinCtrl`` non prevede un paramentro ``validator`` nel suo costruttore, e quindi dobbiamo assegnare il validatore in un secondo momento, usando ``SetValidator``. 

E finalmente esaminiamo i due validatori che abbiamo scritto. ``NotEmptyValidator`` si applica alle due caselle di testo, e il suo metodo ``Validate`` fa quello a cui siamo già abituati: blocca tutto se la casella è vuota. 

La novità sono i due metodi per il trasferimento dei dati. Occorre prima di tutto capire che ``TransferToWindow`` viene invocato automaticamente quando il dialogo si apre. ``TransferFromWindow`` invece viene invocato quando il dialogo si chiude, ma solo in corrispondenza della pressione di ``wx.ID_OK`` (e naturalmente, solo a validazione avvenuta). 

Per poter trasferire i dati, il validatore deve avere qualche conoscenza del nostro "model". Ecco perché passiamo come argomenti ``person`` e ``key``. Il primo è collagato alla ``self.current_person`` della nostra finestra-madre (vedi riga 53), il secondo è il "campo" esatto a cui il widget è collegato (vedi righe 55 e 57). In questo modo il validatore conosce con precisione il valore su cui deve lavorare. 

All'apertura del dialogo, ``TransferToWindow`` si occupa di prelevare il valore alle coordinate "``person`` / ``key``" e di inserirlo nel widget (riga 11). Alla chiusura, ``TransferToWindow`` fa il lavoro opposto, prelevando il nuovo valore e modificando il ``self.current_person`` della finestra-madre (riga 16). La cosa importante da notare che è che, se il dato viene sovrascritto dal validatore, possiamo essere sicuri che è tutto è regolare, in quanto: primo, l'utente ha premuto ``wx.ID_OK``; secondo, la validazione è avvenuta con successo. 

A questo punto il validatore ha terminato il suo lavoro, e per un attimo nella finestra madre si verifica una inconsistenza tra il contenuto di ``self.current_person`` ormai modificato (il "controller"), e il valore riportato nella lista (la "view") e nel database (il "model"). E' infatti, non appena chiuso il dialogo (riga 115), la finestra madre si occupa immediatamente di aggiornare il database (riga 116) e la lista (riga 117). 

.. note:: Non potrebbe occuparsi il validatore di aggiornare anche il database? Se il validatore avesse conoscenza diretta del database (e non solo della ``current_person``) potrebbe ricavare i valori che gli servono da questo, e modificarli quando occorre. Nel nostro esempio, sarebbe naturalmente possibile. Ma nel mondo reale, c'è una ragione tecnica per non farlo: se ogni validatore fa una richiesta separata per ottenere il suo pezzetto di informazione, potete scommettere che l'amministratore del database avrà qualche obiezione (nel nostro esempio, sarebbero già 3 query in entrata e 3 in uscita). Tuttavia, se usate un ORM e siete in grado di ottimizzare le richieste in qualche modo, allora nessun problema. 

Comprendere questo flusso di gestione è fondamentale. Infatti vediamo come i validatori hanno favorito, sia pure in modo ancora embrionale, la separazione delle diverse funzioni, fino ad arrivare a una sorta di "model-controller-view". Nel nostro esempio, il model è ovviamente il database ``PEOPLE``. La view è la lista mostrata nella finesta madre. Il codice di controllo sta nel callback ``on_view_person`` (e in ``on_new`` ce n'è un'altro pressoché identico... andrebbero fattorizzati, ma li ho lasciati separati per semplicità). Il "controller" si occupa di rispondere agli eventi wxPython, e tenere sincronizzato il model con la view. 

La terza casella (l'età della nostra persona) è un ``wx.SpinCtrl``, e per quello abbiamo bisogno di un validatore separato: da un lato non avrebbe senso controllare se il campo è vuoto (un ``wx.SpinCtrl`` non è mai vuoto), e dall'altro abbiamo bisogno di controllare qualche dettaglio ulteriore. 

Il validatore che abbiamo assegnato, ``AgeValidator``, non fa in effetti nessuna validazione (riga 36), e si occupa solo del trasferimento dei dati, in maniera del tutto analoga all'altro validatore. Osservate però che, al momento di aprire il dialogo, si occupa anche di impostare minimo, massimo e valore di default per il ``wx.SpinCtrl`` affidato alla sua sorveglianza (righe 40-41). Nel nostro piccolo esempio questo avviene in un brutto modo "statico", ma non è difficile passare questi valori dinamicamente come parametri. Questo è un esempio di come si possono usare i validatori anche per lavorare con i controlli limitati, affrontando un problema che :ref:`avevamo visto nella prima parte <validatori_controllilimitati>`.


Trasferimento dati negli altri casi.
------------------------------------

La capacità dei validatori di trasferire dati può essere usata anche in un contesto di validazione "manuale". Se applicate un validatore a un widget, ``TransferToWindow`` sarà invocato automaticamente ogni volta che il widget viene mostrato. D'altra parte, dovrete invece chiamare direttamente ``TransferFromWindow`` per riottenere i dati indietro: naturalmente prima dovete assicurarvi di aver chiamato ``Validate`` per controllare che i dati siano giusti.


Conclusioni.
------------

La capacità dei validatori di gestire il flusso dei dati tra il "model" e l'interfaccia grafica, in aggiunta al loro utilizzo più comune per validare i dati, li rende uno strumento potenzialmente centrale nella vostra applicazione. Con i validatori potete automatizzare il flusso dei dati e separare le funzioni di controllo dal resto. 

:ref:`Come abbiamo visto nella prima parte <validatori_consigli>`, le difficoltà non mancano, ma spesso sono legate a una imperfetta comprensione di come funzionano davvero i validatori. Tuttavia, anche con le migliori intenzioni, talvota i validatori possono essere semplicemente scomodi da usare. Va detto che specialmente nel mondo Python, le capacità di automatizzazione dei validatori brillano di meno: spesso basta un ciclo ``for`` per applicare una routine di validazione a tutti i widget della zona, senza bisogno di ulteriori sovrastrutture. 

Tuttavia un utilizzo intelligente dei validatori indirizza verso la separazione tra "model", "controller" e "view", e quindi, se non li volete usare, dovreste comunque fare attenzione che il sistema con cui li rimpiazzate mantenga questo vantaggio. 

Ancora una osservazione: i validatori sono uno dei punti in cui wxPython non si limita a essere un puro "gui framework", ma sconfina nel campo di un "application framework". Non c'è nulla di male in questo, finché ne siete consapevoli. Se, per esempio, volete usare wxPython come front-end grafico "plugin" liberamente sostituibile con altre interfacce, allora probabilmente non vi conviene legare ai validatori il vostro codice di controllo. 

