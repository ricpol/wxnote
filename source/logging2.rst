.. _logging2:

.. index:: 
   single: logging; con wxPython
   single: logging; wx.Log
   single: wx.Log
   single: logging; wx.LOG_*
   single: wx.LOG_*
   single: logging; wx.Log*
   single: wx.Log*
   single: logging; wx.Log.SetLogLevel
   single: wx.Log; SetLogLevel


Logging in wxPython (2a parte).
===============================

Riprendiamo qui il discorso sul logging che abbiamo iniziato :ref:`nella pagina<logging>` dedicata alle strategie per integrare ``logging`` in una applicazione wxPython. Ci occupiamo adesso del framework interno di logging di wxPython.


Logging con wxPython.
---------------------

wxWidgets mette a disposizione un sistema completo di logging, e anche wxPython lo traduce, almeno in parte. A dire il vero, da quando esiste ``logging`` nella libreria standard di Python, non c'è quasi più bisogno di ricorrere a wxPython per loggare. Tuttavia è meglio avere almeno un'idea di come funziona il logging con wxPython, per due motivi: perché in certi casi potrebbe ancora farvi comodo; e soprattutto perché, se non intervenite sui default, occasionalmente wxPython usa il suo sistema di logging per comunicare direttamente all'utente alcuni errori di sistema, con dei pop-up. In genere questo non è sbagliato: tuttavia è fuori dal vostro controllo, e se invece volete avere voce in capitolo, dovete sapere che cosa sta succedendo dietro le quinte. 

