.. _eccezioni2:

.. index:: 
   single: eccezioni; eccezioni wxPython


Gestione delle eccezioni in wxPython (2a parte).
================================================

Riprendiamo il discorso sulle eccezioni :ref:`da dove l'avevamo lasciato<eccezioni>`: dopo aver visto la difficile esistenza delle eccezioni Python nell'ecosistema wxPython, affrontiamo adesso lo stesso argomento dal punto di vista di wxPython stesso (o meglio, dell'architettura wxWidgets sottostante). 

La prima cosa da sapere al riguardo è che wxWidgets non utilizza le eccezioni per segnalare condizioni di errore. Questo perché le eccezioni sono state introdotte nel linguaggio C++ solo quando ormai wxWidgets era già un framework molto esteso e complesso. Lo sforzo di adattare wxWidgets alla nuova realtà è arrivato fino al punto di supportare l'utilizzo delle eccezioni nel codice client (ovvero, le applicazioni wxWidgets scritte in C++ possono usare le eccezioni). Ma al suo interno il framework ha continuato a utilizzare gli strumenti di cui si era nel frattempo dotato per la gestione degli errori. 


.. _pyassertionerror:

.. index:: 
   single: eccezioni; wx.PyAssertionError
   single: wx.PyAssertionError
   single: eccezioni; wx.App.SetAssertMode
   single: wx.App; SetAssertMode
   single: eccezioni; wx.App.GetAssertMode
   single: wx.App; GetAssertMode
   single: eccezioni; wx.PYAPP_ASSERT_*
   single: wx.PYAPP_ASSERT_*

``wx.PyAssertionError``: gli assert C++ tradotti in Python.
-----------------------------------------------------------

wxWidgets, per segnalare condizioni di errore, fa uso di una famiglia di `macro di debugging <http://docs.wxwidgets.org/trunk/group__group__funcmacro__debug.html>`_, la cui più importante è ``wxASSERT``. Non è questa la sede per esaminare il loro complesso funzionamento: la cosa importante dal nostro punto di vista è che ogni volta che il codice wxWidgets emette un assert, questo si trasmette al livello superiore wxPython sotto forma dell'eccezione ``wx.PyAssertionError``, che può quindi essere catturata in un normale blocco ``try/except``. 

A livello globale, questo meccanismo si può controllare con il metodo ``wx.App.SetAssertMode`` (e il suo corrispettivo ``wx.App.GetAssertMode``), che accetta questi possibili valori: ``wx.PYAPP_ASSERT_DIALOG``, ``wx.PYAPP_ASSERT_EXCEPTION`` (il default), ``wx.PYAPP_ASSERT_LOG`` e ``wx.PYAPP_ASSERT_SUPPRESS``, tutti dal significato piuttosto intuitivo. 

``wx.PyAssertionError`` è, in un certo senso, quanto di meglio wxPython può metterci a disposizione per sbirciare nel labirinto altrimenti inaccessibile del codice C++ sottostante. L'utilità di questo strumento, in ogni caso, è minore di quanto si potrebbe sperare. In primo luogo, non è facile scoprire quando una particolare routine C++ potrebbe innescare un assert: la documentazione di wxWidgets non è sempre così completa e accessibile. Ma più che altro, il problema è che non esiste una policy uniforme trasversale a tutto il codice wxWidget, su come e quando si dovrebbero usare gli assert. E' facile trovare incongruenze bizzarre. 

Facciamo un esempio concreto (uno tra i mille possibili) che abbiamo già introdotto :ref:`parlando di logging<wxlog_utile>`: che cosa succede quando proviamo a caricare una ``wx.Bitmap`` con un file inesistente?
::

    bmp = wx.Bitmap('non_esiste.bmp', type=wx.BITMAP_TYPE_ANY)  # (1)
    bmp = wx.Bitmap('non_esiste.bmp', type=wx.BITMAP_TYPE_BMP)  # (2)

