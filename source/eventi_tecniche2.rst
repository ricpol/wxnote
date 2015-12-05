.. _eventitecniche2:

.. index::
   single: eventi
   
Gli eventi: altre tecniche (seconda parte).
===========================================

Dopo aver dedicato :ref:`due <eventibasi>` :ref:`pagine <eventi_avanzati>` agli eventi, e :ref:`una pagina <eventitecniche>` ad alcune tecniche più inconsuete, siamo ancora ben lontani dall'aver esaurito l'argomento! 

In questa sezione affrontiamo alcuni aspetti ancora più esotici, che molto probabilmente non avrete mai bisogno di utilizzare. Ma possono sempre servire a vantarsi con gli amici, naturalmente. 

Ancora una volta, non si tratta di tecniche difficili da comprendere... ma neppure particolarmente facili: leggete ciò che segue solo dopo aver letto e capito tutto quello che abbiamo visto finora sugli eventi. Una raccomandazione: siete incoraggiati a sperimentare per conto vostro a partire da quello che vedrete qui. Tuttavia, giocando con questi strumenti, è facile ottenere interfacce che si bloccano, non rispondono, vanno in crash. Siate preparati a uccidere il processo di python responsabile del vostro programma. E verificate periodicamente se non sono rimasti processi di python ancora in vita. Se qualcosa può andar storto, lo farà. 

.. index::
   single: eventi; filtri
   single: eventi; wx.App.SetCallFilterEvent
   single: eventi; wx.App.FilterEvent
   single: wx.App; SetCallFilterEvent
   single: wx.App; FilterEvent

Filtri.
-------

La possibilità di applicare filtri globali è probabilmente l'aspetto meno documentato e usato di tutto il meccanismo degli eventi di wxPython. 

Diciamo subito che l'intera macchina dei filtri si può far partire e arrestare a comando, chiamando ``wx.App.SetCallFilterEvent(True)`` e ``wx.App.SetCallFilterEvent(False)``. 

Quando il meccanismo dei filtri è attivo, ogni volta che un :ref:`event handler<cosa_e_handler>` deve :ref:`processare un evento<eventi_processamento>`, per prima cosa chiamerà il metodo ``wx.App.FilterEvent``. Nella sua implementazione di default, ``FilterEvent`` non fa nulla e restituisce subito ``-1``. Voi però avete la possibilità di sovrascrivere questo metodo, e fargli eseguire del codice. Inoltre, se ``FilterEvent`` restituisce qualcosa di diverso da ``-1``, l'evento non verrà più processato oltre. 

Più precisamente: ``FilterEvent`` deve restituire uno tra:

- ``-1``, per dire "prosegui a processare l'evento" (stessa cosa che chiamare ``Skip``);
- ``0`` per dire "non processare l'evento"; 
- ``+1`` per dire "considera l'evento già processato, non andare oltre".

Fate molta attenzione, se restituite qualcosa di diverso da ``-1``: ``FilterEvent`` interviene su qualsiasi evento, compresi quelli che disegnano l'interfaccia: se non fate bene i vostri conti, vi ritroverete con il programma bloccato e incapace di rispondere agli eventi. 

La chiamata a ``FilterEvent`` avviene immediatamente all'inizio della propagazione, prima di qualsiasi altra cosa (siamo all'inzio di quella che abbiamo chiamato ":ref:`fase 0<eventi_processamento>`" nella catena della propagazione, se ricordate). E questa chiamata avviene per qualsiasi evento emesso dal vostro programma. Ecco un esempio minimo per rendere l'idea::

  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = wx.Button(p, -1, 'clic', pos=((50,50)))
          b.Bind(wx.EVT_BUTTON, self.on_clic)

      def on_clic(self, evt): print '\n\nCLIC\n\n'


  class myApp(wx.App):
      def OnInit(self):
          self.SetCallFilterEvent(True)
          return True
          
      def FilterEvent(self, evt):
          print 'filter!', evt.__class__.__name__
          return -1


  app = myApp(False)
  Test(None).Show()
  app.MainLoop()