I concetti di base non sono complicati. Il sistema di log è imperniato sulla classe ``wx.Log``, che però non è direttamente necessaria per loggare con le impostazioni di default. Esistono diversi livelli di allerta, simboleggiati dalle costanti ``wx.LOG_*`` (da ``wx.LOG_FatalError`` che vale ``0`` a ``wx.LOG_Trace`` che vale ``7``). Per loggare un messaggio con il desiderato livello, si può ricorrere alle funzioni globali corrispondenti ``wx.Log*`` (da ``wx.LogFatalError`` a ``wx.LogTrace``). Questo specchietto riassuntivo dovrebbe aiutarvi a capire come funzionano le impostazioni di default::

   LOG_LABELS = ['Fatal Error', 'Error', 'Warning', 'Message', 'Status', 
                 'Verbose', 'Debug', 'Trace', 'Sys Error']
   LOG_FUNCTIONS = {
          # significato    funzione di log    
           'Fatal Error':  wx.LogFatalError,
           'Error':        wx.LogError,     
           'Warning':      wx.LogWarning,   
           'Message':      wx.LogMessage,   
           'Status':       wx.LogStatus,     # cfr anche wx.LogStatusFrame
           'Verbose':      wx.LogInfo,       # alias per wx.LogVerbose
           'Debug':        wx.LogDebug,     
           'Trace':        wx.LogTrace,     
           'Sys Error':    wx.LogSysError}
   LOG_LEVELS = {
          # significato    costante x livello    valore 
           'Fatal Error':  wx.LOG_FatalError,   # 0
           'Error':        wx.LOG_Error,        # 1 - anche per wx.LogSysError
           'Warning':      wx.LOG_Warning,      # 2
           'Message':      wx.LOG_Message,      # 3
           'Status':       wx.LOG_Status,       # 4
           'Verbose':      wx.LOG_Info,         # 5
           'Debug':        wx.LOG_Debug,        # 6
           'Trace':        wx.LOG_Trace,        # 7
           'MAX':          wx.LOG_Max,          # 10000
           }


   class MainFrame(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           p = wx.Panel(self)
           level_choices = LOG_LABELS[:-1] # a 'Sys Error' non corrisponde nessun livello
           level_choices += ['MAX'] 
           self.log_levels = wx.RadioBox(p, choices=level_choices, style=wx.VERTICAL)
           self.log_levels.Bind(wx.EVT_RADIOBOX, self.on_set_level)
           s = wx.BoxSizer(wx.HORIZONTAL)
           s.Add(self.log_levels, 1, wx.EXPAND|wx.ALL, 5)
           s1 = wx.BoxSizer(wx.VERTICAL)
           for label in LOG_LABELS:
               b = wx.Button(p, -1, 'provoca un '+label)
               b.Bind(wx.EVT_BUTTON, 
                      lambda evt, func=LOG_FUNCTIONS[label], label=label: self.do_log(evt, func, label))
               s1.Add(b, 1, wx.ALL|wx.EXPAND, 5)
           s.Add(s1, 1, wx.EXPAND)
           p.SetSizer(s)
           self.log_levels.SetSelection(4) # 'Status' -> livello di default
           self.SetStatusBar(wx.StatusBar(self))

       def on_set_level(self, evt):
           level = self.log_levels.GetItemLabel(evt.GetInt())
           wx.Log.SetLogLevel(LOG_LEVELS[level])

       def do_log(self, evt, func, label):
           func("Ecco a voi un... " + label)

   if __name__ == '__main__':
       app = wx.App(False)
       MainFrame(None).Show()
       app.MainLoop()

Alcune osservazioni e spiegazioni: 

* potete cambiare in ogni momento la soglia del logging con ``wx.Log.SetLogLevel`` (è un metodo statico, non serve istanziare prima ``wx.Log``);

* ``wx.LogVerbose`` e ``wx.LogInfo`` sono sinonimi: entrambe le funzioni loggano un messaggio con livello ``wx.LOG_Info`` (ovvero, livello ``5``);

* i livelli fino a ``wx.LOG_Status``, di default, emettono dei messaggi visibili all'utente, sotto forma di pop-up differenziati a seconda della gravità del problema. Il messaggio di ``wx.LogStatus`` è visibile nella barra di stato della finestra (nel nostro esempio qui sopra, sembra succedere solo la prima volta: poi la barra di stato non viene pulita, e i successivi messaggi non si distinguono più). Sopra ``wx.LOG_Status``, i messaggi non sono più visibili all'utente (queste sono le impostazioni di default: si possono cambiare, vedremo).

* ``wx.LogStatus`` utilizza la barra di stato della finestra attiva al momento dell'errore: se si desidera mostrare il messaggio in finestre diverse, esiste anche ``wx.LogStatusFrame``. Per esempio questo, chiamato da una finestra secondaria, scrive nella barra di stato della finestra principale::

   wx.LogStatusFrame(self.GetTopLevelParent(), 'messaggio di log')

* ``wx.LogFatalError`` è un caso speciale: si comporta come ``wx.LogError``, ma non può essere disabilitato, e mostra il messaggio all'utente chiamando la :ref:`funzione globale più sicura<chiusuraapp>` ``wx.SafeShowMessage`` invece del normale ``wx.MessageBox``. Infine, termina il programma (!) con exit code ``3``;

* ``wx.LogSysError`` si comporta come ``wx.LogError``, ma è un caso speciale. Viene usato soprattutto internamente da wxPython, e restituisce anche l'ultimo errore di sistema occorso (``errno`` su Unix, ``GetLastError`` su Windows). Sono informazioni disponibili anche attraverso le funzioni ``wx.SysErrorCode`` e ``wx.SysErrorMsg``, come vedremo meglio parlando di debugging;

.. todo:: una pagina sul debugging.

* in teoria è possibile definire livelli di log personalizzati (compresi tra ``wx.LOG_User`` e ``wx.LOG_Max``). Il problema è che siccome i livelli predefiniti vanno da ``0`` a ``7`` (e ``wx.LOG_User`` vale ``100``!) non è possibile definire livelli intermedi;

* specie se si definiscono livelli personalizzati, sarà utile usare ``wx.LogGeneric`` che, oltre al messaggio, richiede di specificare anche il livello con cui si intende registrarlo;

* ``wx.LOG_Verbose`` è un livello riservato ad eventuali messaggi più dettagliati da mostrare all'utente. Normalmente non è utilizzato, ma potrebbe essere definito da target personalizzati (vedi sotto); 

* ``wx.LOG_Debug`` e ``wx.LOG_Trace`` sono livelli di log attivi solo in debug mode, come vedremo parlando di debugging. 

.. todo:: una pagina sul debugging.


.. index:: 
   single: logging; wx.Log.Suspend
   single: wx.Log; Suspend
   single: logging; wx.Log.Resume
   single: wx.Log; Resume
   single: logging; wx.Log.Flush
   single: wx.Log; Flush
   single: logging; wx.Log.SetActiveTarget
   single: wx.Log; SetActiveTarget
   single: logging; wx.LogGui
   single: wx.LogGui
   single: logging; wx.LogWindow
   single: wx.LogWindow
   single: logging; wx.LogStderr
   single: wx.LogStderr
   single: logging; wx.LogTextCtrl
   single: wx.LogTextCtrl
   single: logging; wx.LogBuffer
   single: wx.LogBuffer

Cambiare il log target.
-----------------------

Il framework di logging wxPython ha il concetto di "log target" per indicare dove dovrebbero essere diretti i messaggi di log, in quali casi, e così via. 

Un log target è semplicemente una sotto-classe di ``wx.Log``. wxPython mette a disposizione alcuni log target già pronti, che soddisfano i casi d'uso più comuni. Il target di default, responsabile per tutti i comportamenti che abbiamo visto fin qui, è ``wx.LogGui``. Per esaminare gli altri, utilizziamo questa semplice finestra di lavoro::

   class MainFrame(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           p = wx.Panel(self)
           do_log = wx.Button(p, -1, 'emetti log', pos=(20, 20))
           do_log.Bind(wx.EVT_BUTTON, self.on_do_log)
           suspend = wx.Button(p, -1, 'sospendi log', pos=(120, 20))
           suspend.Bind(wx.EVT_BUTTON, self.on_suspend)
           resume = wx.Button(p, -1, 'riprendi log', pos=(220, 20))
           resume.Bind(wx.EVT_BUTTON, self.on_resume)
           target = wx.Button(p, -1, 'cambia target', pos=(20, 60))
           target.Bind(wx.EVT_BUTTON, self.on_target)
           restore = wx.Button(p, -1, 'ripristina target', pos=(20, 100))
           restore.Bind(wx.EVT_BUTTON, self.on_restore)

           self.actual_log = wx.Log.GetActiveTarget()

       def on_do_log(self, evt):  wx.LogWarning('un messaggio di log')
       def on_suspend(self, evt): self.actual_log.Suspend()
       def on_resume(self, evt):  self.actual_log.Resume()

       def on_target(self, evt):  pass
       def on_restore(self, evt): pass

   if __name__ == '__main__':
       app = wx.App(False)
       MainFrame(None).Show()
       app.MainLoop()

Una osservazione importante, prima di procedere: alcuni log target implementano un buffer interno in cui accumulano le scritture di log, che vengono mostrate all'utente quando periodicamente il buffer viene svuotato. Il log target di default ``wx.LogGui`` è appunto tra questi. Il buffer viene svuotato dal gestore di default dell'evento ``wx.EVT_IDLE``, che :ref:`come sappiamo<processare_manualmente_eventi>` viene emesso automaticamente quando il loop degli eventi del sistema è libero. Di conseguenza il buffer viene svuotato sempre molto rapidamente, e l'impressione per l'utente è che che il messaggio di log sia visualizzato non appena viene emesso. 

Potete tuttavia interrompere manualmente lo svuotamento del buffer chiamando ``wx.Log.Suspend``, e riprenderlo con ``wx.Log.Resume`` (e in questo intervallo, se volete, potete usare ``wx.Log.Flush`` per svuotare il buffer in momenti precisi). Nel nostro esempio, provate a cliccare sul pulsante "sospendi log": le registrazioni successive si accumulano nel buffer e vengono mostrate tutte insieme quando cliccate su "riprendi log". Dovete fare attenzione, tuttavia: ciascuna chiamata successiva a ``wx.Log.Suspend`` si accumula in uno stack: pertanto, se cliccate due volte di seguito su "sospendi log", dovete poi cliccare due volte su "riprendi log". Questo comportamento sembra bizzarro, visto nell'interfaccia del nostro esempio: ma è il nostro esempio a essere anomalo. In realtà, sospendere lo svuotamento del log dovrebbe essere considerata un'operazione temporanea (quindi, evitate di lasciare direttamente in mano all'utente questa opzione!): ci si aspetta che il componente che chiama ``wx.Log.Suspend`` si preoccupi anche di chiamare ``wx.Log.Resume`` quanto prima, per evitare che il buffer continui a riempirsi all'infinito. Lo stack di ``wx.Log.Suspend`` serve appunto a permettere che ciascun componente possa sospendere e ripristinare lo svuotamento del buffer senza preoccuparsi degli altri. 

Detto questo, esaminiamo gli altri log target disponibili, in aggiunta al predefinito ``wx.LogGui``. Il primo è ``wx.LogWindow``, che apre una finestra separata e re-indirizza il log verso quella::

    def on_target(self, evt): 
        self.actual_log = wx.LogWindow(pParent=self, szTitle='LOG', 
                                       bShow=True, bPassToOld=False)
        
    def on_restore(self, evt):
        self.actual_log = None

``wx.LogWindow`` è un log target "evoluto" che deriva da ``wx.Log`` attraverso ``wxLogInterposer`` (una classe wxWidgets che in wxPython non è tradotta). Questa aggiunta gli conferisce la capacità di mantenere un riferimento anche al precedente target, e di indirizzare i messaggi a entrambi: potete settare l'argomento ``bPassToOld`` a ``True`` per verificare. Un altro effetto gradevole, dal punto di vista di un programmatore Python, è che per usare ``wx.LogWindow`` occorre solo istanziarlo, e per tornare al log target precedente basta solo de-referenziarlo. I log target che vedremo in seguito, derivano invece direttamente da ``wx.Log`` e sono pertanto più limitati e difficili da usare.  

C'è però un difetto fastidioso in ``wx.LogWindow``: se l'utente chiude la finestra di log, questo non basta a distruggere il log target, con il risultato che non viene ripristinato il target di default. Purtroppo, impedire all'utente di chiudere la finestra non è immediato. wxWidgets mette a disposizione due hook, ``wxLogWindow::OnFrameClose`` e ``wxLogWindow::OnFrameDelete``, che sarebbero perfetti per questo scopo: tuttavia, wxPython non li esporta (è senz'altro un baco) e quindi non possiamo utilizzarli. Siamo costretti a sotto-classare::

   class MyLogWindow(wx.LogWindow):
       def __init__(self, *a, **k):
           wx.LogWindow.__init__(self, *a, **k)
           self.GetFrame().Bind(wx.EVT_CLOSE, self.on_close_frame)

       # qui in pratica _non_ chiamare Skip() impedisce la chiusura...
       def on_close_frame(self, evt): return False


   class MainFrame(wx.Frame):
      # etc. etc. come sopra

   def on_target(self, evt): 
      self.actual_log = MyLogWindow(pParent=self, szTitle='LOG', 
                                    bShow=True, bPassToOld=False)

    def on_restore(self, evt):
        # dobbiamo distruggere manualmente il frame  
        # perché il normale EVT_CLOSE è bloccato
        self.actual_log.GetFrame().Destroy()
        self.actual_log = None

Infine, ricordiamo che ``wx.LogWindow`` non usa un buffer interno: di conseguenza ``wx.Log.Suspend`` non ha effetto. 

Un altro log target utile è ``wx.LogTextCtrl``: questo target *non è documentato* ma, come suggerisce il nome, re-indirizza il log verso un ``wx.TextCtrl`` multilinea. Per usarlo, aggiungiamo quindi una casella di testo al nostro frame di esempio::

   class MainFrame(wx.Frame):
       def __init__(self, *a, **k):
           # etc. etc. come sopra 
           self.logtxt = wx.TextCtrl(p, pos=(20, 140), size=(300, 100), 
                                     style=wx.TE_MULTILINE|wx.TE_READONLY)

       def on_target(self, evt): 
           self.actual_log = wx.LogTextCtrl(self.logtxt)
           self.old_target = wx.Log.SetActiveTarget(self.actual_log)
           
       def on_restore(self, evt):
           wx.Log.SetActiveTarget(self.old_target)

Come preannunciato, ``wx.LogTextCtrl`` deriva direttamente da ``wx.Log``, e quindi è un po' più difficile da creare e distruggere. Occorre passare da ``wx.Log.SetActiveTarget``, un metodo che convenientemente restituisce un riferimento al target precedente, che possiamo poi usare al momento di ripristinare il log di default. Ricordiamo poi che neppure ``wx.LogTextCtrl`` fa uso di un buffer interno. 

``wx.LogStderr`` invia le scritture del log verso lo standard error, e il suo uso è del tutto analogo al precedente:: 

    def on_target(self, evt): 
        self.actual_log = wx.LogStderr()
        self.old_target = wx.Log.SetActiveTarget(self.actual_log)

    def on_restore(self, evt):
        wx.Log.SetActiveTarget(self.old_target)

In wxWidgets, ``wx.LogStderr`` è perfettamente in grado di indirizzare il log verso un qualsiasi file stream: basta passare al costruttore il riferimento di un file aperto. Purtroppo però wxPython non offre questa possibilità (un altro baco...), e questo ne limita parecchio l'utilità.

Infine, ``wx.LogBuffer`` invia semplicemente il log a un buffer interno, che si svuota a ogni ``wx.EVT_IDLE``: le scritture in coda vengono mostrate all'interno di un pop-up generico. L'effetto per l'utente è simile a quello del normale ``wx.LogGui``, ma senza i pop-up differenziati per livello di allarme. Siccome c'è un buffer dietro le quinte, possiamo usare ``wx.Log.Suspend`` e ``wx.Log.Resume`` all'occorrenza::

    def on_target(self, evt): 
        self.actual_log = wx.LogBuffer()
        self.old_target = wx.Log.SetActiveTarget(self.actual_log)

    def on_restore(self, evt):
        wx.Log.SetActiveTarget(self.old_target)


.. index:: 
   single: logging; wx.LogNull
   single: wx.LogNull

Sopprimere il log con ``wx.LogNull``.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``wx.LogNull`` è un log target particolare, che ha l'effetto di sopprimere ogni tipo di log. Il suo utilizzo è elementare::

    def on_target(self, evt): 
        self.actual_log = wx.LogNull()

    def on_restore(self, evt):
        self.actual_log = None

Come abbiamo già visto per ``wx.LogWindow``, per ripristinare il precedente log target basta de-referenziare l'istanza di ``wx.LogNull``. 

``wx.LogNull`` va usato con cautela. A differenza di ``wx.Log.Suspend``, che vi consente comunque di recuperare le scritture sul log in un secondo momento, questa classe disabilita completamente ogni tipo di logging. Se per esempio un errore di sistema (lato wxWidgets) dovesse accadere nel periodo "scollegato", wxPython non potrebbe mostrarlo all'utente nel consueto pop-up, né registrarlo in alcun modo (a meno che l'errore non sia così grave da terminare il programma, certo).


.. index:: 
   single: logging; wx.PyLog
   single: wx.PyLog
   single: logging; wx.PyLog.DoLogRecord
   single: wx.PyLog; DoLogRecord
   single: logging; wx.PyLog.DoLogRecordAtLevel
   single: wx.PyLog; DoLogRecordAtLevel
   single: logging; wx.PyLog.DoLogText
   single: wx.PyLog; DoLogText

Scrivere un log target personalizzato.
--------------------------------------

Non è difficile scrivere un log target a partire da zero: è semplicemente una sotto-classe di ``wx.Log`` (che però voi dovete sotto-classare nella versione Python-friendly ``wx.PyLog``). Ci sono tre metodi che potete sovrascrivere:

* ``wx.PyLog.DoLogRecord``, è la prima funzione, nell'ordine, che viene chiamata quando loggate, e si occupa di formattare il messaggio. L'implementazione di default si limita ad aggiungere data e ora, e passare la stringa a ``wx.PyLog.DoLogTextAtLevel``;

* ``wx.PyLog.DoLogTextAtLevel``, differenzia il comportamento a seconda dei livelli di allarme. L'implementazione di default indirizza i livelli ``wx.LOG_Trace`` e ``wx.LOG_Debug`` all'output di debug del sistema, e spedisce tutto il resto a ``wx.PyLog.DoLogText``;

* ``wx.PyLog.DoLogText`` esegue effettivamente la scrittura di log.

Potete quindi sovrascrivere questi metodi, a seconda del tipo di personalizzazione di cui avete bisogno: nei casi più semplici, re-implementare ``wx.PyLog.DoLogText`` potrebbe essere sufficiente. Volendo, tuttavia, potete intervenire alla radice.


Unificare il log wxPython e il log Python.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Armati di questa conoscenza, possiamo scrivere un log target personalizzato che scrive direttamente su un log Python. Ecco un approccio minimalistico:: 

   WXLOG_TO_PYLOG = {
       wx.LOG_FatalError: logging.critical, # non funziona! vedi sotto...
       wx.LOG_Error:      logging.error,
       wx.LOG_Warning:    logging.warning,
       wx.LOG_Message:    logging.info,
       wx.LOG_Status:     logging.info,
       wx.LOG_Info:       logging.info,
       wx.LOG_Debug:      logging.debug,
                    }

   class MyLogTarget(wx.PyLog):
       def DoLogRecord(self, level, msg, info=None):
           msg = '[da wxPython] ' + msg
           WXLOG_TO_PYLOG[level](msg)

   class MyFrame(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           b = wx.Button(self, -1, 'clic')
           b.Bind(wx.EVT_BUTTON, self.on_clic)

       def on_clic(self, evt):
           # provate anche altri livelli: wx.LogError, wx.LogWarning etc.
           wx.LogMessage('prova di log')

   class MyApp(wx.App):
       def OnInit(self):
           logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                               format='%(asctime)s %(levelname)s: %(message)s')
           wx.Log.SetActiveTarget(MyLogTarget())
           return True

   if __name__ == '__main__':
       app = MyApp(False)
       MyFrame(None).Show()
       app.MainLoop()

Abbiamo scritto un semplice log target che traduce i livelli di log wxPython nelle corrispondenti funzioni del modulo ``logging``. La formattazione dei messaggi è curata solo da ``logging.basicConfig``: siccome abbiamo sovrascritto ``wx.PyLog.DoLogRecord``, la formattazione di ``wx.Log`` è completamente annullata. Potete sperimentare diversi livelli di logging: notate in particolare che adesso potete anche loggare con ``wx.LogInfo`` e ``wx.LogDebug``; e notate che ``wx.LogSysError`` continua ad aggiungere al messaggio anche l'indicazione dell'ultimo errore di sistema riscontrato. 

Questo esempio è già un buon punto di partenza: tuttavia, in un programma vero la vostra strategia di logging dovrà essere più complessa. Per esempio, potreste voler usare un logger Python separato per i messaggi che provengono da wxPython. 


Perché conviene sempre usare un log target personalizzato.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Scrivere e usare un log target personalizzato è probabilmente la cosa migliore da fare, in un'applicazione wxPython "seria". Non è soltanto una questione di display dei messaggi (dirottarli su un log Python invece che mostrarli all'utente, per esempio). Il fatto è che, :ref:`come spieghiamo meglio altrove<eccezioni2>`, wxWidgets non usa le eccezioni (le eccezioni C++, naturalmente) per segnalare condizioni di errore: molto spesso solleva degli "assert" interni, che wxPython cattura e trasforma in ``wx.PyAssertionError``. Ma altrettanto spesso utilizza ``wx.LogSysError`` per notificare il problema all'utente, e in questo caso noi non abbiamo nessuna opportunità di intervenire. 

