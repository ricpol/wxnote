.. _dimensioni:

.. index:: 
   single: sizer; dimensioni dei widget
   single: dimensioni in wxPython
   
   
Le dimensioni in wxPython.
==========================

I questa pagina vediamo come si specificano le dimensioni di un widget in wxPython. Gran parte delle cose che stiamo per dire hanno significato soprattutto quando sono applicate ai sizer. Quindi queste note sono un importante complemento alle :ref:`due <sizer_basi>` :ref:`pagine <sizer_avanzati>` che dedichiamo ai sizer: in questa pagina diamo per scontato che le abbiate già lette. 


.. index:: 
   single: dimensioni in wxPython; wx.Size
   single: dimensioni in wxPython; wx.Window.SetSize*
   single: wx.Size
   single: wx.Window; SetSize*

``wx.Size``: la misura delle dimensioni.
----------------------------------------

In wxWidgets le dimensioni si indicano come istanze della classe ``wx.Size``. Questo significa, per esempio, che per definire le dimensioni di un pulsante bisogna scrivere::

    button.SetSize(wx.Size(50, 50))

Tuttavia in wxWidgets trovate anche alcuni metodi "doppioni" che vi consentono più rapidamente di usare due argomenti (larghezza e altezza), senza bisogno di istanziare esplicitamente ``wx.Size``. Questi doppioni si riconoscono perché terminano in ``*WH``. Per esempio, questo è equivalente alla precedente::

    button.SetSizeWH(50, 50)
    
Talvolta invece accade il contrario. Il metodo "normale" richiede due argomenti, e tuttavia ne esiste anche una versione "doppia" che consente l'uso di ``wx.Size``. Questi doppioni si riconoscono perché terminano in ``*.Sz``. Per esempio, ``SetSizeHints`` ha un doppio ``SetSizeHintsSz``. 

In wxPython le cose sono più semplici da un lato, e involontariamente più complicate dall'altro. wxPython converte automaticamente le istanze di ``wx.Size`` in più confortevoli tuple. Potete ancora usare esplicitamente ``wx.Size`` se proprio volete, ma di solito si preferisce farne a meno::

    button.SetSize((50, 50))
    
Notate che comuque ``SetSize`` vuole un solo argomento! Soltanto, abbiamo scritto una tupla al posto dell'istanza di ``wx.Size``. Naturalmente si può sempre usare la versione ``*WH`` del metodo, se si preferisce passare due argomenti invece della tupla. 

In aggiunta a questo, in wxPython alcuni metodi "getter" hanno dei "doppioni" che restituiscono una tupla al posto di istanze di ``wx.Size``. Si riconoscono perché terminano in ``*Tuple``. Per esempio, ``GetSize`` ha il compagno ``GetSizeTuple``. 

.. note:: Tutto questo è in effetti confuso e ridondante. E' vero, ma dovete ricordare che in C++ non sono disponibili le strutture-dati di alto livello di Python. Quindi wxWidgets definisce una lunga serie di tipi fondamentali, come ``wx.Point``, ``wx.Size``, ``wx.Rect``, ``wx.DateTime`` e molti altri. wxPython da un lato semplifica le cose, dall'altro necessariamente le complica, perchè i nuovi oggetti Python devono coesistere con le classi preesistenti C++.

Un'osservazione conclusiva: passare il valore ``-1`` a qualsiasi argomento di queste funzioni, è come dire "non mi importa". Per esempio, se scrivete::

    button.SetSize((50, -1))
    
imponete che la larghezza del pulsante sia 50 pixel, ma lasciate libero wxPython di determinare l'altezza. 


