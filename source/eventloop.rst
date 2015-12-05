.. _eventloop:

.. index::
   single: eventi; loop degli eventi
   single: loop degli eventi
   single: wx.App; MainLoop
   single: wx.EventLoop (alias per GUIEventLoop)
   single: wx.GUIEventLoop
   single: wx.EventLoopBase
   single: loop degli eventi; wx.EventLoop (alias per GUIEventLoop)
   single: loop degli eventi; wx.GUIEventLoop
   single: loop degli eventi; wx.EventLoopBase

Il loop degli eventi.
=====================

Abbiamo già :ref:`dedicato<eventibasi>` :ref:`molte<eventi_avanzati>` :ref:`pagine<eventitecniche>` :ref:`agli<eventitecniche2>` :ref:`eventi<ricette_checkpass_button>`: ma non abbiamo ancora mai indagato sul cuore nascosto della nostra applicazione wxPython: il luogo dove gli eventi arrivano e vengono accoppiati ai loro handler, che a loro volta si incaricheranno di cercare i callback corrispondenti.

Stiamo parlando del loop degli eventi. 

.. note:: Tutto ciò che leggerete in questa pagina è... molto sperimentale. Metteremo le mani sotto il cofano del modello a eventi di wxPython, e finiremo per modificare comportamenti di default molto sensati, meditati e testati. Per giunta, qui la documentazione scarseggia: anche in rete si trovano solo indicazioni vaghe e incomplete (ogni segnalazione in contrario è benvenuta!). Alcune delle informazioni qui raccolte in pratica si trovano solo leggendo il (labirintico) codice sorgente di wxWidgets. Se volete usare queste tecniche, vi raccomandiamo di prendere queste note solo come orientamente iniziale, di sperimentare e approfondire molto per conto vostro, e di testare a lungo il codice che scrivete. 

Il loop degli eventi e il main loop dell'applicazione.
------------------------------------------------------

Per prima cosa dobbiamo chiarire una possibile confusione di termini. Quando :ref:`abbiamo parlato<wxapp_basi>` della ``wx.App``, abbiamo descritto il suo ``MainLoop`` come "un grande ciclo ``while True`` senza fine che si occupa di gestire gli eventi". In realtà, questa definizione confonde main loop e loop degli eventi ("event loop", detto anche loop dei messaggi, "message loop"): al momento era una piccola inesattezza senza conseguenze, ma adesso dobbiamo fare più attenzione. 

``wx.App.MainLoop``, in effetti, è semplicemente un metodo di ``wx.App``: che viene invocato di solito una volta sola, all'inizio della vita della vostra applicazione wxPython. Al suo interno, crea e avvia un event loop per gestire gli eventi man mano che appaiono. E quindi, che cosa è di preciso un event loop? E' un'istanza della classe ``wx.GUIEventLoop``.

.. note:: Una piccola ulteriore confusione terminologica: ``GUIEventLoop`` deriva da ``EventLoopBase``, ma senza estenderne le funzionalità. La documentazione di ``GUIEventLoop`` rimanda semplicemente a quella di ``EventLoopBase``. Nelle vecchie versioni di wxPython, ``GUIEventLoop`` era però chiamata ``EventLoop``: per questa ragione, vedete ancora moltissimo codice in giro che usa ``EventLoop``. Nessun problema, però: ``EventLoop`` esiste ancora per retrocompatibilità, ed è ormai solo un alias di ``GUIEventLoop``. In queste note useremo il nome "moderno". 

.. _processare_manualmente_eventi:

.. index:: 
   single: wx.GUIEventLoop; Pending
   single: wx.GUIEventLoop; Dispatch
   single: wx.GUIEventLoop; ProcessIdle
   single: wx.GUIEventLoop; Run
   single: wx.EVT_IDLE
   single: wx.MilliSleep
   single: loop degli eventi; wx.GUIEventLoop.Pending
   single: loop degli eventi; wx.GUIEventLoop.Dispatch
   single: loop degli eventi; wx.GUIEventLoop.ProcessIdle
   single: loop degli eventi; wx.GUIEventLoop.Run
   single: loop degli eventi; wx.EVT_IDLE
   single: eventi; wx.EVT_IDLE