Di conseguenza, un log target personalizzato è l'unica strada per intercettare in qualche modo un ``wx.LogSysError``. Si tratta di uno strumento molto impreciso (difficile, per esempio, rintracciare il punto esatto in cui si è verificato l'errore), ma è meglio di niente. Possiamo almeno inserire un po' di logica Python nel nostro log target, per reagire in modo speciale a un errore grave::

   class MyLogTarget(wx.PyLog):
       def DoLogRecord(self, level, msg, info=None):
           msg = '[da wxPython] ' + msg
           WXLOG_TO_PYLOG[level](msg)
           if level == wx.LOG_Error:
               # qui possiamo chiedere all'utente di salvare
               # e chiudere, per esempio, o procedere direttamente
               # con wx.Exit() o qualche routine personalizzata...

Anche così, ci sono almeno due limitazioni fastidiose:

- non c'è modo di distinguere tra ``wx.LogError`` e ``wx.LogSysError`` (entrambi usano lo stesso livello di log ``wx.LOG_Error``, purtroppo). Questo però non è grave: ``wx.LogError`` non è usato internamente da wxPython, e di sicuro non lo userete nemmeno voi (perché tutte le vostre scritture avverranno tramite il ``logging`` di Python, chiaramente!). Quindi, se il vostro log target intercetta un log di livello ``wx.LOG_Error``, sicuramente deve trattarsi di un grave ``wx.LogSysError`` proveniente da wxPython;

