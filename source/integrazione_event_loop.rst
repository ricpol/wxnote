.. _integrazione_event_loop:

.. index::
   single: eventi; loop degli eventi
   single: loop degli eventi; integrare loop esterni

Come integrare event loop esterni in wxPython.
==============================================

Affrontiamo in questa pagina un argomento trasversale ad altri che abbiamo coperto in queste note: di conseguenza qui ci limitiamo a fornire delle indicazioni specifiche ma sintetiche, e rimandiamo alle altre pagine per il quadro generale.

Il pre-requisito, naturalmente, è di conoscere :ref:`tutto<eventibasi>` :ref:`quello<eventi_avanzati>` :ref:`che<eventitecniche>` :ref:`abbiamo<eventitecniche2>` :ref:`scritto<eventloop>` sulla gestione degli eventi in wxPython. 

Il problema.
------------

wxPython, come tutti i gui framework, è organizzato intorno al suo "loop degli eventi", in pratica un ``while True`` infinito che resta attivo per tutto il ciclo di vita della vostra applicazione. Di conseguenza, in un'applicazione wxPython, ``wx.App.MainLoop`` è l'alfa e l'omega del vostro programma: per tutto il tempo restate bloccati lì dentro. Questo naturalmente rende disagevole far funzionare wxPython insieme ad altri componenti che hanno un proprio "main loop". 

Un esempio concreto.
^^^^^^^^^^^^^^^^^^^^

Immaginate di aver scritto il motore di un gioco "in tempo reale": al suo cuore, è un ciclo senza fine che controlla lo stato del mondo, decide le mosse di giocatori governati dell'AI, e tra le altre cose accetta gli input del giocatore umano... che che voi volete appunto gestire con un'interfaccia grafica wxPython. Questo scenario pone anche il problema interessante di come scambiare informazioni avanti e indietro tra wxPython e il motore del gioco. 

Ma, più alla base, il dilemma è come integrare un ciclo infinito del tipo::

  class Game(object):
      # etc. etc. 
      
      def run(self):
          while True:
              self.check_world_status()
              self.update_resources()
              for player in self.players:
                  player.move()
              # etc. etc.

in una applicazione wxPython che :ref:`viene pur sempre avviata<wxapp_basi>` con::

  app = wx.App()
  app.MainLoop() # e qui restiamo bloccati!

Dopo aver lanciato il suo main loop, wxPython "prende il comando", e non è possibile far partire anche il main loop del nostro gioco (non nello stesso thread, per lo meno). 

Una soluzione radicale: usare solo wxPython.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Una soluzione è re-implementare tutta la logica del gioco "dal punto di vista" di wxPython: l'utente invia gli input agendo sull'interfaccia; i callback gestiscono la risposta appropriata; e in sostanza il "main loop" di tutta l'applicazione diventa il ``wx.App.MainLoop`` gestito da wxPython. 

Bisogna rinunciare del tutto al main loop ``Game.run`` del nostro gioco, e chiamare i singoli passaggi da dentro wxPython. Le azioni da compiere in risposta all'input dell'utente verranno eseguite nei callback. Le azioni da eseguire a ciclo continuo potrebbero essere pianificate con dei timer, per esempio. 

Bisogna dire che questo approccio, in generale, viola il principio di separazione tra le parti tipico per esempio del pattern Model-Controller-View. E' però una questione discutibile. In un certo senso, nessun gui framework rispetta il pattern MCV in modo rigoroso: avete già rinunciato a MCV dalla riga ``import wx`` in testa al vostro codice. In wxPython, :ref:`come abbiamo visto<eventi_avanzati>` tutti i widget derivano sia da ``wx.Window`` sia da ``wx.Event``: e per questo recitano allo stesso tempo la parte della View e quella del Controller (ovvero, sono capaci di rispondere agli eventi). 