Prima di far girare questo codice, prendetevi un momento per indovinare come funzionerà. Abbiamo sottoclassato ``wx.App`` per chiamare ``SetCallFilterEvent(True)`` nel suo ``OnInit``: in questo modo ci assicuriamo che il filtro degli eventi sia sempre attivo fin dall'inizio. Quindi, abbiamo implementato il suo metodo ``FilterEvent``. Restituiamo comunque ``-1`` in modo che tutti gli eventi verranno processati come al solito, ma prima facciamo qualcosa di speciale (per adesso ci limitiamo a scrivere nello standard output). 

L'effetto del nostro programma è piuttosto vistoso: ``FilterEvent`` interviene proprio su tutti gli eventi, compreso il ``wx.EVT_UPDATE_UI`` che viene emesso al semplice passaggio del mouse, senza contare il ridimensionamento e lo spostamento delle finestre, e anche gli occasionali ``wx.EVT_IDLE``. 

Perfino la documentazione di wxWidgets (il framework c++ sottostante) ci consiglia di usare ``FilterEvent`` con giudizio, per evitare rallentamenti. In python, dove ogni chiamata di funzione è particolarmente dispendiosa, è davvero difficile consigliare l'uso di questa tecnica. 
E' per questo che wxPython introduce ``SetCallFilterEvent`` (che non esiste nelle wx). Di default, il meccanismo dei filtri è disabilitato, e siamo noi a doverlo attivare se proprio ci serve. Come minimo, sarebbe meglio attivarlo solo al momento di utilizzarlo, e disattivarlo di nuovo appena possibile. 

.. note:: In wxWidgets, le cose sono ancora più complicate. ``FilterEvent`` è un metodo originariamente messo a disposizione da una apposita classe mix-in, che si chiama ``EventFilter``. In questo modo, costruendo un widget personalizzato che deriva anche da ``EventFilter`` è possibile dotarlo di un suo metodo ``FilterEvent`` da sovrascrivere, ed è quindi possibile attivare più filtri contemporaneamente. La ``wx.App`` dispone di un suo ``FilterEvent`` di default, perché deriva già "per natura" da ``EventFilter``. In wxPython tutto questo non è supportato: resta solo il ``FilterEvent`` della ``wx.App``.

E quindi? A che cosa potrebbe servirci questo filtro globale? In alcune circostanze è utile a monitorare l'attività dell'utente in modo trasversale a tutta l'applicazione (detta così sa un po' di spionaggio, vero?). Per esempio, considerate questa ``wx.App``::

  class myApp(wx.App):
      def OnInit(self):
          self.SetCallFilterEvent(True)
          self.last_used = datetime.datetime.now()
          return True

      def FilterEvent(self, evt):
          if evt.GetEventType() in (wx.EVT_LEFT_UP.typeId, wx.EVT_KEY_UP.typeId):
              self.last_used = datetime.datetime.now()
          return -1

Come vedete, tiene traccia dell'ultima volta che l'utente ha usato il mouse o la tastiera, ed è quindi possibile calcolare da quanto tempo è inattivo. 

Naturalmente sarebbe possibile ottenere lo stesso effetto collegando con ``Bind`` ogni singolo elemento dell'interfaccia a un callback dedicato a fare questo lavoro (o anche, come vedremo tra poco, usando un handler personalizzato). Ma chiaramente in questo modo si fa prima. 

A partire da questa idea, non è difficile scrivere, per esempio, una ``wx.App`` che traccia in un apposito log tutti i tasti premuti dall'utente... e così via. 

.. index::
   single: eventi; blocchi
   single: wx.EventBlocker
   single: eventi; wx.EventBlocker

Blocchi.
--------

Quando abbiamo detto che i filtri sono l'aspetto meno conosciuto e usato del meccanismo degli eventi, volevamo dire: a eccezione dei blocchi. 