- purtroppo, ``wx.LogFatalError`` continua ad essere un caso a parte: lo abbiamo incluso nel nostro esempio qui sopra, ma in realtà il comportamento di default non può essere cambiato (provate). Questo vuol dire che wxPython continuerà a mostrare un messaggio all'utente e chiudere l'applicazione, che vi piaccia o no. Anche questo non è così grave: se wxPython si imbatte in un problema tale da richiedere ``wx.LogFatalError``, allora vuol dire che chiudere l'applicazione è comunque la cosa migliore. 

.. _wxlog_utile:

Quando il log di wxPython è utile.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Scrivere un log target specializzato che dirotta i messaggi verso il log di Python è probabilmente la cosa migliore da fare. Talvolta però il comportamento di default del log di wxPython (ovvero, il log target predefinito ``wx.LogGui``) potrebbe essere desiderabile. 

Per esempio, sappiamo già che wxPython può utilizzare ``wx.LogSysError`` per mostrare all'utente un messaggio quando si verifica una condizione di errore interno. Vediamo un esempio concreto: quando provate a costruire una ``wx.Bitmap`` a partire da un file "sbagliato" (inesistente o corrotto), wxPython emette un messaggio di log che contiene utili informazioni sull'errore, e lo mostra all'utente (in realtà ci sono delle sottigliezze che qui non consideriamo: approfondiremo ancora proprio questo esempio :ref:`parlando di eccezioni<pyassertionerror>`). Provate a sostituire, nell'esempio di sopra::

    # (...)
    def on_clic(self, evt):
        wx.Bitmap('non_esiste.bmp', type=wx.BITMAP_TYPE_ANY)