.. index:: 
   single: wx.Window; GetSize(Tuple)
   single: wx.Window; SetSize(WH)
   single: wx.Window; GetClientSize(Tuple)
   single: wx.Window; SetClientSize(WH)
   single: wx.Window; SetInitialSize
   single: wx.Window; GetMaxSize
   single: wx.Window; GetMinSize
   single: wx.Window; SetMaxSize
   single: wx.Window; SetMinSize
   single: wx.Window; SetSizeHints(Sz)
   single: wx.Window; GetVirtualSize(Tuple)
   single: wx.Window; SetVirtualSize(WH)
   single: wx.Window; SetVirtualSizeHints(Sz)
   single: wx.Window; GetBestSize(Tuple)
   single: dimensioni in wxPython; wx.Window.GetSize(Tuple)
   single: dimensioni in wxPython; wx.Window.SetSize(WH)
   single: dimensioni in wxPython; wx.Window.GetClientSize(Tuple)
   single: dimensioni in wxPython; wx.Window.SetClientSize(WH)
   single: dimensioni in wxPython; wx.Window.SetInitialSize
   single: dimensioni in wxPython; wx.Window.GetMaxSize
   single: dimensioni in wxPython; wx.Window.GetMinSize
   single: dimensioni in wxPython; wx.Window.SetMaxSize
   single: dimensioni in wxPython; wx.Window.SetMinSize
   single: dimensioni in wxPython; wx.Window.SetSizeHints(Sz)
   single: dimensioni in wxPython; wx.Window.GetVirtualSize(Tuple)
   single: dimensioni in wxPython; wx.Window.SetVirtualSize(WH)
   single: dimensioni in wxPython; wx.Window.SetVirtualSizeHints(Sz)
   single: dimensioni in wxPython; wx.Window.GetBestSize(Tuple)

Gli strumenti per definire le dimensioni.
-----------------------------------------

Ecco un rapido riassunto dei metodi "getter" e "setter" più significativi per quanto riguarda le dimensioni dei widget. Quando esistono "doppioni" dei metodi, li indico in forma abbreviata. Per esempio, ``SetSize(WH)`` indica che esiste anche la forma ``*WH`` di ``SetSize``.

* ``GetSize(Tuple)``, ``SetSize(WH)``: specificano esattamente le dimensioni che deve avere il widget. Notate che, se il widget è inserito in un sizer con flag ``wx.EXPAND`` e/o con proporzione superiore a 0, le sue dimensioni potrebbero comunque variare. 

* ``GetClientSize(Tuple)``, ``SetClientSize(WH)``: come i precedenti, ma meno platform-dependent se usati con i frame e i dialoghi. Infatti calcolano solo l'area "effettiva" della finestra, lasciando fuori bordi e barra del titolo, che possono avere dimensioni diverse su diversi sistemi. Chiaramente, se un widget non ha bordi, è lo stesso che dire ``GetSize``.

* ``SetInitialSize``, come ``SetSize``, ma se lasciate delle dimensioni libere (passando ``-1``), le completa con il "best size" del widget (vedi sotto). Notate che questo è esattamente il comportamento del paramentro ``size`` del costruttore di tutti i widget. Quindi ``SetInitialSize`` è come un "costruttore differito" per quanto riguarda le dimensioni (da cui lo "Initial" nel nome). In più, ``SetInitialSize`` imposta anche le dimensioni minime (come chiamare ``SetMinSize``, vedi sotto). 

* ``GetMaxSize``, ``SetMaxSize``, ``GetMinSize``, ``SetMinSize``: specificano le dimensioni massime e minime che può avere il widget. 

* ``SetSizeHints(Sz)``: consente di specificare dimensioni massime e minime in un colpo solo, come dire ``SetMaxSize`` seguito da ``SetMinSize``.

* ``GetVirtualSize(Tuple)``, ``SetVirtualSize(WH)``, ``SetVirtualSizeHints(Sz)``: per le finestre con scrolling incorporato (``wx.ScrolledWindow``, etc.) si riferisce alle dimensioni "vere", e non quelle che si vedono effettivamente.

* ``GetBestSize(Tuple)``: il "best size", ossia le dimensioni minime per cui il widget si mantiene "presentabile" (per esempio, per un ``wx.StaticText`` questo dipende dalla lunghezza del testo che deve essere visualizzato).

La cosa importante da capire qui è che potete indicare esattamente le dimensioni di un widget, fornire indicazioni su minimi e/o massimi, o infine non indicarle affatto. Tenendo conto dei vincoli che imponete, l'algoritmo dei sizer cercherà di distribuire lo spazio disponibile nel miglior modo possibile.