Processare manualmente gli eventi.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Naturalmente voi potete sovrascrivere ``wx.App.MainLoop``: ma dovete impegnarvi a creare voi stessi e "far girare" un loop, altrimenti la vostra applicazione non potrà rispondere agli eventi. Il vostro compito minimo potrebbe essere::

  class MyApp(wx.App):
      def MainLoop(self):
          loop = wx.GUIEventLoop()
          loop.Run()

Questa però è solo una perdita di tempo: vi siete limitati a replicare quello che l'implementazione standard di ``MainLoop`` farebbe in ogni caso. Anzi, in questo modo avete perso il meccanismo che esce da ``MainLoop`` e chiude la vostra applicazione quando :ref:`non ci sono più finestre top level aperte<chiusuraapp>`: se provate a far girare una gui qualsiasi con questa ``MyApp``, vedrete che wxPython non termina mai (preparatevi a usare ``ctrl-c`` nella shell, o a terminare il processo in qualche modo). 

Tuttavia questo è almeno un inizio: abbiamo imparato a creare un event loop, e ad avviarlo con ``Run``. A questo proposito, va detto che ``Run`` si prende cura di fare il lavoro al posto vostro, ma è proprio l'opposto di quel che stiamo cercando: noi vogliamo gestire gli eventi "manualmente"! Facciamo un passo avanti::

  class MyApp(wx.App):
      def MainLoop(self):
          loop = wx.GUIEventLoop()
          while True:
              while loop.Pending():
                  loop.Dispatch()
              loop.ProcessIdle()

Ecco che cominciamo a prendere il controllo: abbiamo abbandonato ``Run`` e facciamo tutto noi. Il segreto è chiamare ``Dispatch``, metodo che attende l'arrivo di un evento, e si occupa di accoppiarlo al suo primo handler. Siccome ``Dispatch`` è bloccante (aspetta fin quando non c'è un evento da gestire), in genere conviene accoppiarlo con ``Pending``, che ci dice se ci sono eventi in coda in attesa di essere processati. Quando abbiamo finito di gestire gli eventi in coda chiamiamo ``ProcessIdle``, che emette un ``wx.EVT_IDLE`` per segnalare che il loop è attualmente disoccupato. Emettere di tanto in tanto un ``wx.EVT_IDLE`` è necessario, perché in wxPython ci sono dei gestori di default che intercettano questo evento e ne approfittano per fare operazioni di servizio nei tempi morti. 

Dobbiamo ancora occuparci del meccanismo di chiusura dell'applicazione: qui possiamo inventarci strategie diverse, a seconda delle nostre esigenze specifiche. Ma anche un approccio brutale può bastare::

  class MyApp(wx.App):
      def MainLoop(self):
          loop = wx.GUIEventLoop()
          while True:
              while loop.Pending():
                  loop.Dispatch()
              if self.GetTopWindow() == None:
                  wx.Exit()
              loop.ProcessIdle()

Chiamare ``wx.Exit`` è un modo :ref:`raffinato abbastanza<wxexit>` da permettere l'esecuzione di eventuale codice in ``wx.App.OnExit``, quindi le buone maniere sono salve. Ma a dire il vero, non ha comunque molta importanza. Siccome stiamo facendo tutto "a mano", alla peggio potremmo chiamare direttamente anche ``OnExit`` e/o qualsiasi funzione di cleanup necessaria, prima di chiudere. 

Piuttosto, è il test ``GetTopWindow() == None`` che potrebbe essere fragile in certi corner-case. Abbiamo visto :ref:`mille modi<chiusura>` in cui una finestra potrebbe non chiudersi davvero, e altri :ref:`mille modi<finestre_toplevel>` in cui si possono manipolare le finestre top-level. Tuttavia, se mantenete un minimo di organizzazione nel vostro codice, non dovrebbe essere difficile stabilire quando effettivamente è ora di spegnere le luci e chiudere il locale. 

Infine, ancora una raffinatezza: abbiamo organizzato le nostre chiamate nell'ordine giusto, in modo che ``wx.Exit`` possa intervenire solo quando non ci sono più eventi da processare: non si sa mai.

Un'altra tecnica per fare la stessa cosa, sarebbe naturalmente quella di usare un flag::

  class MyApp(wx.App):
      def OnInit(self):
          self.time_to_quit = False
          return True

      def MainLoop(self):
          loop = wx.GUIEventLoop()
          while not self.time_to_quit:
              while loop.Pending():
                  loop.Dispatch()
              loop.ProcessIdle()
          wx.Exit()