Un ``wx.EventBlocker`` è in grado di bloccare temporaneamente qualsiasi evento (o anche solo alcuni eventi selezionati) diretto a uno specifico widget. 

Potete passare al costruttore ``-1`` (ovvero ``wx.EVT_ANY``) per dire "blocca tutti gli eventi", oppure il ``typeId`` di un evento specifico. Se vi serve aggiungere altri eventi da bloccare, potete farlo in seguito chiamando il suo metodo ``Block``. 

Il blocco resta attivo fin quando l'istanza di ``wx.EventBlocker`` non viene fisicamente distrutta (in qualunque modo possiate marcare un oggetto per essere reclamato dal garbage collector in python: uscendo dallo "scope" in cui è stata definita la variabile, o in definitiva anche con ``del``). A quel punto, gli eventi tornano a essere gestiti come di consueto. 

Ecco un esempio pratico::

  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = wx.ToggleButton(p, -1, 'blocca/sblocca', pos=((50,50)))
          b.Bind(wx.EVT_TOGGLEBUTTON, self.onclic)

          self.blockbutton = wx.Button(p, -1, 'posso bloccarmi!', pos=((50, 80)))
          self.blockbutton.Bind(wx.EVT_BUTTON, self.on_blockbutton_clic)

      def on_blockbutton_clic(self, evt):
          print 'evidentemente adesso sto funzionando...'

      def onclic(self, evt): 
          if evt.IsChecked():
              self.block = wx.EventBlocker(self.blockbutton, -1)
          else: 
              del self.block


  app = wx.App(False)
  Test(None).Show()
  app.MainLoop()

Il primo pulsante in alto attiva e disattiva un blocco che agisce sul secondo pulsante. Il blocco è totale: come vedete, il pulsante smette di rispondere a tutti gli eventi (anche il mouseover, per esempio). Se modificate il blocco scrivendo::

  self.block = wx.EventBlocker(self.blockbutton, wx.EVT_BUTTON.typeId)

vedrete che il pulsante blocca solo il ``wx.EVT_BUTTON``, ma risponde ancora agli altri eventi. 

Ancora una volta possiamo domandarci: a che cosa serve questo meccanismo? Ovviamente, se vogliamo solo disabilitare un widget, ``Enable()`` è tutto quel che serve. Un blocco, tuttavia, può essere all'occorrenza più selettivo, fermando esattamente gli eventi che ci servono. Oppure: se vogliamo disattivare l'esecuzione di un segmento di codice a seconda delle circostanze, potremmo mettere un po' di logica in più nel callback. Tuttavia un blocco può aiutarci a mantenere il codice più pulito. 

.. _categorie_eventi:

.. index:: 
   single: eventi; categorie
   single: eventi; wx.Event.GetEventCategory
   single: eventi; wx.wxEVT_CATEGORY_*
   single: wx.Event; GetEventCategory
   single: wx.wxEVT_CATEGORY_*

Categorie.
----------

Nella nostra rassegna dei concetti più oscuri e meno documentati sugli eventi, non potevano mancare le categorie. Detto in breve, ogni evento appartiene a una categoria, a scelta tra: 

- ``wx.wxEVT_CATEGORY_UI``: questa categoria raggruppa gli eventi generati da aggiornamenti della gui (ridimensionamenti, spostamenti, etc.);
- ``wx.wxEVT_CATEGORY_USER_INPUT``: questi sono gli eventi tipicamente generati dell'utente (pressione di tasti, clic del mouse...);
- ``wx.wxEVT_CATEGORY_NATIVE_EVENTS``: definita come l'unione delle due precedenti (``wx.wxEVT_CATEGORY_UI|wx.wxEVT_CATEGORY_USER_INPUT``);
- ``wx.wxEVT_CATEGORY_TIMER``: qui stanno i ``wx.TimerEvent``;
- ``wx.wxEVT_CATEGORY_THREAD``: i ``wx.ThreadEvent`` (gli eventi usati per comunicare tra i thread);
- ``wx.wxEVT_CATEGORY_SOCKET``: a questa categoria appartengono solo i "socket event", che wxPyhton non supporta;
- ``wx.wxEVT_CATEGORY_CLIPBOARD``: gli eventi della clipboard (copia e incolla, drag and drop);
- ``wx.wxEVT_CATEGORY_ALL``: questa categoria raggruppa tutte le altre;
- ``wx.wxEVT_CATEGORY_UNKNOWN``: aggiunta recentemente come fallback. 