e commentate la riga ``wx.Log.SetActiveTarget(MyLogTarget())`` per tornare al normale log di wxPython. Quando fate clic sul pulsante, wxPython vi mostrerà un messaggio di errore. Se adesso ripristinate il nostro log target personalizzato, le informazioni sull'errore finiranno nel log di Python, ma il messaggio di errore non verrà più visualizzato. 


.. index:: 
   single: logging; wx.LogChain
   single: wx.LogChain

Usare contemporaneamente due log target.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In casi del genere, non è difficile aggiungere ancora un po' di logica nel nostro log target specializzato, per recuperare il messaggio di ``wx.LogSysError`` e mostrarlo all'utente in un ``wx.MessageBox``, ricostruendo in questo modo il comportamento di ``wx.LogGui``. Non è forse la soluzione più elegante, ma così non vi complicate troppo la vita. 

In alternativa, il log di wxPython ha il supporto per i log target multipli, proprio come il modulo ``logging`` di Python. Per inviare un messaggio a due target separati, dovete usare la classe apposita ``wx.LogChain``. Purtroppo in wxPython l'uso di questo strumento è reso un po' complicato dalla necessità di separare gli oggetti proxy Python dai corrispondenti oggetti C++: si tratta probabilmente di un vero e proprio baco, per giunta non documentato. Senza scendere troppo nel dettaglio, mostriamo un esempio funzionante di come si può usare ``wx.LogChain`` per dirigere il log contemporaneamente a ``wx.LogGui`` e al nostro log target specializzato (che a sua volta lo indirizza al log di Python)::

    class MyApp(wx.App):
        def OnInit(self):
            logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s: %(message)s')
            # attiviamo prima il target wx.LogGui
            wx.Log.SetActiveTarget(wx.LogGui())
            # creiamo il nostro log target...
            log = MyLogTarget()
            # ... e lo aggiungiamo alla catena
            log_chain = wx.LogChain(log)
            # separiamo i proxy Python dagli oggetti C++ sottostanti
            log.this.disown()
            log_chain.this.disown()
            # "log" e "log_chain" saranno subito reclamati dal garbage collector Python
            # ma gli oggetti C++ saranno distrutti da wxWidgets separatamente 
            # al momento giusto
            return True

