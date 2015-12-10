.. _eventitecniche:

.. index::
   single: eventi
   
Gli eventi: altre tecniche.
===========================

Abbiamo già dedicato :ref:`due <eventibasi>` :ref:`pagine <eventi_avanzati>` agli eventi. In questa sezione raccogliamo alcune note aggiuntive: non si tratta di concetti più difficili dei precedenti, ma semplicemente di tecniche di utilizzo meno frequente. 

La lettura di questa pagina presuppone la conoscenza delle due precedenti.

.. index::
   single: eventi; lambda binding

.. _lambda_binding:

Lambda binding.
---------------

Abbiamo visto che un callback può, di regola, accettare un solo argomento: un riferimento all'evento che è stato intercettato. Questa è una limitazione piuttosto fastidiosa del framework c++ sottostante. In realtà spesso l'oggetto-evento porta con sé molte informazioni utili (``GetEventObject`` restituisce un riferimento all'oggetto originario, per esempio), ma ci sono casi in cui semplicemente si vorrebbe passare al callback qualcosa in più. 

Una soluzione drastica sarebbe quella di creare un evento personalizzato (come mostriamo oltre in questa stessa pagina) che porti dentro di sé tutte le informazioni che ci servono. 

Una soluzione ancora più drastica potrebbe essere intercettare l'evento in uno stadio precedente della sua propagazione, arricchirlo delle proprietà che ci servono, e lasciarlo proseguire. 

Tuttavia le funzioni anonime ``lambda`` ci offrono una soluzione molto più snella. Una ``lambda`` conta pur sempre come "uno" negli argomenti accettati da ``Bind``, ma dentro possiamo metterci quello che vogliamo. Lo schema è molto facile da capire::

    button.Bind(wx.EVT_BUTTON, 
                lambda evt, foo=foo_val, bar=bar_val: self.callback(evt, foo, bar))
                

    def callback(self, evt, foo, bar): 
        pass # ...

La nostra funzione ``lambda`` riceve ancora l'argomento consueto ``evt`` (il riferimento all'evento), ma ne aggiunge anche altri a piacere. In questo modo possiamo passare a ``callback`` più informazioni di quelle contenute in ``evt``. 

Grazie alla consueta flessibilità di Python, possiamo passare come argomenti aggiuntivi sia valori statici (il testo di una label, per esempio), sia riferimenti a funzioni da eseguire nel callback per ottenere valori dinamici. 

.. index::
   single: eventi; binding con 'partial'

Partial binding.
----------------

Il lambda-binding è un trucco molto vecchio. Nelle versioni più recenti di Python, si può ottenere la stessa cosa, naturalmente, usando ``functools.partial``. Si tratta di una tecnica molto meno utilizzata, ma solo per la maggiore consuetudine con il lambda-binding. 

Anche in questo caso, non c'è molto da spiegare::

    from functools import partial
    
    button.Bind(wx.EVT_BUTTON, partial(self.callback, foo=foo_val, bar=bar_val))
    
    
    def callback(self, evt, foo, bar):
        pass # ...
        