.. todo:: una pagina sui thread , una pagina sui timer , una pagina sulla clipboard

Potete sapere a quale categoria appartiene un evento con ``wx.Event.GetEventCategory``. Per esempio, in un callback::

  def mycallback(self, evt):
      print evt.GetEventCategory()

Se state creando un :ref:`evento personalizzato<eventi_personalizzati>` e avete bisogno di impostare la sua categoria, potete sovrascrivere ``GetEventCategory`` per restituire quello che vi sembra più opportuno. 

Il valore di queste costanti, come avrete probabilmente indovinato, è calibrato per poterle combinare in una :ref:`bitmask<cosa_e_bitmask>`, per cui per esempio ``wx.wxEVT_CATEGORY_ALL^wx.wxEVT_CATEGORY_USER_INPUT`` vuol dire "tutto tranne i comandi dell'utente". 

Le categorie degli eventi sono usate praticamente solo per filtrare che cosa processare in una chiamata a ``YieldFor``, e pertanto riprenderemo il discorso :ref:`quando parleremo di questi argomenti<yield_etc>`. Siccome ``YieldFor`` è usato da wxWidget in alcune occasioni, anche queste categorie hanno una funzione interna. Inoltre, naturalmente, potreste usarle per implementare qualche filtro di vostro molto specializzato... se vi viene in mente un'idea. 

.. index::
   single: eventi; handler personalizzati
   single: eventi; wx.PyEvtHandler
   single: eventi; wx.Window.PushEventHandler
   single: wx.PyEvtHandler
   single: wx.Window; PushEventHandler

.. _handler_personalizzati:

Handler personalizzati.
-----------------------

:ref:`Sappiamo già<cosa_e_handler>` che ``wx.EvtHandler`` è la classe-base dedicata alla gestione degli eventi. E sappiamo anche che tutta la gerarchia dei widget (a partire dalla classe madre ``wx.Window``) deriva da ``wx.EvtHandler``, e di conseguenza tutti i widget hanno in sé la capacità di gestire gli eventi. 

Questa architettura di default basta nella vita di tutti i giorni. Ma volendo, possiamo andare oltre... 

Parlando della propagazione degli eventi, :ref:`abbiamo fatto cenno<handler_addizionali>` alla possbilità che un widget abbia addirittura uno stack di handler pronti intervenire uno dopo l'altro per gestire l'evento.

.. todo:: una pagina sui pycontrols (cfr paragrafo seguente)

In effetti, abbiamo la possibilità di creare handler personalizzati (derivando da ``wx.PyEvtHandler``, la classe che wxPython mette a disposizione per sovrascrivere i metodi virtuali), e aggiungerli allo stack degli handler di un determinato widget. In questa sezione vedremo come fare, ma prima un avvertimento: si tratta di strumenti che wxPython mette a disposizione "traducendoli" dal framework c++ sottostante, ma che nel mondo python hanno meno utilità pratica. Leggete i paragrafi seguenti senza badare troppo all'utilità pratica: vedremo che tutto questo vi potrebbe tornare utile, in certi scenari. 

Per cominciare, non c'è nulla di magico in un handler personalizzato: è una semplice sotto-classe di ``wx.PyEvtHandler``. Per esempio::

  class MyEvtHandler(wx.PyEvtHandler):
      def __init__(self):
          wx.PyEvtHandler.__init__(self)
          self.Bind(wx.EVT_BUTTON, self.on_clic)

      def on_clic(self, evt):
          print "sono un clic gestito nell'handler personalizzato"
          evt.Skip()

