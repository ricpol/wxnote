.. index:: 
   single: sizer

.. _sizer_basi:

I sizer: le basi da sapere.
===========================

Questa pagina tratta le cose fondamentali da sapere sui sizer, e descrive ``wx.BoxSizer``, il più semplice dei sizer disponibili in wxPython. I sizer più complessi sono descritti :ref:`in una pagina separata <sizer_avanzati>`. Inoltre, per usare i sizer occorre anche avere un'idea di come si specificano le dimensioni dei widget, argomento che affrontiamo :ref:`a parte <dimensioni>`.

.. index:: 
   single: posizionamento assoluto

Non usate il posizionamento assoluto.
-------------------------------------

In molti esempi brevi di queste note, per semplicità, facciamo uso del posizionamento assoluto, ossia specifichiamo direttamente la posizione (in pixel) del widget rispetto al suo parent, al momento della creazione, passando il parametro ``pos`` (ed eventualmente anche ``size`` per specificare la dimensione)::

    button = wx.Button(self, -1, 'clic me', pos=(10, 10))
    
Il posizionamento assoluto è più rapido, ma non dovrebbe mai essere usato in un programma "serio". E questo per almeno due valide ragioni:

* se l'utente vuole ridimensionare la finestra, i widget non scalano di conseguenza, e si crea dello spazio vuoto, oppure appaiono le barre di scorrimento. Questo problema di usabilità generalmente non è più tollerato nelle interfacce moderne;

* il posizionamento assoluto vi costringe a calcolare esattamente posizione e dimensione di ogni singolo elemento dell'interfaccia. Finché lo fate la prima volta va ancora bene, ma se in seguito volete aggiungere o togliere qualcosa, vi tocca ricalcolare tutto daccapo. 

Questo secondo problema si "risolve" in genere usando i RAD. In effetti, l'accoppiata RAD-posizionamento assoluto è un cavallo di battaglia di certi ambienti di programmazione... molto anni '90 di cui sicuramente avete sentito parlare. Abbiamo già scritto :ref:`che i RAD non vanno usati <non_usare>`, e adesso possiamo aggiungere un motivo: incoraggiano il posizionamento assoluto.


Usate i sizer, invece.
----------------------

wxPython supporta, come abbiamo visto, anche il posizionamento assoluto. Ma il modo consigliato di organizzare il layout di una finestra sono invece i sizer. 

I sizer costituiscono ormai, e non solo in wxPython, la soluzione standard ai due problemi che abbiamo appena visto:

* ri-calcolano la dimensione di tutti i widget man mano che l'utente ridimensiona la finestra, in modo che il contenuto sia sempre proporzionato al contenitore;

* inserire o togliere elementi in un secondo momento diventa banale: siccome è il sizer a occuparsi di calcolare posizioni e dimensione, voi dovete solo dirgli che cosa c'è. 

Lo svantaggio dei sizer è che richiedono parecchie righe di codice in più (bisogna dire al sizer che cosa includere e come, elemento per elemento), e che sono un po' più difficili da imparare. Inoltre, per i layout più complessi, pensare in termini di sizer può diventare complicato. 

Tuttavia, con un po' di pratica, i vantaggi superano ben presto gli svantaggi. Non a caso i sizer sono diventati praticamente onnipresenti nel mondo wxPython e non solo.

.. index:: 
   single: sizer; SetSizer
   single: wx; Sizer()
   single: wx.Window; SetSizer()

Che cosa è un sizer.
--------------------

In wxPython esistono diversi tipi di sizer, tutti derivati dalla classe-madre ``wx.Sizer`` (che però è un genitore astratto, che non deve mai essere usato direttamente). 

``wx.Sizer`` non deriva da ``wx.Window`` perché, semplicemente, un sizer non si deve vedere; e non deriva da ``wx.EvtHandler`` perché non ha bisogno di reagire agli eventi. Un sizer rappresenta semplicemente un algoritmo per disporre i widget in un contenitore. 

Si può applicare un sizer a un frame o a un dialogo/panel, anche se è molto più frequente vederlo applicato a un panel, perché il panel è lo sfondo ideale su cui disporre i widget, :ref:`come abbiamo visto parlando dei contenitori <contenitori>`. 

Il processo di lavoro è comune a tutti i tipi di sizer:

* prima si crea (istanzia) il sizer;
* poi si usa ripetutamente il metodo ``Add`` per aggiungere elementi al sizer. Possono essere aggiunti in questo modo sia widget, sia altri sizer (che a loro volta contengono widget e/o sizer);
* infine, si usa il metodo ``SetSizer`` per attribuire il sizer così organizzato al suo contenitore;
* come opzione ulteriore, è possibile :ref:`usare il metodo <fit_layout>` ``Fit`` per dire al sizer di adattare la sua dimensione a quella degli elementi che contiene. 