La prima versione non produce un assert, ma :ref:`una scrittura di log<logging2>` (con ``wx.LogSysError`` che mostra un messaggio di errore all'utente). La seconda versione non produce né assert né scritture di log (!). In entrambi i casi la creazione dell'oggetto ``wx.Bitmap`` va comunque a buon fine: potete scoprire solo a posteriori che c'è un problema, testando ``wx.Bitmap.IsOk`` (che in entrambi i casi restituisce ``False``).

Ma non è finita. Se il costruttore di ``wx.Bitmap`` non usa gli assert, d'altra parte ci sono molte api che invece testano ``wx.Bitmap.IsOk`` ed emettono assert se qualcosa non va. Per esempio, proviamo a usare una ``wx.Bitmap`` per produrre una ``wx.Mask``::

    bmp = wx.Bitmap('non_esiste.bmp', type=wx.BITMAP_TYPE_BMP)
    mask = wx.Mask(bmp, wx.RED)

Quando istanziamo la ``wx.Mask``, il costruttore C++ emette un assert che viene tradotto in un ``wx.PyAssertionError``, che volendo possiamo intercettare. 

D'altra parte, se invece usiamo la nostra ``wx.Bitmap`` malformata per creare un ``wx.BitmapButton``, l'operazione fallisce silenziosamente, senza che nessun assert venga emesso, e ci viene mostrato un normale pulsante senza nessuna immagine:

    bmp = wx.Bitmap('non_esiste.bmp', type=wx.BITMAP_TYPE_BMP)
    button = wx.BitmapButton(self, bitmap=bmp)

E ancora: proviamo adesso a usare la nostra ``wx.Bitmap`` per creare il pulsante di una ``wx.ToolBar``. Al momento di aggiungere il tool (con ``wx.ToolBar.AddTool``), niente accade. Quando però finalizziamo la creazione della toolbar (``wx.ToolBar.Realize``), allora viene emesso un assert se uno dei tool è "sbagliato"... ma naturalmente a questo punto è impossibile dire esattamente quale::

    bmp = wx.Bitmap('non_esiste.bmp', type=wx.BITMAP_TYPE_BMP)
    toolbar = self.CreateToolBar()
    toolbar.AddLabelTool(-1, 'Ops!', bmp)
    try:
        toolbar.Realize()
    except PyAssertionError:
        print 'presa al volo!'

L'elenco delle eccentricità potrebbe continuare a lungo. ``wx.PyAssertionError`` è uno strumento indubbiamente utile, che però non può essere usato con la stessa disinvoltura con cui un programatore Python è abituato a usare le sue eccezioni. A noi verrebbe naturale scrivere codice più o meno così::

    try:
        bmp = wx.Bitmap('non_esiste.bmp', type=wx.BITMAP_TYPE_BMP)
    except IOError:
        ...

Questo è l'approccio "`Easier to Ask for Forgiveness Than Permission <https://docs.python.org/2/glossary.html>`_" tipico di Python. Ma quando avete a che fare con wxWidgets dovete spesso adeguarvi al principio opposto "Look Before You Leap" del mondo C/C++. In questo caso, tutto considerato, sarebbe probabilmente più saggio verificare se il file esiste davvero, prima di caricarlo nella ``wx.Bitmap``. 

A parte queste considerazioni, vale infine la pena di ricordare che ``wx.PyAssertionError`` ha comunque gli stessi limiti di tutte le eccezioni Python nell'ecosistema wxPython: in particolare, :ref:`deve essere intercettato nello stesso "strato" di codice Python in cui viene emesso<eccezioni>`. 


.. index::
   single: chiusura; wx.PyDeadObjectError
   single: eccezioni; wx.PyDeadObjectError
   single: wx; PyDeadObjectError

``wx.PyDeadObjectError`` e il problema della distruzione dei widget.
--------------------------------------------------------------------

Nella pagina :ref:`dedicata alla chiusura dei widget<chiusura_forzata>` abbiamo già avuto modo di parlare di ``wx.PyDeadObjectError``. Si tratta di un'eccezione che wxPython innesca quando provate ad accedere (da Python) a un oggetto wxWidget che non esiste più in quando è stato distrutto. Abbiamo già visto come, entro certi limiti, possa servire per testare se la chiusura di una finestra è andata a buon fine. Ma si tratta di un'utilizzo "positivo" marginale. In genere ``wx.PyDeadObjectError`` è un evento "negativo" nel contesto del vostro programma: vi segnala che, probabilmente, vi siete dimenticati un handler Python "orfano" in giro. 

Riassumiamo brevemente la questione: wxPython è costruito a partire da wxWidgts usando `SWIG <http://www.swig.org/>`_. Quando istanziate (da Python) un oggetto del framework wxWidget (C++), quello che fa davvero SWIG è creare due oggetti, quello "reale" C++ e un oggetto proxy Python che vi permette di controllarlo::

    >>> import wx
    >>> app = wx.App()
    >>> app
    <wx._core.App; proxy of <Swig Object of type 'wxPyApp *' at 0x333bf00> >
    >>> frame = wx.Frame(None)
    >>> frame
    <wx._windows.Frame; proxy of <Swig Object of type 'wxFrame *' at 0x22fb600> >
    >>> button = wx.Button(frame)
    >>> button
    <wx._controls.Button; proxy of <Swig Object of type 'wxButton *' at 0x4121700> >
    >>>

Come vedete, abbiamo sempre due oggetti: un oggetto Python (``wx._core.App``, ``wx._windows.Frame``, ``wx._controls.Button``) che agisce da proxy per il corrispettivo oggetto C++ (``wxPyApp``, ``wxFrame``, ``wxButton``) creato da SWIG. E' facile perdere la contabilità di questa "partita doppia", specialmente programmando in un linguaggio dinamico come Python. In particolare, potrebbero esserci due problemi speculari:

1) come abbiamo visto, i widget (finestre, pulsanti, etc.) si distruggono usando ``wx.Window.Destroy`` (preferibilmente chiamato attraverso ``wx.Window.Close``): questo finisce per invocare il distruttore dell'oggetto C++, ma non ha nessun effetto sull'oggetto proxy Python, che resta normalmente in vita. 