In pratica, ``functools.partial`` è un wrapper del nostro callback che lascia fuori solo il primo argomento (il consueto riferimento all'evento), e specifica quelli successivi. 

.. index::
   single: eventi; Event Manager
   single: wx.lib.evtmgr; eventManager

.. _eventmanager:

Event Manager.
--------------

``wx.lib.evtmgr`` è una piccola libreria che propone un modo alternativo e più "pitonico" di collegare gli eventi. E' più o meno facile da usare come ``Bind``, tuttavia è anche altrettanto facile scollegare gli eventi, e soprattutto si può registrare un numero arbitrario di widget ad "ascoltare" il verificarsi di un certo evento (con ``Bind`` è possibile solo il contrario: registrare un solo widget per catturare molti eventi). 

Il modulo esporta una classe ``eventManager``, che è un singleton. Il suo utilizzo è incredibilmente semplice:: 

    from wx.lib.evtmgr import eventManager
    
    # per registrare un callback all'ascolto di un evento proveniente da widget
    eventManager.Register(callback, wx.EVT_*, widget)
    
    # per de-registrare un callback
    eventManager.DeregisterListener(callback)
    
    # per de-registrare tutti i callback in ascolto degli eventi di widget
    eventManager.DeregisterWindow(widget)
    
Come si può intuire dall'interfaccia, Event Manager utilizza il design pattern noto come Publisher/Subscriber. In effetti, wxPython ha una sua implemetazione di pub/sub, molto ben fatta, di cui parliamo :ref:`in una pagina separata<pubsub>`.

Event Manager non è molto usato nella pratica perché il normale sistema di collegamento con ``Bind`` è in genere sufficiente: il punto di forza di Event Manager (collegamento molti-a-molti tra sorgenti e ascoltatori) è in genere poco utile nella struttura gerarchica dei gui-framework. 

Tuttavia, Event Manager può essere preso in considerazione in molte situazioni dove pub/sub andrebbe impiegato. Se il vostro design funzionerebbe meglio con pub/sub, allora date prima una possibilità anche a Event Manager. Vi rimandiamo quindi alla :ref:`pagina di pub/sub<pubsub>` per un esame più approfondito di Event Manager e di quando conviene usarlo. 

.. _eventi_personalizzati:

.. index::
   single: eventi; eventi personalizzati

Eventi personalizzati.
----------------------

wxPython offre una grandissima varietà di eventi pronti all'uso, che coprono tutte le possibili interazioni con l'utente. Tuttavia, è possibile anche creare nuovi eventi all'occorrenza. 

Questo può essere utile in diverse occasioni, ma forse la più comune è quando si crea un nuovo widget (partendo da zero, oppure assemblando cose già esistenti). Anche se al suo interno il widget può fare uso dei soliti eventi wxPython, spesso si preferisce che propaghi verso l'esterno un evento nuovo, con un binder specifico apposta per lui. In questo modo si nascondono i dettagli dell'implementazione interna, l'evento può trasportare le informazioni che desideriamo, e l'event type "firma" l'evento rendendo evidente che è stato originato dal nostro widget. 

Creare un evento, di per sé, non basta. Occorre anche creare un nuovo event type e un nuovo binder per collegarlo ai callback. Esaminiamo questi passaggi, prendendo spunto da un esempio concreto: vogliamo creare un nuovo "widget" che permetta di selezionare i trimestri di un anno. 

.. note:: L'esempio che segue è una semplificazione di un widget più elaborato che ho scritto per un altro progetto. La versione completa, per chi è interessato, :ref:`si trova qui <periodwidget>`.

Il widget è composto da un ``wx.ComboBox`` che elenca i trimestri, e uno ``wx.SpinCtrl`` per selezionare l'anno::

    from datetime import datetime

    class PeriodWidget(wx.Panel):
        PERIODS = {'1 trimestre': ((1, 1), (3, 31)), '2 trimestre': ((4, 1), (6, 30)), 
                   '3 trimestre': ((7, 1), (9, 30)), '4 trimestre': ((10, 1), (12, 31))}
        def __init__(self, *a, **k):
            wx.Panel.__init__(self, *a, **k)
            self.period = wx.ComboBox(self, choices=self.PERIODS.keys(), 
                                      style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
            self.period.SetSelection(0)
            self.year = wx.SpinCtrl(self, initial=2012, min=1950, max=2050)
            s = wx.BoxSizer()
            s.Add(self.period, 0, wx.EXPAND|wx.ALL, 5)
            s.Add(self.year, 0, wx.EXPAND|wx.ALL, 5)
            self.SetSizer(s)
            s.Fit(self)
        
        def GetValue(self): 
            start, end = self.PERIODS[self.period.GetStringSelection()]
            year = self.year.GetValue()
            return datetime(year, *start), datetime(year, *end)

Quando l'utente agisce sui due widget interni del nostro ``PeriodWidget``, emette degli eventi che possono essere intercettati. Noi vorremmo però presentare all'esterno un'interfaccia più coerente e pulita: il nostro widget dovrebbe emettere un evento personalizzato ogni volta che l'utente cambia il periodo oppure l'anno. 

Ecco quindi quello che dobbiamo fare.

.. index::
   single: eventi; wx.NewEventType
   single: eventi; wx.PyEventBinder
   single: wx.NewEventType
   single: wx.PyEventBinder
   
Definire un event-type e un binder.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Prima ancora di scrivere la nostra classe-evento, conviene definire un nuovo event type, e di conseguenza un nuovo binder per identificare il nostro evento. Per fortuna questa è la parte più facile di tutta l'operazione::

    myEVT_PERIOD_MODIFIED = wx.NewEventType()
    EVT_PERIOD_MODIFIED = wx.PyEventBinder(myEVT_PERIOD_MODIFIED, 1)

Come si vede, la cosa più difficile è la scelta del nome. In genere per l'event type si preferisce uno schema del tipo ``myEVT_*``, per mimare gli event type standard ``wx.wxEVT_*``. Sempre per consuetudine, il binder ha lo stesso nome dell'event type, tolto il prefisso ``my``. 

``wx.NewEventType()`` restituisce semplicemente un nuovo identificatore non ancora usato per gli event type predefiniti. Ne abbiamo bisogno subito per definire il binder, e poi ne avremo ancora bisogno per istanziare l'oggetto-evento, come vedremo. 

Il nostro binder dovrà essere una istanza di ``wx.PyEventBinder``. Gli argomenti richiesti sono due: il primo è l'event type appena creato, e il secondo indica quanti Id ci si aspetta di ricevere al momento di creare l'evento. Questo sembra strano a prima vista, ma in realtà possiamo anche creare eventi "range" (come per esempio ``wx.EVT_MENU_RANGE``) che accettano due Id. Naturalmente, nella stragrande maggioranza dei casi abbiamo invece bisogno di un solo Id, quindi basta passare ``1``. 

.. index::
   single: eventi; wx.PyCommandEvent
   single: eventi; wx.PyEvent
   single: wx.PyCommandEvent
   single: wx.PyEvent
   
Scrivere un evento personalizzato.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Si tratta adesso di derivare da ``wx.PyCommandEvent``, la classe che wxPython mette a disposizione, al posto di ``wx.CommandEvent``, per sovrascrivere i metodi virtuali. Esiste anche una ``wx.PyEvent`` se si vuole scrivere un evento "non command", ma questo è naturalmente più inconsueto. 

.. todo:: una pagina sui pycontrols

Nella migliore delle ipotesi, basterà dichiarare la nostra sotto-classe (ma se è questo il vostro caso, allora c'è un modo ancora più facile di procedere, che vedremo oltre). 

Nel nostro caso, ne approfittiamo invece per aggiungere delle informazioni ulteriori che l'evento trasporterà con sé. Qui per esempio definiamo due proprietà per comunicare se l'utente ha modificato l'anno oppure il periodo (non dico che sia una cosa molto utile, ma è solo un esempio!)::

    class PeriodEvent(wx.PyCommandEvent):
        def __init__(self, evtType, id, mod_period=False, mod_year=False):
            wx.PyCommandEvent.__init__(self, evtType, id)
            self.mod_period = mod_period
            self.mod_year = mod_year

Come si vede, ``wx.PyCommandEvent`` accetta due argomenti: ``evtType`` è l'event type, e ``id`` è l'Id dell'oggetto da cui parte l'evento. Gli altri due argomenti sono una nostra aggiunta. Avremmo anche potuto aggiungere dei getter e setter per queste due proprietà, naturalmente. 

Abbiamo lasciata "aperta" la possibilità di settare il parametro ``evtType`` al momento della creazione dell'istanza: in genere è quello che si preferisce fare, perché si potrebbero creare diversi event type per lo stesso evento. Tuttavia, se sappiamo che esisterà solo un event type possibile per il nostro evento, possiamo anche impostarlo direttamente nella nostra classe:: 

    class PeriodEvent(wx.PyCommandEvent): # versione alternativa
        def __init__(self, id, mod_period=False, mod_year=False):
            wx.PyCommandEvent.__init__(self, myEVT_PERIOD_MODIFIED, id)
            self.mod_period = mod_period
            self.mod_year = mod_year

.. index::
   single: eventi; wx.EvtHandler.ProcessEvent
   single: eventi; wx.PostEvent
   single: wx.EvtHandler; ProcessEvent
   single: wx.PostEvent

.. _lanciare_evento_personalizzato:

Lanciare l'evento personalizzato.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adesso si tratta di scegliere il momento giusto per lanciare dal nostro widget l'evento che abbiamo scritto. Siccome vogliamo che l'evento parta nel momento in cui l'utente agisce su uno dei due elementi del widget, colleghiamo normalmente i due eventi corrispondenti, e quindi creiamo il nostro evento nei callback::

    # nell'__init__ di PeriodWidget aggiungiamo:
        self.period.Bind(wx.EVT_COMBOBOX, self.on_changed)
        self.year.Bind(wx.EVT_SPINCTRL, self.on_changed)
        
    def on_changed(self, evt): 
        changed = evt.GetEventObject()
        my_event = PeriodEvent(myEVT_PERIOD_MODIFIED, self.GetId(), 
                               changed==self.period, changed==self.year)
        my_event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(my_event)

Abbiamo collegato entrambi gli elementi allo stesso callback: ci fidiamo di ``GetEventObject`` per recuperare l'elemento che è stato modificato. La parte più interessante è la creazione dell'istanza di ``PeriodEvent``: come visto sopra, richiede due argomenti "obbligatori" (l'event type e l'Id del widget che lo sta generando), ai quali aggiungiamo i nostri due argomenti "personalizzati". 

E' anche utile impostare alcune proprietà dell'evento appena creato, prima di emetterlo. Nel nostro esempio impostiamo ``SetEventObject``, per permettere al futuro callback che lo intercetterà di usare ``GetEventObject`` se lo desidera. 

Quindi, dobbiamo emettere l'evento. Il modo più consueto è rivolgersi all'handler dello stesso widget che lo sta generando (``self.GetEventHandler()``) e chiedergli di processare immediatamente l'evento invocando direttamente ``ProcessEvent``. 

Si noti anche che, siccome nel callback non chiamiamo ``Skip``, i due eventi originari smettono di propagarsi, come desideriamo: d'ora in poi saranno sostituiti dal nostro evento personalizzato. 

C'è un altro modo di mettere in moto il nostro evento, ed è usare la funzione globale ``wx.PostEvent``. Nel nostro caso, sarebbe::

    wx.PostEvent(self.GetEventHandler(), my_event)
    
C'è una differenza minima ma importante tra i due metodi. ``ProcessEvent`` fa partire immediatamente l'evento, mentre ``PostEvent`` lo mette in coda allo stack di eventi pendenti dell'handler. Nel nostro esempio non fa nessuna differenza, ma supponiamo invece di dover chiamare ``Skip`` nel callback, per esempio per permettere la ricerca di gestori nelle sovraclassi. In questo caso, ``PostEvent`` farebbe partire il nostro evento soltanto *dopo* che ``wx.EVT_COMBOBOX`` (o ``wx.EVT_SPINCTRL``) sono stati intercettati dalle sovra-classi, il che è in genere quello che vogliamo. Invece ``ProcessEvent`` infilerebbe il nostro evento *prima* di terminare di processare quelli originali. Il risultato è che, se qualcuno intercetta il nostro evento, *quel* callback verrà eseguito *in mezzo* al nostro processo interno, e in genere non è il comportamento corretto. 

Per testare la differenza tra i due metodi, ecco una versione leggermente modificata del nostro esempio, che introduce una catena di sovra-classi del ``wx.ComboBox``::

    from datetime import datetime

    myEVT_PERIOD_MODIFIED = wx.NewEventType()
    EVT_PERIOD_MODIFIED = wx.PyEventBinder(myEVT_PERIOD_MODIFIED, 1)
        
    class PeriodEvent(wx.PyCommandEvent):
        def __init__(self, evtType, id, mod_period=False, mod_year=False):
            wx.PyCommandEvent.__init__(self, evtType, id)
            self.mod_period = mod_period
            self.mod_year = mod_year
            
    class SuperCombo(wx.ComboBox):
        def __init__(self, *a, **k):
            wx.ComboBox.__init__(self, *a, **k)
            self.Bind(wx.EVT_COMBOBOX, self.oncombo)
            
        def oncombo(self, evt):
            print 'sto lavorando nella sovra-classe'
            evt.Skip()
            
    class MyCombo(SuperCombo):
        def __init__(self, *a, **k): SuperCombo.__init__(self, *a, **k)

    class PeriodWidget(wx.Panel):
        PERIODS = {'1 trimestre': ((1, 1), (3, 31)), '2 trimestre': ((4, 1), (6, 30)), 
                   '3 trimestre': ((7, 1), (9, 30)), '4 trimestre': ((10, 1), (12, 31))}
        def __init__(self, *a, **k):
            wx.Panel.__init__(self, *a, **k)
            self.period = MyCombo(self, choices=self.PERIODS.keys(), 
                                  style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
            self.period.SetSelection(0)
            self.year = wx.SpinCtrl(self, initial=2012, min=1950, max=2050)
            s = wx.BoxSizer()
            s.Add(self.period, 0, wx.EXPAND|wx.ALL, 5)
            s.Add(self.year, 0, wx.EXPAND|wx.ALL, 5)
            self.SetSizer(s)
            s.Fit(self)
            
            self.period.Bind(wx.EVT_COMBOBOX, self.on_changed)
            self.year.Bind(wx.EVT_SPINCTRL, self.on_changed)
            
        def on_changed(self, evt): 
            evt.Skip()
            changed = evt.GetEventObject()
            my_event = PeriodEvent(myEVT_PERIOD_MODIFIED, self.GetId(), 
                                   changed==self.period, changed==self.year)
            my_event.SetEventObject(self)
            # alternate tra questi due metodi, e scoprite la differenza:
            # wx.PostEvent(self.GetEventHandler(), my_event)
            self.GetEventHandler().ProcessEvent(my_event)
        
        def GetValue(self): 
            start, end = self.PERIODS[self.period.GetStringSelection()]
            year = self.year.GetValue()
            return datetime(year, *start), datetime(year, *end)
            

    class MyFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            p = wx.Panel(self)
            self.period = PeriodWidget(p)
            self.period.Bind(EVT_PERIOD_MODIFIED, self.on_period)
            
        def on_period(self, evt):
            print 'mod. periodo:', evt.mod_period, 'mod. anno:', evt.mod_year
            print evt.GetEventObject().GetValue()

    app = wx.App(False)
    MyFrame(None).Show()
    app.MainLoop()


Intercettare l'evento personalizzato.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

L'esempio che abbiamo appena riportato illustra anche come si intercetta il nostro evento personalizzato. Non c'è nulla di speciale da dire al riguardo. Il codice cliente deve usare ``Bind(EVT_PERIOD_MODIFIED, ...)`` come farebbe con un qualsiasi altro binder ``wx.EVT_*``. 

.. index::
   single: eventi; wx.lib.newevent.NewCommandEvent
   single: eventi; wx.lib.newevent.NewEvent
   single: wx.lib.newevent; NewCommandEvent
   single: wx.lib.newevent; NewEvent
   
Un modo più rapido di creare un evento.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Se non avete bisogno di definire una classe per il vostro evento, allora ``wx.lib.newevent`` vi mette a disposizione una comoda scorciatoia per scavalvare le altre operazioni di routine. Tutto quello che occorre fare è::

    PeriodEvent, EVT_PERIOD_MODIFIED = wx.lib.newevent.NewCommandEvent()

Questo vi restituisce in un colpo solo una classe già costruita, e un binder. La classe è già predisposta con il type event corretto (che quindi non avete bisogno di conoscere). Quando volete creare l'istanza dell'evento, dovete solo passare un Id corretto al costruttore. Nel nostro esempio, sarebbe quindi::

    my_event = PeriodEvent(self.GetId())
    
Ovviamente, siccome ``PeriodEvent`` non è più una classe che abbiamo scritto noi stessi, non ha nessun metodo/proprietà aggiuntiva (o almeno, non *dovrebbe* averne... ma poi siamo pur sempre programmatori Python... un po' di monkey patching non ci spaventa di certo!). 

Quando vogliamo intercettare il nostro evento, possiamo usare il binder ``EVT_PERIOD_MODIFIED`` proprio come prima.

Oltre a ``wx.lib.newevent.NewCommandEvent()`` esiste anche ``wx.lib.newevent.NewEvent()`` per creare un evento "non command". 