Usare un gui framework non significa rinunciare a un sano principio di separazione delle parti. Ma bisogna aver presente che wxPython (al pari di altri framework analoghi) non riguarda solo la parte "view", ma mette anche a disposizione gli strumenti per gestire (almeno in parte) il "controller" dell'applicazione. Bisogna giocare secondo le regole di wxPython, e adattare MCV di conseguenza. Nel nostro caso, come abbiamo detto, vorrebbe dire in pratica lasciare inalterate le varie routine di ``Game`` (``check_world_status`` etc.), e chiamarle dall'interno di wxPython.

.. todo:: una pagina su MCV.

Tuttavia, anche lasciando da parte le perplessità relative a MCV, questo approccio potrebbe essere sgradevole da usare quando il main loop "ospite" è complesso, o è comunque già stato scritto e non intendiamo rinunciarvi. 

E poi ci sono anche altri componenti già esistenti, "a eventi" o comunque dotati di qualche tipo di loop, che forniscono servizi di gestione e coordinamento tra logica di business e logica di presentazione, e che potremmo dover integrare in wxPython. Per esempio framework asincroni come Twisted, o librerie più leggere come Gevent, motori di rendering come PyGame, e molti altri ancora. Naturalmente non possiamo metterci a "smontare" il main loop di questi grandi framework: per integrarli, dobbiamo usare altre strategie. 

Un approccio sbagliato: un ciclo ``while True``.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Quello che non potete fare, naturalmente, è chiamare il vostro "main loop" ospite da qualche parte dentro l'applicazione wxPython. Per esempio, immaginate questo scenario: voi avviate normalmente la ``wx.App``, e presentate una finestra con un pulsante. Quando l'utente fa clic sul pulsante, parte il motore del gioco. Questo vorrebbe dire, nel callback collegato al pulsante, scrivere quacosa come::

  def on_clic(self, evt):
      game = Game()
      game.run()

In teoria, nessun problema. In pratica però, siccome ``run`` è un ciclo infinito, noi restiamo bloccati per sempre nel callback ``on_clic``: wxPython aspetterà per sempre l'uscita da quel callback, il loop degli eventi si fermerà, e l'interfaccia si bloccherà (in compenso però il motore di gioco, invisibile, continuerà a funzionare benissimo!)

L'approccio corretto: eseguire uno step alla volta.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le strategie per risolvere questo problema sono molte, ma quasi tutte si fondano su una premessa indispensabile: dovete essere in grado di spezzettare il vostro main loop ospite in operazioni di durata "abbastanza piccola" da poter essere intercalate alle operazioni della gui, senza causare rallentamenti.

Il modo più consueto consiste nell'eseguire, ogni volta, solo un singolo ciclo (uno "step") del vostro ``while True``. Ma se questo dovesse essere ancora troppo lungo, bisognerebbe frammentare lo step in operazioni più piccole. 

Per riprendere l'esempio del nostro motore di gioco, dovreste poter effettuare questa piccola modifica::

  class Game(object):
      # etc. etc. 
      
      def make_step(self):
          self.check_world_status()
          self.update_resources()
          for player in self.players:
              player.move()
          # etc. etc.
      
      # e quindi (ma ormai non ci servirà più...)
      def run(self):
          while True:
              self.make_step()

Nel mondo reale, forse, operazioni come ``check_world_status`` etc., saranno ancora troppo complesse e/o intercalate da azioni dell'utente: dovranno essere ulteriormente segmentate. 

Ma se avete la possibilità di frammentare in qualche modo il vostro loop in operazioni abbastanza brevi, allora siete pronti a implementare una delle soluzioni che seguono (altrimenti, forse potete ugualmente provare con la n. 5, che rovescia i termini del problema e vi propone di segmentare il loop di wxPython, invece).

.. index:: 
   single: wx.GUIEventLoop; Yield
   single: wx.App; Yield
   single: eventi; wx.GUIEventLoop.Yield
   single: eventi; wx.App.Yield

Soluzione 1: usare ``Yield``.
-----------------------------