2) gli oggetti proxy, d'altra parte, si possono distruggere come qualsiasi oggetto Python: ri-assegnando la variabile che ne conservava un riferimento; lasciando semplicemente che escano dallo "scope"; usando l'operatore ``del``. In tutti questi casi, naturalmente posto che non ci siano in giro altri riferimenti all'oggetto, il garbage collector di Python ne programma la distruzione. Ma distruggere il proxy Python non ha nessun effetto sul corrispondente oggetto C++, che quindi resta in vita. 

Approfondiamo ciascuno di questi due casi separatamente.

.. todo:: una pagina su SWIG e l'oop Python/C++.


Distruggere il proxy Python lasciando in vita l'oggetto C++.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In linea di principio, distruggere il proxy Python di un oggetto C++ ancora in vita sarebbe un "memory leak": avete un oggetto che resta in memoria senza che possiate più raggiungerlo da Python. In realtà, nel caso dei normali widget, di solito non è così grave: da un lato, esiste in genere la possibilità di rintracciarli tramite i normali meccanismi di wxPython (per esempio :ref:`gli id<gli_id>`, o usando la :ref:`catena dei parent<catenaparent>`); dall'altro, se il widget è visibile, l'utente ha sempre la possibilità di intervenire: per esempio chiudere una finestra lasciata aperta. Nell'esempio che segue, ogni clic sul pulsante crea un nuovo ``wx.Frame`` (invisibile!): l'oggetto Python viene sempre cancellato, non appena la variabile ``frame`` esce dallo "scope" del callback ``on_clic``. Tuttavia gli oggetti C++ che restano in vita in questo caso sono figli del frame principale, e pertanto possono essere recuperati da wxWidgets attraverso strumenti come ``wx.Window.GetChildren``::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b = wx.Button(p, -1, 'clic', pos=(20, 20))
            b.Bind(wx.EVT_BUTTON, self.on_clic)

        def on_clic(self, evt):
            frame = wx.Frame(self)
            print len(self.GetChildren())


Distruggere l'oggetto C++ lasciando in vita il proxy Python.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Il caso opposto di solito è più preoccupante. La distruzione di un oggetto wxWidgets può avvenire in qualsiasi momento e anche indipendentemente da noi: basta che l'utente faccia clic sul pulsante di chisura di una finestra, e non solo quella finestra ma anche tutti i widget che contiene saranno distrutti. Una volta che l'oggetto wxWidgts è distrutto, qualunque ulteriore accesso al proxy Python innesca un ``wx.PyDeadObjectError``, come sappiamo::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b = wx.Button(p, -1, 'clic', pos=(20, 20))
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            self.child_frame = wx.Frame(self )
            self.child_frame.Show()

        def on_clic(self, evt):
            print self.child_frame.GetId() # per esempio