Se provate questa versione di ``wx.App`` con il codice dell'esempio precedente, noterete che i messaggi di log sono effettivamente indirizzati sia al log di Python (attraverso il log target personalizzato ``MyLogTarget``), sia al log di wxPython (che in questo caso è ``wx.LogGui``, ma potete anche scegliere un log target diverso). La danza un po' goffa delle due chiamate a ``this.disown`` è necessaria per risparmiarsi la fatica di dover capire quando esattamente occorre distruggere gli oggetti proxy Python. ``this`` è un riferimento all'oggetto C++ collegato, e ``disown`` scollega il proxy Python (che quindi può essere distrutto senza che l'oggetto C++ sia interessato).

.. todo:: una pagina su SWIG e l'oop Python/C++.


Il conclusione: come loggare in wxPython.
-----------------------------------------

Se avete letto questa e :ref:`la precedente pagina<logging>` sul log, dovreste avere gli strumenti per implementare una strategia di logging adatta alle vostre esigenze. 

Sarebbe questo il momento di dare qualche consiglio pratico riassuntivo prima di abbandonare definitivamente l'argomento. Siccome tuttavia il problema del logging in wxPython è strettamente intrecciato con il problema della gestione delle eccezioni, preferiamo raccogliere queste indicazioni :ref:`al termine del discorso sulle eccezioni<consigli_finali_log_eccezioni>`. 