Probabilmente il modo più semplice per venirne a capo è :ref:`usare<yield_etc>` ``wx.App.Yield`` e i suoi cugini. Per esempio, ricordate il ciclo ``while True`` che poco fa bloccava completamente wxPython? Ecco, basta modificarlo così::

  def on_clic(self, evt):
      game = Game()
      while True:
          wx.GetApp().Yield()
          game.make_step()

In linea di principio, basta questo a togliervi il pensiero. A ogni ciclo, ``Yield`` raccoglie gli eventi che si sono accumulati nella coda, e li processa prima di cedere di nuovo la parola al vostro main loop ospite.

Nella vita reale forse non vorrete ospitare il main loop secondario proprio all'interno di un callback. Ma potete inserirlo dove preferite, il principio non cambia: naturalmente dovete avviarlo quando il ``wx.App.MainLoop`` è partito, altrimenti non funzionerà.

Vantaggi: è davvero molto facile da usare. Per i casi semplici, potrebbe davvero "funzionare e basta". 

Svantaggi: ``Yield`` e compagni godono in generale di cattiva fama tra i programmatori wxWidgets/wxPyhton. ``Yield`` è fragile: può andar bene per sbloccare la gui in situazioni occasionali e temporanee, ma fargli tenere in piedi la responsività della vostra applicazione lungo tutto il suo ciclo di vita... molti vi diranno che probabilmente è un po' troppo. Intanto dovete cautelarvi contro la possibilità che l'utente faccia qualcosa di "illogico", :ref:`come già detto<yield_etc>`. Ma quando le applicazioni diventano più complesse, e soprattutto quando i messaggi tra la gui e il "ciclo ospite" si fanno più intrecciati ed è cruciali risolverli nell'ordine corretto... le cose potrebbero diventare difficili da gestire e da debuggare. In essenza ``Yield`` scombina l'ordine naturale degli eventi nella coda. I problemi di "rientri" (ossia, un evento chiamato una seconda volta prima che il loop abbia avuto la possibilità di gestire la prima chiamata) sono sempre in agguato. 

.. index:: 
   single: wx.EVT_IDLE
   single: wx.IdleEvent; RequestMore
   single: eventi; wx.EVT_IDLE
   single: eventi; wx.IdleEvent.RequestMore

Soluzione 2: catturare ``wx.EVT_IDLE``.
---------------------------------------

``wx.EVT_IDLE`` è un evento che wxPython emette per segnalare che "non ha niente da fare" in quel momento (ovvero, che la coda degli eventi da gestire è temporaneamente vuota). :ref:`Abbiamo già detto<processare_manualmente_eventi>` che il sistema ne approfitta per compiere operazioni di routine dietro le quinte. 

Ma possiamo approfittarne anche noi. Basta intercettare l'evento, e far compiere al nostro loop ospite uno "step". Potete catturare il ``wx.EVT_IDLE`` dove volete, naturalmente: anche nella ``wx.App``::

  class MyApp(wx.App):
      def OnInit(self):
          self.Bind(wx.EVT_IDLE, self.on_idle)
          self.game = Game()

      def on_idle(self, evt):
          self.game.make_step()
          evt.RequestMore()

La chiamata finale a ``wx.IdleEvent.RequestMore`` è una finezza necessaria. Lo scenario che vogliamo evitare è questo: la gui non ha niente da fare, e quindi emette un ``wx.EVT_IDLE``; noi lo intercettiamo, ed eseguiamo uno "step" del loop ospite. Finito lo step, può succedere che l'utente continui a non fare assolutamente nulla; ma ormai wxPyhton ha già emesso il suo ``wx.EVT_IDLE``, e dal suo punto di vista non è ancora cambiato niente... quindi tutto si blocca senza emettere più segnali, fino a quando l'utente riprende in mano il mouse! Per evitare questo intoppo, ``RequestMore`` segnala semplicemente la necessità di emettere un nuovo ``wx.EVT_IDLE``. Se nel frattempo l'utente è rimasto inattivo, l'evento sarà di nuovo intercettato da noi. Se invece l'utente ha prodotto qualche segnale, allora prenderà la precedenza, e verrà processato. 