Nell'esempio qui sopra, ottenete un ``wx.PyDeadObjectError`` quando fate clic sul pulsante dopo aver chiuso il frame figlio. Come abbiamo già detto nella pagina :ref:`sulla chiusura dei widget<chiusura_forzata>` potete sfruttare questa eccezione per testare se un widget esiste ancora, catturandola in un blocco ``try/except``. 

:ref:`Come abbiamo visto<chiusura_avanzata>`, la distruzione a cascata di molti widget (per esempio, a seguito della chiusura di una finestra) comporta delle complicazioni ulteriori. Se è possibile intromettersi nel processo di distruzione (ovvero, generare o intercettare un evento nell'intervallo compreso tra la prima chiamata a ``wx.Window.Destroy`` e l'effettiva distruzione di tutti i widget coinvolti), potrebbero esserci delle conseguenze bizzarre. 

Per esempio, non è difficile modificare :ref:`uno degli esempi<trappole_chiusura>` che abbiamo fatto in modo da ottenere un ``wx.PyDeadObjectError``::

    class MyFrame(wx.Frame): 
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            self.txt = wx.TextCtrl(p, pos=(20, 20))
            self.tree = wx.TreeCtrl(p, pos=(20, 60), size=(100, 300),
                                    style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
            root = self.tree.AddRoot('')
            for i in range(10):
                item = self.tree.AppendItem(root, 'nodo %d' % i)
            self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)

        def on_sel_changed(self, evt):
            print self.txt.GetValue()