.. index:: 
   single: sizer; wx.Sizer.Fit
   single: sizer; wx.Window.Fit
   single: sizer; wx.Sizer.Layout
   single: sizer; wx.Window.Layout
   single: sizer; wx.EVT_SIZE
   single: sizer; SendSizeEvent
   single: eventi; wx.EVT_SIZE
   single: eventi; wx.Window.SendSizeEvent
   single: dimensioni in wxPython; wx.Sizer.Fit
   single: dimensioni in wxPython; wx.Window.Fit
   single: dimensioni in wxPython; wx.Sizer.Layout
   single: dimensioni in wxPython; wx.Window.Layout
   single: dimensioni in wxPython; wx.Window.SendSizeEvent
   single: dimensioni in wxPython; wx.EVT_SIZE
   single: wx.Sizer; Fit
   single: wx.Window; Fit
   single: wx.Sizer; Layout
   single: wx.Window; Layout
   single: wx.Window; SetAutoLayout
   single: dimensioni in wxPython; wx.Window.SetAutoLayout
   single: wx.EVT_SIZE
   single: wx.Window; SendSizeEvent
   
.. _fit_layout:

``Fit`` e ``Layout``: ricalcolare le dimensioni.
------------------------------------------------

Esistono apparentemente due versioni di ``Fit``, una come metodo di ``wx.Sizer`` (quindi di tutti i sizer derivati) e un'altra come metodo di ``wx.Window`` (quindi di tutti i widget). In realtà il secondo finisce per chiamare il primo, quindi alla fine è indifferente quale utilizzate. 

``wx.Sizer.Fit(window)`` (passando come argomento il contenitore che il sizer gestisce) dice al sizer di calcolare le dimensioni della finestra basandosi su tutto quello che conosce riguardo agli elementi al suo interno. 

``wx.Window.Fit()`` (senza argomenti) dice alla finestra di calcolare le sue dimensioni, con strategie diverse a seconda dei casi. Se alla finestra è stato assegnato un sizer, chiama direttamente ``wx.Sizer.Fit(window)`` per fare il lavoro. Altrimenti sceglie il "best size" per la finestra. 

Anche ``Layout`` è disponibile sia come metodo dei sizer, sia dei contenitori (e ha effetti analoghi in entrambi i casi). Chiamare ``Layout()`` forza il ricalcolo dell'algoritmo del sizer (e/o dei :ref:`constraints<constraint>`). Notate che il gestore di default di un evento ``wx.EVT_SIZE`` non chiama ``Layout`` automaticamente per ridisegnare la finestra ogni volta che l'utente la ridimensiona, e in genere questo non è necessario se il vostro layout è disegnato con i sizer. Se invece usate i constraints, o se comunque volete che ``Layout`` sia chiamato ogni volta, potete impostare ``wx.Window.SetAutoLayout(True)`` sul contenitore-parent di grado più alto (per esempio, il panel che contiene i widget che volete ri-disegnare). Ricordatevi anche che, se catturate voi stessi un ``wx.EVT_SIZE``, dovreste sempre ricordarvi di chiamare ``Skip`` nel vostro callback per consentire la gestione di default dell'evento. Se non vi orientate in tutto questo, probabilmente non avete ancora letto :ref:`la sezione dedicata agli eventi <eventibasi>`.

Ci sono due casi tipici (constraints a parte) in cui forzare il ricalcolo con ``Layout`` è utile:

* quando date delle dimensioni fisse a un frame, e poi lo riempite con dei widget, li organizzate in un sizer e infine assegnate il sizer al frame, in effetti il frame non riceve alcun ``wx.EVT_SIZE`` dopo il primo dimensionamento, e quindi verrà disegnato male. In questi casi, un ``self.Layout()`` proprio alla fine dell'``__init__`` risolve le cose (ma un'altra soluzione, beninteso, è ricordarsi di impostare le dimensioni del frame *come ultima cosa*, oppure non impostarle affatto);

* all'occorrenza, per ri-disegnare la finestra dopo che è stata mostrata, se per esempio sono stati aggiunti o nascosti dei widget. 

In casi particolari potrebbe essere necessario innescare programmaticamente un ``wx.EVT_SIZE``, anche se la finestra non viene ridimensionata. Per esempio, se nascondete/mostrate una toolbar, o un menu, o una status bar, allora chiamare ``Layout`` da solo non basta, perché questi elementi non sono gestiti direttamente dai sizer. In casi del genere, potete chiamare ``SendSizeEvent()`` sulla finestra per innescare programmaticamente un ``wx.EVT_SIZE``. 