.. index:: 
   single: sizer; BoxSizer
   single: wx; BoxSizer()
   single: wx; HORIZONTAL
   single: wx; VERTICAL
   
``wx.BoxSizer``: il modello più semplice. 
-----------------------------------------

Il più semplice sizer che potete usare è il ``wx.BoxSizer``. Questo sizer organizza i widget in colonna, uno sotto l'altro, oppure in riga, uno accanto all'altro. 

Al momento di crearlo, dovete specificare la **direzione** lungo la quale si sviluppa il sizer. Se scrivete::

    sizer = wx.BoxSizer(wx.HORIZONTAL) # default

il BoxSizer si svilupperà in senso orizzontale, allineando i suoi elementi uno accanto all'altro. Se invece scrivete::

    sizer = wx.BoxSizer(wx.VERTICAL)

il sizer impilerà i suoi elementi uno sopra l'altro. 

Una volta che il sizer è stato creato, usate ``Add`` per aggiungere un nuovo elemento sotto gli altri (se il sizer è verticale) o a destra degli altri (se è orizzontale). Potete aggiungere quanti elementi desiderate. Per esempio, per aggiungere un pulsante che avete creato in precedenza, scrivete::

    sizer.Add(my_button)
    
.. Note:: Inoltre, ci sono alcuni altri metodi che più raramente possono esservi utili. ``sizer.GetOrientation()`` vi restituisce l'orientamento del sizer. ``AddMany`` permette di inserire più elementi alla volta. ``Prepend`` vi consente di inserire un elemento all'inizio del sizer, invece che alla fine. ``Insert`` inserisce un elemento tra altri due. ``Remove`` rimuove un elemento e lo distrugge, ``Detach`` lo rimuove senza distruggerlo, ``Replace`` lo sostituisce con un altro. Potete consultare la documentazione per scoprire esattamente come funzionano. Non vi consigliamo di fare uso frequente di queste tecniche, tuttavia. 

.. index:: 
   single: sizer; Add
   single: wx.Sizer; Add()
   
``Add`` in dettaglio.
---------------------

Il metodo ``Add`` di un sizer richiede un argomento obbligatorio (il widget che bisogna aggiungere) e altri 3 facoltativi. Esaminiamoli nel dettaglio. 


L'argomento ``proportion`` di ``Add``.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Il secondo argomento è ``proportion``, un numero intero che indica la *proporzione*. La proporzione fa sempre riferimento alla direzione (orizzontale o verticale) del sizer. Se la proporzione è 0, allora il widget, lungo quella direzione, occuperà solo lo spazio che gli compete (il suo "best size" naturale, oppure quello che avete impostato voi in qualche modo). Tutti i widget con proporzione nulla occuperanno solo lo spazio di cui hanno effettivamente bisogno. Tutti i widget con proporzione superiore a 0, invece, competeranno per occupare lo spazio eventualmente rimanente, in maniera proporzionale alla loro... proporzione, appunto. 

In altri termini, se un sizer contiene tre widget, con proporzione 0, 1, e 2 rispettivamente, allora il primo occuperà lo spazio di cui ha bisogno, e lo spazio rimanente sarà diviso tra gli altri due: il secondo ne occuperà un terzo, e l'ultimo si prenderà i due terzi restanti. Tutto questo, non dimentichiamolo, soltanto lungo la direzione "principale" del sizer. Ecco il codice che illustra questo esempio::

    class TopFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            p = wx.Panel(self)
            sizer = wx.BoxSizer(wx.VERTICAL)  # la direzione e' verticale
            sizer.Add(wx.Button(p), 0)
            sizer.Add(wx.Button(p), 1)
            sizer.Add(wx.Button(p), 2)
            p.SetSizer(sizer)
            

    app = wx.App(False)
    TopFrame(None).Show()
    app.MainLoop()

Notate che tutte le volte che ridimensionate la finestra cambiano anche le dimensioni dei pulsanti, ma il secondo e il terzo occuperanno sempre lo spazio restante in proporzione 2:1, mentre le dimensioni del primo pulsante non cambieranno mai. Notate anche che i pulsanti si contendono soltanto lo spazio nella direzione verticale (ossia la direzione del sizer), mentre in orizzontale ciascuno mantiene sempre lo stesso "best size". 


L'argomento ``flag`` di ``Add``.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Il terzo argomento di ``wx.Sizer.Add`` è ``flag``, ed è una bitmask come quelle che abbiamo già visto :ref:`parlando degli stili <stili>`. In questa bitmask possono rientrare due indicazioni molto differenti tra loro:

* primo, come allineare i widget, rispetto agli altri, e/o definirne le dimensioni;

* secondo, se lasciare dello spazio vuoto come bordo intorno al widget. 

Il primo aspetto è complicato. Potete scegliere tra varie opzioni:

* uno dei possibili ``wx.ALIGN_*`` (``*TOP``, ``*BOTTOM``, etc.) mantengono l'allineamento dei widget rispetto agli altri del sizer. Questo in molti casi ha senso solo se il widget ha priorità nulla;

* ``wx.FIXED_MINSIZE`` mantiene sempre le dimensioni minime del widget (e si può abbinare con uno degli allineamenti appena visti);

* ``wx.EXPAND`` o il suo sinonimo ``wx.GROW`` forzano il widget a occupare tutto lo spazio disponibile *lungo la dimensione "secondaria" del sizer* (chiariremo meglio questo punto tra poco);

* ``wx.SHAPED`` è come ``wx.EXPAND``, ma forza il widget a mantenere le proporzioni originarie. 

Un chiarimento importante riguardo a ``wx.EXPAND``. Questo flag forza il widget a espandersi lungo la direzione *secondaria* del sizer. Per contro, dare al widget una priorità superiore a 0 lo costringe a espandersi lungo la direzione *principale*, come abbiamo visto. Quindi se il widget ha sia priorità superiore a 0, sia il flag ``wx.EXPAND``, riempirà lo spazio disponibile in entrambe le direzioni. 

In generale, dovete chiedervi in quale direzione ha senso far espandere i vostri widget. Per esempio, in un sizer verticale, in genere i widget "multilinea" (liste, etc.) dovrebbero espandersi in entrambe le direzioni, mentre gli altri (caselle di testo, combobox...) potrebbero espandersi solo nella direzione secondaria. Infine, altri ancora (pulsanti, spin...) non dovrebbero espandersi per nulla::

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(wx.TextCtrl(...), 0, wx.EXPAND) # cresce solo in orizzontale
    sizer.Add(wx.ListBox(...), 1, wx.EXPAND)  # cresce in entrambe le direzioni
    sizer.Add(wx.Button(...), 0, wx.ALIGN_CENTER_HORIZONTAL) # non cresce
    
Quando al secondo punto, potete indicare una combinazione qualsiasi di ``wx.RIGHT``, ``wx.LEFT``, ``wx.TOP``, ``wx.BOTTOM`` oppure ``wx.ALL`` (che li comprende tutti) per indicare su quali lati volete che sia lasciato il bordo. 


L'argomento ``border`` di ``Add``.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Il quarto argomento di ``Add`` è anche il più semplice. Se nella bitmask del ``flag`` avete specificato che volete del bordo, indicate qui la dimensione del bordo, in pixel. 
Non è possibile specificare bordi di differente ampiezza su lati diversi. 

.. index:: 
   single: wx.Sizer; AddStretchSpacer()
   
Aggiungere uno spazio vuoto.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Add`` può essere usato anche per inserire uno spazio vuoto tra due widget. Basta passare il numero dei pixel da lasciare vuoti in una tupla (in realtà, un'istanza di ``wx.Size``, come vediamo :ref:`nella pagina dedicata <dimensioni>`). Siccome in genere vi interessa specificare solo lo spazio da lasciare lungo la direzione principale del sizer, potete passare ``-1`` per l'altra direzione. Per esempio::

    sizer = wx.Sizer(wx.VERTICAL)
    sizer.Add(wx.Button(...), 0, wx.ALL, 5)
    sizer.Add((-1, 10))   # uno spazio di 10 pixel in verticale
    sizer.Add(wx.Button(...), 0, wx.ALL, 5)

I due widget saranno così separati da 20 pixel di spazio (contanto anche i bordi). 

Notate che uno "spazio vuoto" si comporta esattamente come gli altri widget, e quindi può essere inserito con un flag e una proporzione. In particolare, è molto frequente l'idioma ``Add((-1, -1), 1, wx.EXPAND)``, che aggiunge uno spazio indeterminato che si allarga quando ridimensioniamo la finestra. Provate questo "trucco", che mantiene i widget nel centro della finestra::

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add((-1, -1), 1, wx.EXPAND)
    sizer.Add(wx.Button(...), 0, wx.EXPAND)
    sizer.Add(wx.Button(...), 0, wx.EXPAND)
    sizer.Add((-1, -1), 1, wx.EXPAND)
    
L'idioma è abbastanza comune da aver meritato la creazione di un metodo apposito ``sizer.AddStretchSpacer()`` per riassumerlo.