Vantaggi: questo sistema è davvero molto performante (rispetto a un timer, per esempio). E' probabilmente il sistema migliore da tentare come prima cosa, se non ci sono ragioni particolari in contrario. 

Svantaggi: non c'è garanzia che ``wx.EVT_IDLE`` venga emesso con regolarità. Se le attività della gui tengono il sistema molto occupato, è possibile che la frequenza del ciclo ospite rallenti troppo per le vostre necessità. Per esempio, non dovreste usare questo sistema e al contempo intercettare altri eventi molto frequenti (``wx.EVT_UPDATE_UI``...) e impegnarli con callback "pesanti". Se intercettate ``wx.EVT_IDLE`` anche per altri scopi, dovete stare attenti a chiamare ``Skip()`` altrimenti il callback della ``wx.App`` non verrà mai attivato. Ma anche in casi apparentemente normali, l'emissione di ``wx.EVT_IDLE`` potrebbe interrompersi per un po': per esempio, se l'utente apre un menu o un dialogo modale, la gui resta attiva finché non viene richiuso. 

Soluzione 3: usare un timer.
----------------------------

.. todo:: una pagina sui timer.

Usare un timer è un'opzione tutto sommato facile da implementare. Basta avviarlo e catturare il relativo evento periodico::

  def __init__(....)
      # .....
      self.timer = wx.Timer(self)
      self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
      self.timer.Start(10)  # millisecondi
  
  def on_timer(self, evt):
      # wx.GetApp().Yield()
      self.game.make_step()
      self.timer.Start(10)

Notate che forse dovremmo comunque chiamare ``Yield``, se la gui reagisce troppo lentamente: ma conviene prima testare il programma senza ``Yield``, ed eventualmente inserirlo dopo. 

Vantaggi: la frequenza dei timer è regolabile, e questo (insieme a un sano uso di ``Yield``) permette di bilanciare esattamente le esigenze di entrambi i loop. Inoltre i timer sono più affidabili dei ``wx.EVT_IDLE``: non c'è il rischio che si interrompano quando l'utente apre un menu, per esempio. 

Svantaggi: i timer sono sempre più lenti dei ``wx.EVT_IDLE``. Se entrambi i vostri loop tengono molto impegnata la cpu, potrebbe darvi noia il sovraccarico ulteriore dovuto al timer. In questo caso, forse vi convengono i ``wx.EVT_IDLE``.

Soluzione 4: gestire manualmente gli eventi.
--------------------------------------------

E' la soluzione più complessa, ma anche la più flessibile. :ref:`Abbiamo parlato a lungo<eventloop>` dei loop degli eventi di wxPython e delle tecniche per manipolarlo. Molte cose si possono personalizzare se intervenite a quel livello. Ma la tecnica standard che si può applicare al nostro esempio è questa::

  class MyApp(wx.App):
      def OnInit(self):
          self.time_to_quit = False
          self.game = Game()

      def MainLoop(self):
          loop = wx.GUIEventLoop()
          active = wx.EventLoopActivator(loop)
          while not self.time_to_quit:
              self.game.make_step()
              while loop.Pending():
                  loop.Dispatch()
              # wx.MilliSleep(10)
              loop.ProcessIdle()
          wx.Exit()

Essenzialmente, si tratta di processare alternativamente la coda di eventi di wxPython e uno step del loop ospite, in uno stesso ciclo. E' possibile regolare il ritmo con cui vengono emessi ``wx.EVT_IDLE`` chiamando ``wx.MilliSleep`` (anche per evitare un utilizzo eccessivo della cpu, in molti casi). 

Una cosa importante da notare è che abbiamo il controllo completo dell'ordine in cui verranno gestiti tutti i segnali provenienti da entrambi i loop. 