Questo è un handler che gestisce un ``wx.EVT_BUTTON`` nel modo che ormai vi è familiare (questo è un buon momento per ricordarsi che, dopo tutto, ``Bind`` :ref:`è un metodo di<che_cosa_e_bind>` ``wx.EvtHandler``). Per usarlo, non dobbiamo fare altro che istanziarlo, e assegnarlo a un widget. In teoria potremmo assegnarlo a un widget qualsiasi, ma siccome il suo scopo è gestire un ``wx.EVT_BUTTON``, ha senso assegnarlo a un pulsante (o a un panel che contiene dei pulsanti, magari). Per esempio::

  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = wx.Button(p, -1, 'clic', pos=((50, 50)))

          handler = MyEvtHandler()
          b.PushEventHandler(handler)

  app = wx.App(False)
  Test(None).Show()
  app.MainLoop()

Tutto qui. ``PushEventHandler`` "spinge" il nostro handler personalizzato in cima allo stack degli handler del pulsante. Il pulsante acquisisce il nostro handler, e quindi acquisisce la sua caratteristica risposta all'evento ``wx.EVT_BUTTON``. 

Se adesso fate girare questo codice, vi accorgerete che avete ottenuto un comportamento del tutto analogo alla normale gestione di un evento da parte di un pulsante. La differenza è che adesso il callback ``on_clic`` è definito nella classe dell'handler, e non nella classe del frame come di consueto. 

.. note:: questo è il motivo principale per cui esiste questo meccanismo nel framework c++. Il punto è che in wxWidgets non si possono definire callback all'esterno della classe in cui risiedono i widget: quindi scrivere un handler separato e agganciarlo a un widget è l'unico modo per intervenire "dal di fuori". In python, ovviamente, questa feature non ci impressiona più di tanto: le funzioni e i metodi sono "first class object", e si possono passare a ``Bind`` come parametri normali. In wxPython un callback può essere un metodo di un'altra classe, o una funzione esterna stand-alone, senza alcuna difficoltà. 

Naturalmente è possibile anche collegare un "normale" callback al pulsante::

  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = wx.Button(p, -1, 'clic', pos=((50, 50)))
          b.PushEventHandler(MyEvtHandler())
          b.Bind(wx.EVT_BUTTON, self.onclic)

      def onclic(self, evt): print 'un clic "normale"'

Potete aggiungere diversi handler allo stack in successione, e in questo modo potete ottenere una riposta più "componibile", "modulare" all'evento. 

.. note:: questa è una possibilità effettivamente nuova, nel senso che invece non è possibile collegare con ``Bind`` diversi callback per lo stesso evento ad un widget. Naturalmente però nessuno vieta di chiamare una serie di funzioni esterne in successione dallo stesso callback, ottenendo lo stesso effetto di modularità. 

Lo stack degli handler è appunto uno stack: l'ultimo handler inserito è il primo che si occuperà dell'evento. Notate che l'handler predefinito (ovvero il widget stesso) in questo modo resta sempre in fondo allo stack, ed è quindi l'ultimo a occuparsi dell'evento (prima cioè che l'evento si propaghi oltre il widget). 

Questa caratteristica ci permette di determinare con precisione l'ordine in cui i callback devono intervenire. Può essere importante, in alcuni scenari: esploriamo meglio uno di questi scenari :ref:`in una ricetta separata<ricette_checkpass_button>`.