In questo modo evitiamo di chiamare ``GetTopWindow`` a ogni ciclo, e ci guadagnamo in velocità. Quando volete uscire, dovete ricordarvi di settare il flag: per esempio, intercettando il ``wx.EVT_CLOSE`` della finestra principale::

  def on_close(self, evt):
      wx.GetApp().time_to_quit = True

Questo vi assicura di uscire dall'applicazione appena esaurita la coda corrente degli eventi da processare. 

Infine, ancora un dettaglio di cui forse vi sarete già accorti, se avete... prestato orecchio alla ventola del vostro computer! Il problema è che wxPython, quando è al comando, si preoccupa di dosare il consumo della vostra cpu: ma il nostro ``while True`` senza alcuna moderazione finisce per occupare il processore quasi al 100% (solo ``ProcessIdle`` rallenta un po' le cose). Prima di prosciugare le risorse del nostro computer per niente, sarà meglio correre ai ripari::

  # se non volete importare time, usate wx.MilliSleep()
  import time 

  class MyApp(wx.App):
      def OnInit(self):
          self.time_to_quit = False
          return True

      def MainLoop(self):
          loop = wx.GUIEventLoop()
          while not self.time_to_quit:
              while loop.Pending():
                  loop.Dispatch()
              loop.ProcessIdle()
              time.sleep(0.1) # un po' di sollievo per la cpu
              # wx.MilliSleep(10)
          wx.Exit()

.. index:: 
   single: wx.GUIEventLoop; Pending
   single: wx.GUIEventLoop; IsRunning
   single: wx.GUIEventLoop; Exit
   single: wx.GUIEventLoop; IsMain
   single: wx.GUIEventLoop; GetActive
   single: wx.GUIEventLoop; SetActive
   single: loop degli eventi; wx.GUIEventLoop.Pending
   single: loop degli eventi; wx.GUIEventLoop.IsRunning
   single: loop degli eventi; wx.GUIEventLoop.Exit
   single: loop degli eventi; wx.GUIEventLoop.IsMain
   single: loop degli eventi; wx.GUIEventLoop.GetActive
   single: loop degli eventi; wx.GUIEventLoop.SetActive
   single: loop degli eventi; wx.App.GetMainLoop
   single: loop degli eventi; wx.App.OnEventLoopEnter
   single: loop degli eventi; wx.App.OnEventLoopExit
   single: wx.App; GetMainLoop
   single: wx.App; OnEventLoopEnter
   single: wx.App; OnEventLoopExit

Altre cose da sapere sul loop degli eventi.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Un loop degli eventi (``wx.GUIEventLoop``) ha alcuni metodi che possono tornare utili, oltre a quelli che abbiamo già visto. In primo luogo, ``IsRunning`` permette di sapere se il loop è al momento quello attivo (come vedremo presto, ci possono essere diversi event loop allo stesso tempo... complicazioni in vista!). Se avete avviato il loop con ``Run``, potete chiamare ``Exit`` per uscire dal loop (questo non distrugge l'istanza del loop, naturalmente): sarà meglio subito avviare un altro loop, altrimenti la vostra applicazione resterà sospesa. 

``wx.App.GetMainLoop()`` restituisce un riferimento al loop degli eventi "principale", ossia quello che è stato creato da wxPython in ``wx.App.MainLoop``. Va da sé che, se avete scritto un loop per conto vostro, allora ``GetMainLoop`` resituirà ``None``... poco male: basta conservare un riferimento all'istanza del vostro loop e recuperarla all'occorrenza.

Similmente, anche ``wx.GUIEventLoop.IsMain()`` restituisce ``True`` solo se il loop è stato creato da wxPyhton in fase di inizializzazione. 

Infine, anticipiamo qui il concetto di "attivazione" dei loop, che riprenderemo tra poco, parlando degli event loop secondari (qualche ripetizione sarà inevitabile, a quel punto): i metodi che si occupano di questo aspetto sono ``wx.GUIEventLoop.GetActive`` e ``wx.GUIEventLoop.SetActive``. In realtà l'attivazione di un loop è una questione poco più che simbolica. Quando chiamate ``SetActive``, l'unico cambiamento che avviene è l'impostazione di un flag interno. 

Tuttavia, ``SetActive`` chiama contestualmente anche ``wx.App.OnEventLoopEnter``, che è un altro degli hook della ``wx.App`` che potete sovrascrivere. A differenza di ``OnInit`` che :ref:`abbiamo già visto<wxapp_avanzata>`, ``OnEventLoopEnter`` può essere sfruttato per eseguire codice che ha bisogno di un loop già funzionante (ovvero, che ha bisogno di postare degli eventi nella coda). Si noti inoltre che ``OnEventLoopEnter`` viene chiamato *ogni volta* che si entra in un nuovo loop degli eventi (come vedremo presto, possono esserci più loop nella vita di un'applicazione wxPython). Se vi serve eseguire codice solo una volta all'inizio, potete testare se il loop è ``IsMain``. Simmetricamente, quando uscite da un loop degli eventi (chiamando ``Exit`` come vedremo tra poco), viene chiamato ``wx.App.OnEventLoopExit`` che potete sovrascrivere. 

In definitiva, "attivare" un loop può essere completamente inutile. Conviene però sempre farlo, per uniformità e perché wxPython "se lo aspetta" (nel senso che altre parti del codice potrebbero testare ``GetActive`` e prendere delle decisioni di conseguenza). Si può attivare un loop appena creato chiamando ``SetActive`` prima di avviarlo (``Run``). Tuttavia la cosa migliore è servirsi dell'apposito helper ``wx.EventLoopActivator``, della cui funzione parleremo tra poco, a proposito dei loop secondari. 

Per quanto riguarda ``GetActive``, ricordiamo infine che si tratta di un metodo di classe, e che quindi va usato semplicemente così::

  wx.GUIEventLoop.GetActive() # restituisce l'istanza del loop attivo

.. _yield_etc:

.. index:: 
   single: wx.GUIEventLoop; Yield
   single: wx.App; Yield
   single: wx.Yield (deprecato, usare wx.App.Yield) 
   single: wx.App; SafeYield
   single: wx.SafeYield
   single: wx.GUIEventLoop; IsYielding
   single: wx.GUIEventLoop; YieldFor
   single: loop degli eventi; wx.GUIEventLoop.IsYielding
   single: loop degli eventi; wx.GUIEventLoop.YieldFor
   single: eventi; wx.GUIEventLoop.Yield
   single: eventi; wx.App.Yield
   single: eventi; wx.Yield (deprecato, usare wx.App.Yield) 
   single: eventi; wx.App.SafeYield
   single: eventi; wx.SafeYield
   single: eventi; wx.GUIEventLoop.IsYielding
   single: eventi; wx.GUIEventLoop.YieldFor

``Yield`` e i suoi compagni.
----------------------------

A proposito di loop degli eventi, un discorso a parte merita ``Yield``. Intanto diciamo che questo è un metodo di ``wx.GUIEventLoop`` (la classe madre degli event loop), ma è anche gemello della funzione globale ``wx.Yield`` (che però è ormai deprecata) e del metodo ``wx.App.Yield``: potete usarli indifferentemente. 

La funzione di ``Yield`` è di passare subito a processare i successivi eventi in coda, se ce ne sono. Questo è utile quando la risposta a un evento (callback) rischia di metterci molto tempo e bloccare la gui. 

Un esempio chiarirà meglio::

  def long_op(): time.sleep(0.1)
  
  class Test(wx.Frame): 
      def __init__(self, *a, **k): 
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b1 = wx.Button(p, -1, 'clic', pos=((50, 50)))
          b2 = wx.Button(p, -1, 'clic', pos=((50, 80)))
          b1.Bind(wx.EVT_BUTTON, self.clic_b1)
          b2.Bind(wx.EVT_BUTTON, self.clic_b2)
  
      def clic_b1(self, evt):
          evt.GetEventObject().Enable(False)
          for i in xrange(100): 
              wx.GetApp().Yield()
              long_op()
          evt.GetEventObject().Enable(True)
  
      def clic_b2(self, evt): 
          print 'clic'
  
  app = wx.App(False)
  Test(None).Show()
  app.MainLoop()

L'efficacia di ``Yield`` dipende da quanto spesso riuscite a chiamarlo, ovvero da quanto riuscite a "spezzettare" la vostra operazione bloccante. Nel nostro esempio, potete sperimentare con diverse durate di ``long_op`` per vedere fino a quando la gui risponde in modo accettabile. 

Se riuscite a segmentare adeguatamente l'operazione bloccante, ``Yield`` potrebbe essere un primo tentativo per integrare task secondari in modo "asincrono" (senza ricorrere a thread separati), o addirittura per :ref:`integrare loop esterni dentro wxPython<integrazione_event_loop>` (un problema di design piuttosto comune). 

.. todo:: una pagina sui thread

Usando ``Yield``, occorre ricordare che è vietato chiamarlo ricorsivamente: per questo, nel nostro esempio, abbiamo dovuto disabilitare il pulsante, mentre l'operazione è in corso. Provate a eliminare questa precauzione, e cliccare due volte in successione sul pulsante: otterrete un ``PyAssertionError``. C'è anche un altro modo per evitare questo problema: chiamare ``Yield`` con il parametro ``onlyIfNeeded=True`` (è ``False`` per default). Provate a togliere le righe di codice che dis/abilitano il pulsante, e sostituire la chiamata con ``wx.GetApp().Yield(True)``. Non otterrete più nessun errore, ma naturalmente questo non vuole ancora dire che siete a posto: nel nostro caso, chiamare ricorsivamente l'operazione bloccante genera un sovraccarico sufficiente per bloccare comunque la gui, e ``Yield`` non può farci nulla. 

Questo ci insegna la lezione più importante: ``Yield`` può consentire di sbloccare la gui mentre un'operazione altrimenti bloccante viene processata in background: ma non è detto che l'utente farà buon uso di questa possibilità. E' importante capire quali sono le attività che l'utente non può svolgere finché dura l'operazione lunga, e disabilitare menu e pulsanti per evitare inconsistenze. 

Per questa ragione, talvolta è preferibile usare invece ``wx.App.SafeYield`` (che è anche disponibile come funzione globale ``wx.SafeYield``, ma non come metodo di ``wx.GUIEventLoop``). Questo metodo si comporta come ``Yield``, ma vuole due argomenti: il secondo è il già noto ``onlyIfNeeded`` (con la differenza che questa volta è obbligatorio). Il primo argomento, invece, può essere ``None``: in questo caso ``SafeYield`` blocca tutte le interazioni con l'interfaccia prima di procedere con l'operazione, e le sblocca di nuovo alla fine. Se invece passate come primo argomento un riferimento a un widget (un'intera finestra, se volete), allora solo le interazioni con questo widget resteranno attive, permettendo quindi un utilizzo limitato finché dura l'operazione "bloccante". 

Se la protezione di ``SafeYield`` non vi basta, potete implementare una logica più raffinata per decidere se, cosa e quando bloccare l'interfaccia, testando il metodo ``wx.GUIEventLoop.IsYielding``. Questo metodo restituisce ``True`` solo se è chiamato dall'interno di un ``Yield`` (o ``YieldFor``, che discuteremo tra poco). Per rendervene conto, nell'esempio di sopra provate a sostituire ``print 'clic'`` nel callback del secondo pulsante con::

  print wx.GetApp().GetMainLoop().IsYielding()

Adesso, se cliccate sul secondo pulsante mentre il primo "sta lavorando", otterrete ``True``. 

Un'altra implementazione raffinata di ``Yield`` è ``YieldFor``, che si comporta come ``Yield`` con ``onlyIfNeeded=True``, e inoltre accetta come parametro una bitmask di :ref:`categorie di eventi<categorie_eventi>` da processare subito: quindi, solo gli eventi che non appartengono a quelle categorie verranno ritardati. E' facile vederlo in azione nel nostro esempio, basta sostituire la chiamata a ``Yield`` con::

  wx.GetApp().GetMainLoop().YieldFor(wx.wxEVT_CATEGORY_NATIVE_EVENTS)

Questa soluzione (la più frequente) permette di processare subito gli eventi "locali" importanti, lasciando fuori quelli che provengono da thread o altre fonti "ritardabili" (nel caso del nostro esempio non ci sarà ovviamente nessun effetto visibile). 

Ricordatevi che non è possibile processare separatamente ``wx.wxEVT_CATEGORY_UI`` e ``wx.wxEVT_CATEGORY_USER_INPUT`` con ``YieldFor`` (si è visto che portava a troppe complicazioni): bisogna per forza usare il raggruppamento ``wx.wxEVT_CATEGORY_NATIVE_EVENTS``. Notate anche che ``YieldFor(wx.wxEVT_CATEGORY_ALL)`` è equivalente semplicemente a ``Yield(onlyIfNeeded=True)``. 

Ricordatevi infine che ``YieldFor`` è disponibile solo come metodo di ``wx.GUIEventLoop``. 

.. index:: 
   single: wx.GUIEventLoop; Yield
   single: wx.EventLoopActivator
   single: wx.GUIEventLoop; Exit
   single: wx.GUIEventLoop; GetActive
   single: wx.GUIEventLoop; SetActive
   single: wx.App; OnEventLoopEnter
   single: wx.App; OnEventLoopExit
   single: wx.Dialog; ShowModal
   single: loop degli eventi; stack dei loop
   single: loop degli eventi; wx.GUIEventLoop.Yield
   single: loop degli eventi; wx.EventLoopActivator
   single: loop degli eventi; wx.GUIEventLoop.Exit
   single: loop degli eventi; wx.GUIEventLoop.GetActive
   single: loop degli eventi; wx.GUIEventLoop.SetActive
   single: loop degli eventi; wx.App.OnEventLoopEnter
   single: loop degli eventi; wx.App.OnEventLoopExit

Loop secondari.
---------------

Finora abbiamo parlato sempre e solo di "un" event loop, ma la realtà è più complicata. Nella vita di un'applicazione wxPython è possibile avere più loop compresenti: wxPython mantiene uno stack di loop degli eventi "innestati" uno dentro l'altro: solo il loop in cima allo stack è attivo. Quando si esce da un loop, il controllo ritorna al loop precedente, e così via. 

Anche senza nessun intervento da parte vostra, questo avviene per esempio tutte le volte che mostrate un dialogo "modale" (ossia un dialgo che disattiva tutti gli altri componenti della vostra applicazione finché non lo chiudete). Per implementare un dialogo modale, wxPython crea e avvia un nuovo loop degli eventi, che finisce quindi in cima allo stack. Quando il dialogo è distrutto, il nuovo loop termina e viene espulso dallo stack, facendo tornare il controllo al loop precedente. Naturalmente nulla vieta che nel dialogo modale ci sia, per esempio, un pulsante che apre un nuovo dialogo modale: lo stack dei loop può crescere in teoria all'infinito. 

Facciamo una prova veloce::

  class TestDialog(wx.Dialog):
      def __init__(self, *a, **k):
          wx.Dialog.__init__(self, *a, **k)
          b1 = wx.Button(self, -1, 'apri dialogo', pos=((50, 50)))
          b1.Bind(wx.EVT_BUTTON, self.clic_b1)
          b2 = wx.Button(self, -1, 'print evtloop', pos=((50, 80)))
          b2.Bind(wx.EVT_BUTTON, self.clic_b2)
  
      def clic_b1(self, evt): TestDialog(self).ShowModal()
      def clic_b2(self, evt): print wx.GUIEventLoop.GetActive()
  
  app = wx.App(False)
  TestDialog(None).Show()
  app.MainLoop()

Ogni volta che cliccate sul primo pulsante, aprite un nuovo dialogo modale "annidato". Cliccando sul secondo pulsante, noterete che il loop attivo è di volta in volta diverso (confrontate gli indirizzi di memoria per vederlo).

Tenete conto che, al di là della chiamata esplicita a ``ShowModal``, wxPython potrebbe mostrarvi molti dialoghi modali "di routine" durante la normale vita di un'applicazione. Di conseguenza, lo stack dei loop è uno scenario frequente dietro le quinte. 

In pratica, quanto è importante sapere queste cose? Dipende dal vostro scenario: di solito, anche quando sovrascrivete ``wx.App.MainLoop`` e gestite gli eventi "a mano", il comportamento standard dei dialoghi modali è comunque quello che volete. Non vi importa se gli eventi prodotti dal dialogo tornano a essere gestiti in modo autonomo da wxPython per un po'. 

Se però lo ritenete opportuno, potete creare e distruggere anche i loop annidati "secondari". In questo caso, dovreste ricordarvi di ripristinare (riattivare) il loop precedente quando uscite da quello attuale. Per aiutarvi in questo compito, vi conviene usare ``wx.EventLoopActivator``: si tratta di una classe speciale che attiva un nuovo loop e mantiene un riferimento a quello vecchio. Quando distruggete l'istanza di ``wx.EventLoopActivator``, automaticamente verrà ripristinato il loop precedente. Un esempio chiarirà forse meglio::

  class TestDialog(wx.Dialog):
      def __init__(self, *a, **k):
          wx.Dialog.__init__(self, *a, **k)
          self.loop = wx.GUIEventLoop()
          self.active = wx.EventLoopActivator(self.loop)
          self.Bind(wx.EVT_CLOSE, self.on_close)
          print 'loop attivo nel dialogo:', wx.GUIEventLoop.GetActive()
  
      def on_close(self, evt):
          self.loop.Exit()
          del self.active
          self.Destroy()
  
  
  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = wx.Button(p, -1, 'apri dialogo', pos=((50, 50)))
          b.Bind(wx.EVT_BUTTON, self.onclic)
  
      def onclic(self, evt):
          print 'loop attivo:', wx.GUIEventLoop.GetActive()
          TestDialog(self).Show()
    

  app = wx.App(False)
  Test(None).Show()
  app.MainLoop()

Notate prima di tutto che abbiamo rinunciato a ``ShowModal`` per mostrare il dialogo (altrimenti wxPython avrebbe semplicemente aperto un altro loop dentro il nostro). Se volete disattivare il resto dell'interfaccia, dovete farlo a mano. L'uso di ``wx.EventLoopActivator`` è mostrato nel nostro ``TestDialog``: all'inizio apriamo un nuovo loop, e quando il dialogo viene chiuso, distruggiamo anche l'istanza dell'attivatore, ripristinando il loop precedente. Notate però che ``wx.EventLoopActivator``, al momento della sua distruzione, non chiama ``Exit`` sul loop, quindi dobbiamo pensarci noi stessi (simmetricamente, chiamare ``Exit`` sul loop non basta a "disattivarlo"! Occorre distruggere il ``wx.EventLoopActivator`` che lo ha attivato).

E' importante uscire dal loop con ``Exit``? Lo è abbastanza: come abbiamo già detto qui sopra, ``wx.App`` mette a disposizione due hook specifici: ``OnEventLoopEnter`` e ``OnEventLoopExit``. Il primo è chiamato da ``wx.GUIEventLoop.SetActive``, e il secondo da ``wx.GUIEventLoop.OnExit`` (che a sua volta dipende proprio da ``wx.GUIEventLoop.Exit``). Potete sovrascrivere questi metodi per eseguire codice ogni volta che entrate e uscite da un loop degli eventi. Per vedere come funzionano, potete sostituire l'``App`` generica dell'esempio precedente con questa::

  class MyApp(wx.App):
      def OnEventLoopEnter(self): 
          print 'entro nel loop', wx.GUIEventLoop.GetActive()
  
      def OnEventLoopExit(self):
          print 'esco dal loop', wx.GUIEventLoop.GetActive()
  
  
  app = MyApp(False)
  Test(None).Show()
  app.MainLoop()

Adesso notate che la "partita doppia" dei messaggi provenienti da ``MyApp`` e da ``TestDialog`` coincide. Ma se togliete la chiamata a ``self.loop.Exit()``, vedrete che ``MyApp.OnEventLoopExit`` non viene più eseguito quando chiudete il dialogo. Naturalmente, potrebbe essere quello che volete in certe occasioni: l'importante è capire che ri-attivare un loop non comporta automaticamente uscire dal loop precedente. 

Infine, un suggerimento: se intendete usare sul serio queste tecniche, probabilmente vi conviene mantenere uno stack (una semplice lista python) delle istanze di ``wx.EventLoopActivator`` man mano che le create, e poi distruggerle semplicemente pop-andole fuori dallo stack. 

.. index:: 
   single: loop degli eventi; personalizzati
   single: wx.GUIEventLoop; Run
   single: loop degli eventi; wx.GUIEventLoop.Run

Creare loop degli eventi personalizzati.
----------------------------------------

Negli ultimi esempi qui sopra, vi sarete accorti che, per giostrare tra diversi loop, abbiamo di nuovo rinunciato a occuparci di gestire personalmente gli eventi. Tutto ciò che abbiamo fatto è stato istanziare dei ``wx.GUIEventLoop`` e attivarli in successione, replicando peraltro quello che wxPython farebbe normalmente. 

Se vi serve questa tecnica di gestire diversi loop, ma (ovviamente) volete anche personalizzare il modo in cui questi loop gestiscono gli eventi, siete arrivati al punto in cui dovete sotto-classare ``wx.GUIEventLoop``. 

Il metodo che vi serve sovrascrivere è ``Run``, all'interno del quale wxPython fa girare il ciclo infinito che già conosciamo. Ecco un esempio minimale, che dovrebbe ormai esservi familiare: abbiamo solo spostato il cuore delle operazioni dentro una sottoclasse di ``wx.GUIEventLoop.Run``::

  import time

  class MyFrame(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = wx.Button(p, -1, 'clic')
          b.Bind(wx.EVT_BUTTON, self.onclic)
          self.Bind(wx.EVT_CLOSE, self.onclose)
  
      def onclic(self, evt):  
          print 'la gui risponde agli eventi!'
  
      def onclose(self, evt):
          wx.GetApp().stop_app()
  
  
  class MyEvtLoop(wx.GUIEventLoop):
      def __init__(self): 
          self.time_to_quit = False
          wx.GUIEventLoop.__init__(self)
  
      def Run(self):
          active = wx.EventLoopActivator(self)
          while not self.time_to_quit:
              while self.Pending():
                  self.Dispatch()
              self.ProcessIdle()
              time.sleep(0.1)
          self.Exit()
          del active
          
  
  class MyApp(wx.App):
      def OnInit(self):
          self.time_to_quit = False
          return True
  
      def MainLoop(self):
          self.loop = MyEvtLoop()
          self.loop.Run()
          wx.Exit()
  
      def stop_app(self):
          self.loop.time_to_quit = True
  
  
  app = MyApp(False)
  MyFrame(None).Show()
  app.MainLoop()

In questo esempio abbiamo predisposto le cose nel ``wx.App.MainLoop`` per avere un solo loop per tutta la vita dell'applicazione (chiamiamo ``wx.Exit()`` subito dopo che il loop ha smesso di funzionare). Ma naturalmente potete organizzare le cose in modo da attivare più loop il successione, a seconda delle vostre esigenze. 

Perché manipolare il loop degli eventi?
---------------------------------------

Abbiamo lavorato a lungo per comprendere il meccanismo dei loop degli eventi in wxPython, ma alla fine: quando è necessario utilizzare queste tecniche? 

Fortunatamente, quasi mai. Pochissime nozioni tra quelle contenute in questa pagina potrebbero trovar posto negli scenari comuni: in pratica, vale la pena di tenere sottomano solo ``wx.Yield``. 

Altre idee possono tornarvi utili solo se sviluppate cose molto esotiche: certe "applicazioni dentro applicazioni" (un editor visuale, per esempio) potrebbero aver bisogno di event loop gestiti separatamente per consentire all'applicazione "figlia" di funzionare senza intaccare la "madre". Questa è la tecnica, per esempio, che permette a una shell IPython di integrare al suo interno una gui wxPython. 

In teoria, come parte di un'architettura Model-Controller-View, si potrebbe voler "spacchettare" il loop degli eventi per farlo gestire da un Controller esterno a wxPython. Ma è un approccio inutilmente complicato, almeno in linea di principio: per fortuna wxPython offre degli agganci molto più comodi. :ref:`Postare eventi personalizzati<eventi_personalizzati>` nella coda, o perfino :ref:`usare un handler personalizzato<handler_personalizzati>` sono tecniche molto più pratiche e agevoli per stabilire una comunicazione tra la gui e il Model sottostante (senza contare, naturalmente, la possibilità di un sistema di messaggistica estraneo a wxPython, come Publish/Subscriber). 

.. todo:: una pagina su mcv, una su pub/sub

In generale, prima di smontare il loop degli eventi, conviene provare tutte le altre soluzioni: quelle descritte in questa pagina sono tecniche complicate e possono portare a errori difficili da scoprire, comportamenti non cross-compatibili, etc. 

Infine, un caso specifico e perfino abbastanza comune in cui potreste voler mettere le mani sotto il cofano, è quando dovete affiancare a wxPython un altro loop degli eventi. La logica di molte applicazioni si fonda su qualche tipo di ciclo infinito; anche molti grandi framework esistenti fanno uso di qualche tipo di event loop, da Twisted a Pygame, da Gevent a Tornado. Effettivamente, per integrare wxPython in queste architetture, in certi casi potrebbe essere necessario accedere direttamente al loop degli eventi. Ma non è l'unica strada, e anzi, talvolta non ce n'è proprio bisogno: dedichiamo :ref:`una pagina separata<integrazione_event_loop>` ad approfondire questi scenari. 