Questo richiede un piccolo approfondimento. E' normale infatti che i due loop interagiscano tra loro scambiandosi "messaggi": potrebbero essere oggetti di un sistema Publish/Subscriber, oppure banalmente degli eventi wxPython (:ref:`sappiamo già<eventi_personalizzati>` come emettere eventi personalizzati: ora possiamo usarli come sistema di messaggistica tra i due loop, se vogliamo). Ebbene, con questa tecnica, ogni segnale emesso dal loop ospite in direzione di wxPython, verrà raccolto e processato immediatamente dopo, nello stesso ciclo. Allo stesso modo, se la parte wxPython vuole inviare un segnale al loop ospite, questo sarà processato nel ciclo immediatamente successivo, e non oltre. 

.. todo:: una pagina su MVC | una pagina su pub/sub.

Soluzione 5: rovesciare il rapporto tra loop principale e ospite.
-----------------------------------------------------------------

Invece di gestire il loop ospite dall'interno di wxPython, possiamo fare il contrario::

  class Game(object):
      def __init__(self):
          # ....
          self.bootstrap_wxPython()

      def make_step(self):
          self.check_world_status()
          self.update_resources()
          for player in self.players:
              player.move()
          # etc. etc.
          
      def bootstrap_wxPython(self):
          self.wxApp = MyApp(False)
          self.wxLoop = wx.GUIEventLoop()
          active = wx.EventLoopActivator(self.wxLoop)

      def stop_wxPython(self):
          wx.Exit()

      def make_wxStep(self, loop):
          while loop.Pending():
              loop.Dispatch()
          # wx.MilliSleep(10)
          loop.ProcessIdle()

      def run(self):
          while True:
              self.make_step()
              self.make_wxStep(self.wxLoop)

  game = Game()
  game.run()

Se guardate questo esempio dopo molto tempo passato nella logica di wxPython, la sensazione sarà più o meno come guidare in Inghilterra. E' opportuna qualche spiegazione in più. 

Prima di tutto, in una logica Model-Controller-View la nostra classe ``Game`` adesso fa un po' la parte del Model e un po' quella del Controller. Forse vi converrà dividere le funzioni in due classi separate (ma non necessariamente! MCV non è una religione, dopo tutto). In ``bootstrap_wxPython`` creiamo la ``wx.App`` e anche il loop degli eventi. Qui stiamo sottintendendo che in ``MyApp.OnInit`` ci sia il codice necessario per mostrare la finestra principale (altrimenti, poco male: basta crearla e mostrarla direttamente in ``bootstrap_wxPython``). Quindi, alla fine di ``bootstap_wxPython``, l'utente vede l'interfaccia sullo schermo, ma niente è ancora attivo. 

Fin qui siamo arrivati alla riga ``game = Game()``. Immediatamente dopo, però, viene eseguito ``game.run()`` e tutto si mette in moto. Il metodo ``run`` esegue alternativamente, in un ciclo infinito, uno step del nostro motore di gioco, e uno step dell'interfaccia wxPython. 

Più precisamente, uno step di wxPython (``make_wxStep``) corrisponde alla consueta sequenza di gestione degli eventi a cui siamo abituati (emissione di ``wx.EVT_IDLE`` compresa). 

Naturalmente a un certo punto bisognerà uscire dal programma. Potete scegliere la strategia che preferite: per esempio, ci sarà un flag che provoca il ``break`` dal ciclo infinito di ``run``. Una volta smesso di processare gli eventi wxPython, tuttavia, l'interfaccia resterà sempre visibile ma inattiva. Ancora una volta dovrà essere la classe ``Game`` a intervenire, chiamando al momento opportuno ``stop_wxPython``. 

.. index::
   single: wx.CallAfter

Soluzione 6: usare un thread separato.
--------------------------------------

Le soluzioni viste fin qui sono asincrone: alternano i due loop nell'ambito di un solo thread di esecuzione. Ma naturalmente potete anche provare a far vivere tutto il loop ospite in un thread separato. 