.. index::
   single: eventi; handler
   single: eventi; wx.Window.PopEventHandler
   single: eventi; wx.EvtHandler.SetNextHandler
   single: eventi; wx.EvtHandler.SetPreviousHandler
   single: eventi; wx.EvtHandler.GetNextHandler
   single: eventi; wx.EvtHandler.GetPreviousHandler
   single: eventi; wx.EvtHandler.Unlink
   single: eventi; wx.EvtHandler.IsUnlinked
   single: eventi; wx.EvtHandler.Unbind
   single: eventi; wx.EvtHandler.SetEvtHandlerEnabled
   single: wx.Window; PopEventHandler
   single: wx.EvtHandler; SetNextHandler
   single: wx.EvtHandler; SetPreviousHandler
   single: wx.EvtHandler; GetNextHandler
   single: wx.EvtHandler; GetPreviousHandler
   single: wx.EvtHandler; Unlink
   single: wx.EvtHandler; IsUnlinked
   single: wx.EvtHandler; Unbind
   single: wx.EvtHandler; SetEvtHandlerEnabled

Altre operazioni con gli handler.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

L'operazione opposta a ``PushEventHandler`` è ``PopEventHandler``, che toglie l'ultimo handler inserito nello stack (e lo restituisce come risultato). Non potete togliere anche l'handler predefinito (cioè il widget stesso). Se cercate di farlo, wxPython solleva una ``wx._core.PyAssertionError``. Quindi tenete conto degli handler man mano che li aggiungete, oppure preparatevi a intercettare questa eccezione::

  while True: # svuoto completamente lo stack
      try: mywidget.PopEventHandler()
      except wx._core.PyAssertionError: break

``PopEventHandler`` restituisce un riferimento all'handler rimosso: se lo conservate in una variabile potete riutilizzarlo in seguito, se volete. 

Potete anche manipolare lo stack usando ``SetNextHandler`` e ``SetPreviousHandler``. Ricordatevi però che wxPython mantiene una lista doppia di riferimenti alla catena degli handler: di conseguenza, se impostate B come successivo di A, dovete anche impostare A come precedente di B::

  handler_A.SetNextHandler(handler_B)
  handler_B.SetPreviousHandler(handler_A)

Impostare a ``None`` sia il precedente sia il successore di un handler, equivale a rimuoverlo dalla catena: dovete però fare attenzione a "ripararla". Per evitare complicazioni, se volete rimuovere un handler intermedio della catena, usate piuttosto ``handler.Unlink()``: questo ripara anche automaticamente la catena. 

Potete conoscere il successore di un handler chiamando ``handler.GetNextHandler()`` (che restituisce ``None`` se l'handler è l'ultimo della catena). Analogamente, ``handler.GetPreviousHandler`` vi restituisce l'handler precedente. Se entrambi questi metodi restituiscono ``None``, vuol dire che l'handler è "sganciato" dalla catena: potete anche sapere se un handler è attualmente "sganciato" chiamando, più rapidamente, ``handler.IsUnlinked()``. 

Inoltre, ricordatevi la possibilità di scollegare un evento da un handler con ``handler.Unbind()`` (che funziona proprio come ``Bind`` ma al contrario), e la possibilità di disconnettere completamente un handler chiamando ``handler.SetEvtHandlerEnabled()``. 

Infine, :ref:`abbiamo già fatto cenno<lanciare_evento_personalizzato>` a ``handler.ProcessEvent()`` (e alla quasi equivalente funzione globale ``wx.PostEvent()``) che torna utile per far processare immediatamente a un handler un certo evento (tipicamente un evento personalizzato creato sul momento, ma si può naturalmente usare anche con gli eventi "ordinari"). Questo metodo, insieme con ``AddPendingEvent`` e ``QueueEvent``, torna utile anche nel caso specifico in cui gli eventi personalizzati sono creati, lanciati e processati come mezzo di comunicazione tra diversi thread.

.. todo:: una pagina sui thread.

A che cosa servono gli handler personalizzati?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

E quindi, a che cosa servono questi oggetti? Come abbiamo già spiegato, sono importanti nel mondo c++, ma hanno una utilità pratica ridotta in wxPython. Potete senz'altro usarli per aumentare la scomposizione e la fattorizzazione del codice, se volete usare strumenti wxPython (invece delle normali tecniche python). Occasionalmente potreste voler aggiungere degli handler "plug-in" a runtime (ma di solito potete ottenere lo stesso effetto chiamando ``Bind`` e ``Unbind`` a runtime, o mantenendo un callback fisso e da quello applicando qualche tipo di "strategy pattern" per selezionare le funzioni da chiamare a seconda dei casi). 