Se siete in Windows, questo codice genera una raffica di ``wx.PyDeadObjectError`` al momento di chiudere la finestra, quando gli eventi spuri emessi dal ``wx.TreeCtrl`` provocano dei tentativi di accesso a un ``wx.TextCtrl`` che nel frattempo è stato già distrutto (per l'analisi completa del motivo di tutto ciò, dovete leggervi :ref:`la pagina dedicata<trappole_chiusura>`). 

In ogni caso, abbiamo già anche visto la soluzione: tutte le volte che un evento potrebbe essere intercettato nel mezzo del processo di chiusura, potete evitare gli eventuali ``wx.PyDeadObjectError`` semplicemente testando la finestra per ``wx.Window.IsBeingDeleted``: se ottenete ``True``, semplicemente non eseguite il codice del callback::

    def on_sel_changed(self, evt):
        if not self.IsBeingDeleted():
            print self.txt.GetValue()


.. index:: 
   single: eccezioni; type checking

Le "%typemap" di SWIG e il type checking in wxPython.
-----------------------------------------------------

Infine, un cenno meritano le eccezioni con cui wxPython sostituisce il type checking statico della controparte C++. Avrete già notato che, se chiamate un metodo o una funzione con una signature diversa da quella prevista (parametri del tipo sbagliato etc.), ottenete una eccezione Python (che si comporta come di consueto in wxPython: non ferma il programma, etc.).

Queste eccezioni sono originate dalle `"%typemap" di SWIG <http://www.swig.org/Doc3.0/Typemaps.html>`_: in sostanza, meccanismi di traduzione che convertono il type checking delle funzioni C++ di wxWidgets. 

Le typemap di SWIG fanno in genere molto bene il loro lavoro: tuttavia si tratta pur sempre di meccanismi automatici che, per quanto regolati e affinati negli anni da Robin Dunn, hanno pur sempre le loro idiosincrasie. Con la pratica, non è difficile imbattersi in curiose bizzarrie di ogni tipo::

    wx.Colour(100, -1, 100)    # restituisce ValueError
    wx.Colour(100, 'ops', 100) # restituisce ValueError
    wx.Colour(100, 500, 100)   # restituisce OverflowError... naturalmente!

Esperienze del genere scoraggiano un po' chi è abituato alla comodità di ``try/except``. Non c'è dubbio che programmando in wxPython bisogna adeguarsi all'approccio "Look Before You Leap" tipico del mondo C/C++. Tuttavia anche le eccezioni Python si possono usare con successo: l'importante, come sempre, è non lesinare mai con gli unit test.


.. _consigli_finali_log_eccezioni:

Consigli conclusivi su logging e gestione delle eccezioni.
----------------------------------------------------------

Per finire, riprendiamo qui anche il discorso sul :ref:`logging in wxPython<logging2>`, e riassumiamo alcune strategie tipiche. 

- Per fare logging in wxPython, vi conviene utilizzare il modulo ``logging`` della libreria standard di Python. 

- Ci sono pochi casi in cui forse vi conviene usare il framework di logging di wxPython (``wx.Log`` etc.): quando l'applicazione è così semplice da non avere una logica di business "pure-Python" separata; o magari quando scegliete di usare il log in modo intensivo per mostrare messaggi all'utente. Eventualmente, valutate se usare ``wx.LogChain`` per indirizzare i messaggi a diversi log target separati. 

- Se decidete di usare ``logging``, questo non basta comunque a liberarvi del tutto da ``wx.Log`` perché wxPython ne fa uso in due modi:

- wxPython emette un ``wx.LogFatalError`` prima di chiudere l'applicazione, in caso di errore talmente grave da compromettere il funzionamento del motore di wxWidget: questo comportamento non è modificabile in nessun modo;

- wxPython emette un ``wx.LogSysError`` (e di default mostra un messaggio all'utente) quando incontra un errore interno non fatale. Potete (e dovreste, in effetti) reagire a questi errori scrivendo un log target personalizzato: quando intercettate il messaggio, potete inviarlo al normale log Python; mostrare o meno un messaggio all'utente; chiudere l'applicazione, e così via. 

- Un log target personalizzato non è uno strumento molto preciso, ma è il meglio che potete fare per intercettare gli errori di sistema che wxPython tratta con ``wx.LogSysError``.

- Poi ci sono gli errori che wxWidgets gestisce internamente con gli assert C++, e che wxPython cattura e restituisce sotto forma di ``wx.PyAssertionError``. Potete intercettare questa eccezione in un normale blocco ``try/except``, se volete. Ma spesso non è una buona idea, perché si tratta di un'eccezione molto generica. Se siete sicuri che una determinata api emette ``wx.PyAssertionError`` solo in una circostanza ben precisa, usate ``try/except``. Altrimenti è preferibile l'approccio "Look Before You Leap": verificate che le condizioni siano tutte corrette, e soltanto allora chiamate l'api. Se fate così, tutte le eccezioni ``wx.PyAssertionError`` che dovessero ancora verificarsi sarebbero bachi imprevisti: catturatele nel vostro "hook acchiappa-tutto" (vedi sotto) e debuggate quanto prima. 

- Per ``wx.PyDeadObjectError`` vale praticamente la stessa raccomandazione: intercettatelo in un ``try/except`` solo quando siete veramente sicuri del motivo per cui viene emesso. Altrimenti, "Look Before You Leap": nei casi critici potete testare ``wx.Window.IsBeingDeleted`` prima di accedere a un widget. I ``wx.PyDeadObjectError`` "liberi" sono naturalmente dei bachi: catturateli nel vostro "hook acchiappa-tutto" e debuggate.

- Siete invece liberi di usare ``try/except`` a piacere, per le eccezioni Python che provengono dal vostro codice: anzi, è il normale approccio "Easier to Ask for Forgiveness Than Permission" di Python. Attenzione però: le eccezioni Python vanno catturate quanto prima, perché in wxPython non possono propagarsi al di fuori del segmento di codice Python da cui sono originate. Un'eccezione Python non catturata è, ancora una volta, un baco: in wxPython però l'applicazione non termina come al solito, e questo è un problema grave. Il meglio che potete fare è catturarle nell'"hook acchiappa-tutto" e debuggare, debuggare quanto prima. 

- Siccome le eccezioni Python non gestite (vostre, o i ``xw.Py*Error`` generati da wxPython) non terminano immediatamente il programma, potrebbero avere effetti nascosti molto gravi. Il meglio che potete fare è sovrascrivere ``sys.excepthook`` con un vostro "hook acchiappa-tutto": quando catturate in questo modo un'eccezione non gestita, dovreste senz'altro scriverla nel log. Potete eventualmente mostrare un messaggio all'utente, e chiudere voi stessi l'applicazione. 

- Tutte queste raccomandazioni (log target personalizzati, ``sys.excepthook`` sovrascritti, etc.) valgono solo quando il vostro programma è in produzione. In fase di sviluppo, naturalmente, volete invece che gli errori saltino fuori nel modo più appariscente possibile. Una buona strategia potrebbe essere scrivere due versioni separate della vostra ``wx.App`` (o almeno, due versioni del suo ``wx.App.OnInit`` e ``wx.App.OnExit``), da usare in ambiente di sviluppo e in produzione. 