Ai thread in wxPython dedicheremo una pagina apposita, e avremo modo di discutere pro e contro. Nell'attesa, eccovi la versione breve. I thread sono sempre un argomento controverso: in generale tutti li sconsigliano, e con molte buone ragioni. Nella pratica però spesso sono una soluzione comoda e a portata di mano... almeno finché non *scappano* di mano. In python i thread sono particolarmente facili da usare, e in wxPython sono addirittura banali, finché vi tenete sul sicuro e seguite una raccomandazione fondamentale. 

Questa raccomandazione è di non eseguire mai chiamate che pprovengono da da un thread secondario e che modificano lo stato dell'interfaccia. In wxPython è obbligatorio che tutto ciò che riguarda la gui sia eseguito nel thread principale (quello in cui vive la ``wx.App``). 

Per "modificare lo stato dell'interfaccia" basta veramente poco: non potete, per esempio, impostare il valore di una casella di testo da un thread secondario. Questo in pratica vi lascia con ben poche opzioni: per fortuna però, in nove casi su dieci, l'opzione giusta è anche la più facile da capire e usare. 

Basta far passare tutte le comunicazioni dal thread secondario al thread principale attraverso ``wx.CallAfter``. Questa funzione globale è semplicemente un wrapper thread-safe intorno alle chiamate di funzione wxPython. Detto in poche parole, se da un thread secondario chiamate qualcosa come::

  main_frame.some_textctrl.SetValue('hello')

la vostra applicazione rischia di disintegrarsi. Ma se invece chiamate::

  wx.CallAfter(main_frame.some_textctrl.SetValue, 'hello')

tutto funzionerà come per incanto. Davvero: in nove casi su dieci vi basta sapere questo per fare multithreading in wxPython. Se però inciampate senza saperlo nel decimo caso, allora siete nei guai.