Uno scenario in cui invece potrebbero tornarvi utili, è quando avete bisogno di controllare l'ordine esatto in cui vengono eseguiti i callback. Quando avete molteplici callback, l'ordine di esecuzione può dipendere da come intercettate l'evento (potete collegarlo al widget, oppure a un suo parent). Se questa incertezza non va bene per quello che dovete fare, allora una buona soluzione è far gestire l'evento da un handler personalizzato, e poi inserire l'handler nello stack del widget (e ripetere all'occorrenza con altri callback in altri handler). In questo modo avete sempre il controllo dello stack degli handler, e sapete con esattezza in che ordine verranno eseguiti i callback. 

Per illustrare un esempio concreto di questo scenario, abbiamo scritto :ref:`una ricetta<ricette_checkpass_button>` in cui vogliamo che un pulsante, quando viene premuto, per prima cosa chieda la password all'utente prima di procedere a elaborare ogni azione successiva. 

.. _esempio_finale_propagazione_aggiornato:

Un esempio finale per la propagazione degli eventi (aggiornato).
----------------------------------------------------------------

Riprendiamo infine l'esempio riassuntivo che :ref:`avevamo fatto<esempio_finale_propagazione>` al termine del discorso sulla propagazione degli eventi, aggiornandolo con le tecniche viste in questa pagina. Di nuovo, fate girare il codice e osservate in che ordine sono eseguiti i callback::

  class MyEvtHandler(wx.PyEvtHandler):
      def __init__(self, name):
          wx.PyEvtHandler.__init__(self)
          self.name = name
          self.Bind(wx.EVT_BUTTON, self.onclic)

      def onclic(self, evt):
          print "clic dall'handler", self.name
          evt.Skip()


  class MyButton(wx.Button):
      def __init__(self, *a, **k):
          wx.Button.__init__(self, *a, **k)
          self.Bind(wx.EVT_BUTTON, self.onclic)

      def onclic(self, evt): 
          print 'clic dalla classe Mybutton'
          evt.Skip()


  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          panel = wx.Panel(self)
          button = MyButton(panel, -1, 'clic', pos=((50,50)))

          button.PushEventHandler(MyEvtHandler('Alice'))
          button.PushEventHandler(MyEvtHandler('Bob'))

          button.Bind(wx.EVT_BUTTON, self.onclic_button)
          panel.Bind(wx.EVT_BUTTON, self.onclic_panel, button)
          self.Bind(wx.EVT_BUTTON, self.onclic_frame, button)
          
      def onclic_button(self, evt): 
          print 'clic dal button'
          evt.Skip()

      def onclic_panel(self, evt):
          print 'clic dal panel'
          evt.Skip()

      def onclic_frame(self, evt):
          print 'clic dal frame'
          evt.Skip()


  class MyApp(wx.App):
      def OnInit(self):
          self.Bind(wx.EVT_BUTTON, self.onclic)
          self.SetCallFilterEvent(True)
          return True

      def FilterEvent(self, evt):
          evt.Skip()
          if evt.GetEventType() == wx.EVT_BUTTON.typeId:
              print 'clic dal filtro'
          return -1

      def onclic(self, evt):
          print 'clic dalla wx.App'
          evt.Skip()


  app = MyApp(False)
  Test(None).Show()
  app.MainLoop()

Abbiamo finito di parlare degli eventi in wxPython? Naturalmente no! Come abbiamo accennato sopra, parliamo di eventi anche nella pagina dedicata ai thread. Ma soprattutto, ci restano ancora molte cose da scoprire sugli event loop... Ma sarà l'argomento di una :ref:`pagina separata<eventloop>`!