Anche se in teoria è facile mettere il loop ospite in un processo separato, di rado questa è una buona idea. In genere, a ben vedere usare i thread diventa solo una versione più complicata di qualche soluzione che abbiamo già visto. Per esempio, molto spesso il loop ospite deve aggiornare la gui a intervalli regolari. Potete metterlo in un thread secondario, e poi mandare messaggi al thread principale usando ``wx.CallAfter`` con regolarità (o postando eventi nella coda con ``wx.PostEvent``, l'altra tecnica standard in queste situazioni). Ma tutto questo si può fare lo stesso, mantenendo i due loop nello stesso thread, e usando invece un timer. Inoltre, raramente framework complessi, che hanno molte ramificate interazioni con il resto del vostro sistema operativo, funzionano bene in un thread secondario. 

Fatte queste precisazioni, il nostro "motore di gioco" potrebbe in effetti essere avviato in un thread separato::

  import threading 
  import time
  import wx
  
  class Game(object):
      def __init__(self): self.players=('A', 'B', 'C')
      def check_world_status(self): return 'controllo lo stato'
      def update_resources(self): return 'aggiorno le risorse'
      def move(self, player): return 'muovo il giocatore '+player
      
  class ControllerThread(threading.Thread):
      def __init__(self, gui_frame):
          threading.Thread.__init__(self)
          self.time_to_quit = False
          self.gui_frame = gui_frame
          self.game = Game()
  
      def run(self):
          while True:
              if self.time_to_quit: break
              wx.CallAfter(self.gui_frame.update_gui, 
                           self.game.check_world_status())
              time.sleep(2)
              if self.time_to_quit: break
              wx.CallAfter(self.gui_frame.update_gui, 
                           self.game.update_resources())
              time.sleep(2)
              for player in self.game.players:
                  if self.time_to_quit: break
                  wx.CallAfter(self.gui_frame.update_gui, 
                               self.game.move(player))
                  time.sleep(1)
  
  
  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = wx.Button(p, -1, 'clic', pos=((50, 50)))
          b.Bind(wx.EVT_BUTTON, self.on_clic)
          self.text = wx.TextCtrl(p, pos=((50, 80)), size=((200, -1)))
          self.Bind(wx.EVT_CLOSE, self.on_close)

          self.game_thread = ControllerThread(self)
          self.game_thread.start()
  
      def on_clic(self, evt): 
          self.text.SetValue('rispondo agli eventi!')
  
      def on_close(self, evt):
          self.game_thread.time_to_quit = True
          dlg = wx.ProgressDialog("Chiusura", "Un attimo prego...",
                                  maximum = 50, parent=self,
                                  style = wx.PD_APP_MODAL)
          for i in xrange(50):
              time.sleep(.1)
              dlg.Update(i)
          dlg.Destroy()
          evt.Skip()
  
      def update_gui(self, msg):
          self.text.SetValue(msg)
  
  app = wx.App(False)
  Test(None).Show()
  app.MainLoop()

E' un tentativo molto rozzo, perché abbiamo cercato di modificare il meno possibile l'esempio originario, ma può bastare a rendere l'idea. Abbiamo spostato il main loop del gioco dentro una classe "controller" per comodità. Abbiamo usato ``time.sleep`` dentro il main loop per simulare una certa complessità, e soprattutto per lasciarvi il tempo di vedere i successivi aggiornamenti della casella di testo. 

Questo genera un problema imprevisto al momento di chiudere la finestra: il motore di gioco potrebbe trovarsi in un punto in cui non ha ancora eseguito il controllo sul flag ``self.time_to_quit``, e quindi cerca di scrivere in una casella di testo che ormai è stata distrutta. Eventi come questo in wxPython sollevano un ``PyDeadObjectError``, che dobbiamo evitare. Per questo motivo abbiamo introdotto il check ``if self.time_to_quit: break`` ogni volta che potevamo, ma restano sempre dei "buchi" di almeno 2 secondi. Abbiamo infine risolto ritardando la chiusura del frame principale, mentre mostriamo un ``wx.ProgressDialog``. 

E' una soluzione provvisoria a un problema che nel mondo reale, almeno in questi termini, non si presenterà: il vostro main loop non resterà mai bloccato così a lungo. Tuttavia è un problema interessante, ed è un esempio dei grattacapi che potreste dover affrontare: ``CallAfter`` programma un aggiornamento futuro della gui, che però nel frattempo potrebbe assumere uno stato incompatibile con la situazione com'era al momento della chiamata a ``CallAfter``.

In conclusione, è possibile in molti casi gestire un main loop secondario "alla pari" in un thread separato, anche se difficilmente vale la pena. D'altro canto, i thread possono essere utili per altri compiti di routine, per esempio eseguire operazioni di lunga durata in background senza bloccare la gui. Ma discuteremo meglio di questi aspetti quando parleremo di thread.

.. todo:: una pagina sui thread: accorciare tutto questo paragrafo di conseguenza.

Integrare altri framework in wxPython.
--------------------------------------

Le tecniche viste fino a questo punto possono anche aiutarvi a usare wxPython insieme ad altri framework dotati di un proprio main loop. 

A dire il vero, alcuni framework mettono a disposizione delle apposite api per l'integrazione con wxPython. In altri casi, ci sono comunque delle ricette già collaudate. Prima di mettersi a sperimentare soluzioni fatte in casa, conviene sempre documentarsi. Vediamo di seguito qualche caso interessante. 

.. index::
   single: IPython

wxPython e IPython.
^^^^^^^^^^^^^^^^^^^

IPython mette a disposizione degli hook per integrare nella sua shell gui fatte con wxPython o altri framework. La `documentazione relativa <https://ipython.org/ipython-doc/3/interactive/reference.html#gui-event-loop-support>`_ è molto chiara. In pratica, se in una shell IPython scrivete::

  %gui wx

IPython avvia per voi una ``wx.App`` di cui gestisce il main loop, lasciandovi la libertà di disegnare interattivamente la gui. 

Queste capacità sono esposte anche sotto forma di api, cosa che vi permette di scrivere gui wxPython integrate in IPython. Come ricorda anche la documentazione, in questo caso dovete però fare attenzione a non avviare voi stessi il ``wx.App.MainLoop``, perché questo è un compito da lasciare allo hook di IPython. Potete comunque sottoclassare e istanziare ``wx.App``, e quindi utilizzare i vari ``OnInit``, ``OnExit`` etc. come di consueto. 

Vale in ogni caso la pena di dare un'occhiata ai `tre <https://github.com/ipython/ipython/blob/master/IPython/lib/guisupport.py>`_ `moduli <https://github.com/ipython/ipython/blob/master/IPython/lib/inputhook.py>`_ che `implementano <https://github.com/ipython/ipython/blob/master/IPython/lib/inputhookwx.py>`_ questa funzionalità: al netto delle necessarie astrazioni per supportare diversi gui framework da collegare e disconnettere a runtime, troverete alcuni spunti interessanti che riprendono le tecniche viste finora. 

.. index::
   single: Pygame

wxPython e Pygame.
^^^^^^^^^^^^^^^^^^

L'integrazione con Pygame è più problematica. Non esiste un'api "ufficiale", e le ricette che si trovano in rete sono vecchie e tutte piuttosto sperimentali. Far girare Pygame in un thread separato sembra non essere l'idea giusta: Pygame ha bisogno di vivere nel main thread, proprio come wxPython. La soluzione corretta sembra essere una qualche variante del pattern di sfruttare ``wx.EVT_IDLE`` o ``wx.EVT_TIMER`` per aggiornare il canvas di Pygame.

`Questa pagina <http://wiki.wxpython.org/IntegratingPyGame>`_ del wiki di wxPython sono raccolti alcuni suggerimenti. Ma la strada più promettente sembra essere quella indicata `nel sito di Pygame <http://pygame.org/project-Pygame+embedded+in+wxPython-1580-2788.html>`_. 

.. index::
   single: Twisted

wxPython e Twisted.
^^^^^^^^^^^^^^^^^^^

Twisted mette a disposizione un reactor specializzato per l'integrazione con wxPython. Potete trovare i dettagli `nella documentazione <http://twistedmatrix.com/documents/current/core/howto/choosing-reactor.html#core-howto-choosing-reactor-wxpython>`_, e in `questo esempio <http://twistedmatrix.com/trac/browser/trunk/docs/core/examples/wxdemo.py>`_. 

Purtroppo sia la documentazione sia l'esempio sono un po' vecchi, e usano convenzioni wxPython ormai deprecate. Non è difficile, comunque, tradurre l'esempio in un wxPython "moderno". Eccolo ri-adattato::

  from twisted.internet import wxreactor
  # importante! prima installare wxreactor...
  wxreactor.install()
  # ... poi importare internet.reactor
  from twisted.internet import reactor
  
  class MyFrame(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          menu = wx.Menu()
          menu_item = menu.Append(-1, 'Exit')
          menuBar = wx.MenuBar()
          menuBar.Append(menu, 'File')
          self.SetMenuBar(menuBar)
          self.Bind(wx.EVT_MENU, self.DoExit, menu_item)

          p = wx.Panel(self)
          b = wx.Button(p, -1, 'reactor!', pos=(20, 20))
          b.Bind(wx.EVT_BUTTON, self.on_clic)

          self.Bind(wx.EVT_CLOSE, self.DoExit)

      def DoExit(self, evt):
          # importante: fermiamo il reactor prima di chiudere
          reactor.stop()

      def on_clic(self, evt):
          # programmiamo una chiamata con il reactor di Twisted
          reactor.callLater(2, self.twoSecondsPassed)
  
      def twoSecondsPassed(self):
          print "two seconds passed"
  
  app = wx.App(False)
  # registriamo l'istanza della wx.App con Twisted...
  reactor.registerWxApp(app)
  MyFrame(None).Show()
  # ... e lasciamo che Twisted pensi ad avviare il mainloop della wx.App
  reactor.run()

