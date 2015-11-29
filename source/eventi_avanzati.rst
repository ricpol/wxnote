.. highlight:: python
   :linenothreshold: 5
   
.. _eventi_avanzati:

.. index::
   single: eventi
   
Gli eventi: concetti avanzati.
==============================

In questa pagina affrontiamo alcuni aspetti degli eventi che non entrano quasi mai in gioco in un normale programma wxPython. Tuttavia è opportuno conoscerli, e in certi casi conviene utilizzarli. 

La lettura di questa pagina è consigliata solo se avete seguito :ref:`la prima parte del discorso <eventibasi>`, che presenta la terminologia e i concetti di base che qui daremo per scontati. 

Per cominciare, riprendiamo alcune cose già viste. Un evento può essere collegato a un handler e a un callback, usando il metodo ``Bind`` di un binder (in pratica si usa il ``Bind`` dell'handler, ma questo invoca subito il ``Bind`` del binder per fare il lavoro). Lo stile che si usa in genere è questo::

    button = wx.Button(...)
    button.Bind(wx.EVT_BUTTON, callback)
    
Questo stile trae vantaggio dal fatto che tutti gli elementi visibili in wxPython (i vari widget) derivano anche da ``wx.EvtHandler``, e quindi hanno la capacità di fare da handler per i loro stessi eventi. 

Abbiamo anche visto che si può scegliere anche un altro handler, e scrivere per esempio::

    button = wx.Button(self, ...)   # dove self e' un dialogo, per esempio
    self.Bind(wx.EVT_BUTTON, callback, button)
    
E abbiamo detto che quasi sempre i due stili sono equivalenti... ma "quasi sempre" non è "sempre", appunto. 

Per capire di più, dobbiamo parlare della propagazione degli eventi. 

.. index::
   single: eventi; propagazione
   single: eventi; command event
   single: wx; CommandEvent()
   
La propagazione degli eventi.
-----------------------------

Abbiamo detto che tutti gli eventi derivano da ``wx.Event``, ma questa in realtà è una classe-base che fa poco. Una distinzione più importante avviene al livello della sottoclasse ``wx.CommandEvent``: questi eventi (e tutti quelli delle classi derivate) si chiamano in gergo "command event", e *si propagano*. Tutti gli altri non si propagano. 

Che cosa vuol dire "propagarsi"? Vuol dire che il segnale costituito dall'oggetto-evento, una volta creato, raggiunge in primo luogo il widget stesso che lo ha originato. Se l'evento è di quelli che non si propagano, allora il segnale si ferma lì, e nessun altro elemento della gui verrà mai a conoscenza che l'evento si è generato. In questo caso, in pratica, soltanto l'handler del widget stesso che ha prodotto l'evento ha la possibilità di intercettarlo: in altre parole, l'unico modo per intercettare questi eventi è usare lo stile ``widget.Bind(wx.EVT_*, callback)`` (ricordiamo ancora che ogni widget è anche un handler). 

Se invece l'evento si propaga, il segnale procede a visitare l'immediato "parent" del widget. Poi arriva al parent del parent, e continua ad arrampicarsi per tutta :ref:`la catena dei parent <catenaparent>`, fino a quando non raggiunge la finestra top-level. Di qui, salta direttamente alla ``wx.App``. 

A ogni fermata di questa esplorazione, l'algoritmo di gestione dell'evento cerca se c'è un handler in grado di gestirlo, ovvero se quell'handler è stato preventivamente collegato, grazie a un binder, a quel tipo di evento e a un callback. Se sì, il callback viene eseguito e l'algoritmo si ferma. Se no, prosegue nel suo viaggio. Come ultima possibilità, quando arriva alla ``wx.App``, chiede anche al suo handler (sì, anche la ``wx.App`` deriva da ``wx.EvtHandler``, e quindi è possibile collegarla agli eventi). Se voi non avete previsto nessun collegamento neppure lì, allora la ``wx.App`` ha un gestore di default, che semplicemente non fa nulla. E questo, finalmente, fa morire l'evento. 

Dopo aver capito a grandi linee il meccanismo di propagazione, vediamo come funziona nel dettaglio. 

.. index::
   single: eventi; processamento
   single: eventi; Skip()
   single: wx.EvtHandler; ProcessEvent()
   single: wx.EvtHandler; SetEvtHandlerEnabled()
   single: wx.Event; Skip()

.. _eventi_processamento:

Come un evento viene processato. 
--------------------------------

.. topic:: Fase 0

    **nasce l'evento.**

L'evento si genera da un widget. Dunque l'handler del widget stesso se ne occupa, passando l'evento al suo algoritmo interno ``wx.EvtHandler.ProcessEvent()``. E si va alla fase 1.


.. topic:: FASE 1

    **l'handler è abilitato?**

Qui la decisione che wxPython deve prendere è se questo handler è abilitato a processare eventi, oppure no. 

In genere la risposta è sì. Tuttavia, è possibile chiamare manualmente ``SetEvtHandlerEnabled(False)`` su un handler (su un widget, cioè) per impedirgli di processare eventi. Per ripristinare il comportamento normale, basta chiamare ``widget.SetEvtHandlerEnabled(True)``.

Se la risposta è no, si passa direttamente alla fase 5. Se la risposta è sì, passare alla fase successiva.


.. topic:: FASE 2

    **l'handler può gestire l'evento?**

Ovvero: avete collegato questo handler, per questo evento, a un callback, grazie a un binder? 

Se la risposta è sì, l'algoritmo ``ProcessEvent`` esegue il vostro callback (bingo!). Quindi passa alla fase 3. 

Se la risposta è no, ovviamente non c'è nessun callback da eseguire, e si procede con la fase 3.


.. topic:: FASE 3

    **l'evento dovrebbe propagarsi?**

Se l'evento non è un "command event", non ha la potenzialità di propagarsi. 

Se invece l'evento è un "command event", ha la potenzialità di propagarsi, ma non è detto che lo farà. 

Prima di tutto, ci sono due dettagli che bisogna considerare:

* gli eventi non si propagano oltre i dialoghi. :ref:`Abbiamo già accennato a questa cosa <wxdialog>`, parlando dell'extra-style ``wx.WS_BLOCK_EVENTS`` che nei dialoghi è settato per default. Questo significa che un evento può passare da un frame al parent (eventuale) del frame, ma non dal dialogo al parent del dialogo. Naturalmente è possibile settare ``wx.WS_BLOCK_EVENTS`` anche su un frame, se si desidera. 

* anche se un evento è "command", potrebbe non propagarsi all'infinito. Infatti gli eventi hanno un "livello di propagazione" interno. L'unico modo per conoscerlo è chiamare ``event.StopPropagation()``, che interrompe la propagazione e restituisce il livello di propagazione. Non dimenticatevi di chimare ``event.ResumePropagation()`` subito dopo. Se per esempio il livello è 1, l'evento non si propagherà oltre il diretto genitore. Se il livello è 2, andrà fino al parent del parent, ma poi si fermerà. In pratica però i normali "command event" hanno il livello di propagazione settato a ``sys.maxint``, e quindi si propagano effettivamente all'infinito. Ma potreste voler scrivere un classe-evento personalizzata che si propaga in modo più limitato, se necessario.

Tenendo anche conto di queste cose, se l'evento non è ancora stato processato in precedenza, si propaga senz'altro. 

Se invece l'evento è già stato processato, e quindi un callback è stato appena eseguito, di regola ``ProcessEvent`` termina e restituisce ``True``, *a meno che* il callback non abbia chiamato ``Skip()`` sull'evento. Chiamare ``event.Skip()`` è un segnale che si richiede di continuare il processamento degli eventi. Su ``Skip()`` parleremo in modo più approfondito in seguito. 

Potete sapere se l'algoritmo ha deciso che l'evento può propagarsi chiamando ``event.ShouldPropagate``. 

Dopo che wxPython determina se l'evento dovrebbe propagarsi, con questa informazione si passa alla fase 4. Più precisamente, se l'evento è un "command event", fase 4A. Altrimenti, fase 4B.


.. topic:: FASE 4A 

    **passare all'handler successivo** (versione "command event").

A questo punto l'algoritmo cerca l'handler successivo a cui bisogna rivolgersi. La ricerca avviene secondo le precedenze che elenchiamo qui sotto. In breve, ogni volta che viene trovato un handler, si torna alla fase 1, e si esegue il ciclo 1-2-3. Se la fase 3 determina che occorre una ulteriore propagazione, si torna a questa fase 4A, e si riprende la ricerca dal punto in cui era arrivata.

Ecco le regole per la ricerca degli handler: 

.. _handler_addizionali: 

* **4A.1**: handler addizionali

Qui in genere non succede mai nulla. Comunque, un widget potrebbe avere uno stack di numerosi handler. Ovviamente è una tecnica piuttosto avanzata, ma potreste :ref:`scrivere un handler personalizzato<handler_personalizzati>` (una sottoclasse di ``wx.EvtHandler``) e aggiungerlo allo stack chiamando ``widget.PushEventHandler(my_handler)``. 

L'handler di cui abbiamo parlato finora nelle fasi 1 e 2, è in realtà il primo handler dello stack (e anche il solo, se non ne avete aggiunti altri). Ma, se ci sono altri handler in coda, per ciascuno di essi si passa attraverso le fasi 1, 2, e 3. Come sopra, se la fase 3, a un certo passaggio, determina che l'evento non può propagarsi ulteriormente, l'algoritmo si ferma. Altrimenti, tutti gli handler addizionali vengono interrogati in seguenza. Quando sono esauriti, si procede con la fase 4A.2.

* **4A.2**: handler nelle sovraclassi

Prima si cerca nelle varie sovra-classi. Per ciascuna di esse, si interroga l'handler che si trova, passando per la fase 1 (è abilitato?), la fase 2 (può gestire l'evento?) e la fase 3 (potrebbe ancora propagarsi?). Se, a un certo passaggio, la fase 3 determina che l'evento non si può propagare ulteriormente (tipicamente perché un callback è stato trovato ed eseguito nella fase 2, ma non ha chiamato ``Skip``) allora l'algoritmo si ferma, ``ProcessEvent`` termina e restituisce ``True``. Se invece a ogni passaggio la fase 3 determina che l'evento può ancora propagarsi, si passa alla sovra-classe successiva fino a esaurirle. Quindi si procede alla fase 4A.3 qui sotto. 

* **4A.3**: handler del parent

Soltanto se, nell'ultima fase 3 attraversata, abbiamo stabilito che l'evento può ancora propagarsi, finalmente si passa al parent del widget attuale. Si chiede prima al suo handler, e poi si continua a cercare nelle sovra-classi e tra gli handler addizionali, percorrendo sempre le fasi 1-2-3 finché la fase 3 non determina che l'evento non può ulteriormente propagarsi. 

Quando alla fine l'handler trovato

* è un dialogo, oppure un frame con ``wx.WS_BLOCK_EVENTS`` settato, oppure
* è una finestra top-level, 

si esegue il ciclo 1-2-3 un'ultima volta (compresa la fase 4 per la ricerca nelle sovra-classi, naturalmente), e poi, se alla fase 3 si decide che l'evento dovrebbe ancora propagarsi, allora si passa alla fase 5.


.. topic:: FASE 4B

    **passare all'handler successivo** (versione "non command").

Questa versione della fase 4 è analoga a quella dei "command event". Soltanto, l'evento non può propagarsi al suo parent. Tuttavia, la ricerca nelle sovra-classi e negli handler addizionali avviene ancora. Quindi, ecco quello che succede: 

* **4B.1**: handler nelle sovra-classi. 

Per ciascuna sovra-classe si interroga l'handler e si passa per il ciclo 1-2-3. 
Se, a un certo passaggio, nella fase 3 troviamo che un callback è stato appena eseguito nella fase 2, ma non ha chiamato ``Skip``, allora l'algoritmo si ferma. Se invece il callback ha chiamato ``Skip``, si passa alla sovra-classe successiva fino a esaurirle. Quindi si procede alla fase 4B.2.

* **4B.2**: handler addizionali

Se ci sono handler addizionali, per ciascuno di essi si passa per il ciclo 1-2-3. Come sopra, se la fase 3, a un certo passaggio, trova che l'evento è stato processato ma il callback non ha chiamato ``Skip``, l'algoritmo si ferma. Altrimenti, tutti gli handler addizionali vengono interrogati in seguenza. 

E poi non si procede oltre, perché l'evento non può comunque propagarsi al parent del widget. 

Se l'evento non è stato ancora gestito, oppure se è stato gestito ma il callback ha chiamato ``Skip``, si procede ancora con la fase 5. 

.. _wxapp_ultimo_handler:

.. topic:: FASE 5

    **la ``wx.App`` come ultimo handler.**

Se si arriva fino a questo punto e l'algoritmo non è ancora terminato (perché l'evento non è ancora stato processato, oppure perché finora tutti i callback incontrati hanno sempre chiamato ``Skip``), allora l'algoritmo chiede all'handler della ``wx.App`` se è in grado di occuparsene. 

In effetti è possibile collegare con un binder un evento a un callback anche nella ``wx.App``, proprio come fareste di solito. 

Se perdete anche questa ultima occasione, il ``ProcessEvent`` dell'handler della ``wx.App`` ha comunque un comportamento predefinito, che semplicemente non fa nulla. In questo modo, l'algoritmo termina comunque e l'evento muore. 


Riassunto dei passaggi importanti.
----------------------------------

Come vedete, il ciclo completo è piuttosto complicato, ma nel 99% dei casi si riduce a pochi semplici passaggi:

* se non è un "command event", allora:

    * o viene processato dall'handler del widget stesso che lo ha generato, 
    * oppure da qualche sua sovra-classe,     
    * oppure dall'handler della ``wx.App``. 
    
* se invece l'evento è un "command event", allora:

    * o viene processato dal widget che lo ha generato, 
    * oppure da qualche sua sovra-classe,
    * oppure si cerca un collegamento in tutti i parent successivi, 
    * fino ad arrivare a un dialogo o a una finestra top-level, 
    * e quindi si conclude cercando un collegamento nell'handler della ``wx.App``. 
    * Se in una di queste stazioni si trova un callback, la propagazione si ferma, a meno che il callback non chiami ``Skip()`` sull'evento. 

.. index::
   single: wx.Event; Skip()
   single: eventi; Skip()

Come funziona ``Skip()``.
-------------------------

``event.Skip()`` può essere chiamato sull'evento, dall'interno di un callback che lo gestisce. Non importa se viene chiamato all'inizio o alla fine del codice del vostro callback: imposta comunque un flag interno all'evento, che segnala all'algoritmo di gestione che dovrebbe continuare il processamento degli eventi in coda. Questo significa: 

* continuare a propagare l'evento corrente (se può farlo), come se non fosse stato trovato nessun callback. 

* processare gli eventi successivi che sono in coda. 

Entrambe queste cose sono importanti, e per quanto riguarda la seconda, bisogna ricordare che spesso una singola azione dell'utente scatena più eventi in successione. 

Per esempio, quando fate clic su un pulsante, producete un ``wx.EVT_LEFT_DOWN``, un ``wx.EVT_LEFT_UP`` e un ``wx.EVT_BUTTON`` in sequenza. Se voi intercettate il primo, e nel callback non chiamate ``Skip()``, gli altri due non verranno mai processati. 

Voi direte: questo è grave solo se voglio intercettare anche un evento successivo; altrimenti, poco male. Ma non è del tutto esatto, perché bloccando il processamento degli eventi potreste comunque impedire a wxPython di invocare il comportamento di default di un widget. Per esempio, quando fate clic sul pulsante, wxPython deve comunque preoccuparsi di cambiare per un istante il suo aspetto per farlo sembrare "abbassato", e poi "rialzarlo". 

Il comportamento di default, quando occorre, *si aggiunge* a quello che voi eventualmente prescrivete nei vostri callback. Più precisamente, arriva *dopo* il vostro, perché è scritto nella sovra-classe madre da cui avete derivato il vostro widget. A questo proposito, c'è un dettaglio (diabolico!) incluso nel nostro schema, che occorre comprendere bene: l'algoritmo di processamento cerca gli handler nelle sovra-classi (fase 4.1) *dopo* aver determinato se l'evento deve propagarsi (fase 3). Quindi, se intercettate un evento e non chiamate ``Skip()`` nel relativo callback, potreste impedire la ricerca di eventuali meccanismi di gestione di default che si trovano nella classe-madre del vostro widget. 

Torniamo all'esempio del clic sul pulsante, che genera ``wx.EVT_LEFT_DOWN``, ``wx.EVT_LEFT_UP`` e ``wx.EVT_BUTTON`` in sequenza. Se voi intercettate il primo e non chiamate ``Skip()``, non solo impedite l'esecuzione di ulteriori callback che potreste aver scritto in corrispondenza del secondo e del terzo; ma inoltre impedirete a wxPython di gestire correttamente lo stato del pulsante. 

Per fortuna, i comportamenti di default di un pulsante sono codificati in risposta a ``wx.EVT_LEFT_DOWN`` e ``wx.EVT_LEFT_UP``, ossia gli eventi che in genere non vi interessano. L'evento che intercettate di solito è ``wx.EVT_BUTTON``, che parte solo *dopo* che tutta la gestione di default del pulsante è stata già completata (in particolare, ``wx.EVT_BUTTON`` è lanciato da ``wx.EVT_LEFT_UP`` alla fine del suo procedimento interno). Quindi potete tranquillamente dimenticarvi di chiamare ``Skip()`` nel callback di un ``wx.EVT_BUTTON``, e il vostro pulsante funzionerà come vi aspettate. 

In genere, tutti i widget fanno partire in coda gli eventi "di più alto livello", che sono quelli che in genere volete intercettare. Così potete risparmiarvi di chiamare ``Skip()`` nel callback, perché wxPython ormai ha già fatto la sua parte. 

Una lezione che si può trarre da tutto questo è: non dovete intercettare ``wx.EVT_LEFT_UP`` su un pulsante, se potete fare la stessa cosa intercettando ``wx.EVT_BUTTON``. 

Una seconda lezione è questa: se siete in dubbio, chiamate ``Skip()``. 


Un esempio per ``Skip()``.
--------------------------

Ecco qualche riga di codice che illustra l'esempio del "clic su un pulsante"::

    class SuperButton(wx.Button):
        def __init__(self, *a, **k): 
            wx.Button.__init__(self, *a, **k)
            self.Bind(wx.EVT_BUTTON, self.on_clic)
            
        def on_clic(self, event):
            print 'clic su SuperButton'
            event.Skip()
        
    class MyButton(SuperButton):
        def __init__(self, *a, **k):
            SuperButton.__init__(self, *a, **k)
            
    class TestEventFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            p = wx.Panel(self)
            button = MyButton(p, -1, 'clic!', pos=(50, 50)) 
            button.Bind(wx.EVT_LEFT_DOWN, self.on_down) 
            button.Bind(wx.EVT_LEFT_UP, self.on_up) 
            button.Bind(wx.EVT_BUTTON, self.on_clic) 
            button.SetDefault()

        def on_down(self, event): 
            print 'mouse giu'
            event.Skip()
            
        def on_up(self, event):
            print 'mouse su'
            event.Skip()
        
        def on_clic(self, event): 
            print 'clic'
            event.Skip()
            
    app = wx.App(False)
    TestEventFrame(None).Show()
    app.MainLoop()

Come si vede, abbiamo creato una gerarchia di sotto-classi di ``wx.Button`` per testare anche la ricerca degli handler nelle sovra-classi. 

Stiamo intercettando contemporaneamente ``wx.EVT_LEFT_DOWN``, ``wx.EVT_LEFT_UP`` e ``wx.EVT_BUTTON``. Nella configurazione di base, tutti i callback chiamano ``Skip()``. Se provate a eseguire adesso lo script, trovate che l'ordine in cui i callback sono chiamati rispecchia la normale ricerca degli handler: prima ``on_down``, poi ``on_up``, poi ``on_clic`` e infine ``SuperButton.on_clic``. 

Avvertenza: abbiamo un piccolo problema terminologico. Da questo momento, quando dico "pulsante" intendo "pulsante sinistro del mouse". Quando dico "bottone" mi riferisco invece al ``wx.Button`` disegnato sullo schermo. 

Osserviamo più da vicino, con l'avvertenza che quanto segue potrebbe differire tra le varie piattaforme. Se abbassate il pulsante del mouse, ma poi allontanate il puntatore dall'area del bottone prima di rilasciarlo, allora verranno catturati il ``wx.EVT_LEFT_DOWN`` e anche il ``wx.EVT_LEFT_UP``, *tuttavia* il ``wx.EVT_BUTTON`` non verrà emesso. wxPython sa che il secondo evento "appartiene" ugualmente al bottone, anche se il puntatore si è spostato nel frattempo: lo sa perché ha avuto modo di completare correttamente il processo interno del primo evento, e adesso si aspetta che il prossimo ``wx.EVT_LEFT_UP`` sia da attribuire al bottone. Tuttavia, quando il ``wx.EVT_LEFT_UP`` effettivamente si verifica, wxPython non innesca anche il ``wx.EVT_BUTTON``, se il puntatore non è rimasto nell'area del bottone. 

Specularmente, se abbassate il pulsante del mouse fuori dall'area del bottone, e poi lo rilasciate dopo averlo spostato all'interno dell'area, vedrete comparire soltanto un ``wx.EVT_LEFT_UP`` "orfano" (e ovviamente nessun ``wx.EVT_BUTTON``).

Adesso, per prima cosa provate a eliminare lo ``Skip`` di ``on_clic`` (riga 34). Il risultato è che ``SuperButton.on_clic`` non verrà più eseguito. D'altra parte però il pulsante funzionerà correttamente, perché non c'è nessuna particolare routine di default che ``wx.Button`` deve svolgere in risposta a un ``wx.EVT_BUTTON``. 

Invece, provate a togliere lo ``Skip`` di ``on_down`` (riga 26): il vostro callback verrà ovviamente ancora eseguito, ma ciò che succede dopo comincia a diventare... strano. La ricerca di handler nelle sovra-classi si arresta, e pertanto wxPython non è in grado di gestire il corretto funzionamento del bottone: notate infatti che non assume il caratteristico aspetto "abbassato". 

Il ``wx.EVT_LEFT_UP`` (contrariamente a quando forse vi aspettate) viene ancora emesso quando sollevate il pulsante: in realtà l'oggetto-evento del mouse (l'istanza della classe ``wx.MouseEvent``) è creato da wxPython allo startup dell'applicazione, e resta sempre in circolazione: assume di volta in volta differenti "event type" (e quindi può essere collegato da differenti binder) a seconda dell'azione specifica del mouse in quel momento. Quindi non c'è niente di strano che un ``wx.EVT_LEFT_UP`` venga ugualmente ricosciuto e catturato, se rilasciate il pulsante del mouse finché il puntatore è ancora nell'area del bottone. 

Notate però che, se prima di risollevare il mouse allontanate il puntatore dall'area del bottone, allora il ``wx.EVT_LEFT_UP`` questa volta non verrà catturato: questo è spia di un cambiamento importante. A causa della gestione non completa del precedente ``wx.EVT_LEFT_DOWN``, adesso wxPython non è più in grado di capire che il ``wx.EVT_LEFT_UP`` deve essere attribuito comunque al bottone. Inutile dire che, in queste circostanze, non c'è modo per ``wx.EVT_LEFT_UP`` di chiudere in bellezza innescando il ``wx.EVT_BUTTON``, anche rimanete con il puntatore all'interno dell'area del bottone. Quando non avete eseguito il gestore di default del ``wx.EVT_LEFT_DOWN``, avete spezzato irrimediabilmente il meccanismo: una sequenza di "giù" e poi "su", sia pure nell'area del bottone, non basta più a far partire il ``wx.EVT_BUTTON``.

Se infine togliete lo ``Skip`` del callback ``on_up`` (riga 30), le cose diventano se possibile ancora più strane. Chiaramente i callback ``on_down`` e ``on_up`` vengono eseguiti, ma da quel momento tutto smette di funzionare correttamente. wxPython non ha modo di completare la gestione di ``wx.EVT_LEFT_UP``, e quindi nessun ``wx.EVT_BUTTON`` viene innescato. Ma ciò che è peggio, il bottone resta costantemente "premuto" rifiutando di resettarsi (potete passarci sopra il puntatore del mouse per convincervi del problema). Inoltre, adesso wxPython attribuisce ogni successivo clic del mouse al bottone: fate clic al di fuori del bottone, e vedrete che i vostri callback continuano a essere chiamati lo stesso. Ovviamente, siccome tutti i clic sono attribuiti al bottone, non potete nemmeno più chiudere la finestra dell'applicazione!

Impressionante, vero? Ovviamente questa non è una conseguenza generale che avviene ogni volta che dimenticate di chiamare ``Skip`` al momento giusto. In questo caso, molto dipende dal tipo di gestione interna che avviene nei ``wx.Button``.

Tuttavia, la regola generale resta quella: se siete in dubbio, chiamate ``Skip``.

.. index::
   single: eventi; Bind()
   single: eventi; propagazione

.. _tre_stili_di_bind:

``Bind`` e la propagazione degli eventi.
----------------------------------------

Finalmente siamo in grado di rispondere alla domanda da cui eravamo partiti: che differenza c'è tra ``widget.Bind(...)`` e ``self.Bind(..., button)``?

Per la precisione, ci sono tre modi differenti di usare ``Bind``. Per esempio::

    # 'button' e' un pulsante, 'self' e' il panel/frame/dialog che lo contiene
    
    button.Bind(wx.EVT_BUTTON, self.callback)        # (1)
    self.Bind(wx.EVT_BUTTON, self.callback, button)  # (2)
    self.Bind(wx.EVT_BUTTON, self.callback)          # (3)

Lo stile (1) collega l'evento generato da ``button`` direttamente all'handler ``button``. Questo significa che l'handler ``button`` sarà il primo a ricevere l'evento, e se ne occuperà eseguendo ``self.callback``. Se al suo interno ``self.callback`` non chiama ``Skip``, l'evento non si propagherà oltre. Nove volte su dieci, questo è lo stile di collegamento che vi serve davvero. 

Lo stile (2) collega l'evento generato da ``button`` all'handler di ``self`` (che nel nostro esempio potrebbe essere un panel, o un altro contenitore). Nove volte su dieci, questo stile ha lo stesso effetto del precedente. Tuttavia è importante capire che in questo caso l'evento viene catturato solo dopo che si è propagato qualche volta. La catena dei parent da ``button`` a ``self`` potrebbe anche essere lunga. Se nessun altro handler interviene a gestire l'evento prima di ``self``, allora effettivamente non c'è differenza tra lo stile (1) e lo stile (2). Lo stile (2) torna utile solo nei casi un cui è utile inserire diversi handler lungo la catena di propagazione.  

Ecco un esempio pratico:: 

    from itertools import cycle

    class ColoredButton(wx.Button):
        def __init__(self, *a, **k):
            wx.Button.__init__(self, *a, **k)
            self.Bind(wx.EVT_BUTTON, self.change_color)
            self.color = cycle(('green', 'yellow', 'red'))
            self.SetBackgroundColour(self.color.next())
            
        def change_color(self, event): 
            self.SetBackgroundColour(self.color.next())
            event.Skip()


    class TopFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            panel = wx.Panel(self)
            button = ColoredButton(panel, -1, 'clic!', pos=(50, 50)) 
            panel.Bind(wx.EVT_BUTTON, self.on_clic, button) 

        def on_clic(self, event): 
            print 'qui facciamo il vero lavoro...'


    app = wx.App(False)
    TopFrame(None).Show()
    app.MainLoop()

Abbiamo definito un pulsante personalizzato ``ColoredButton`` che cambia colore ogni volta che facciamo clic. Questo comportamento è codificato dal callback ``change_color``, che è collegato direttamente all'handler del pulsante stesso (riga 6: utilizziamo il primo stile). Notate che ``change_color`` chiama ``Skip``, permettendo all'evento di propagarsi per essere intercettato anche in seguito. 

Infatti, quando vogliamo usare il nostro pulsante nel mondo reale, è necessario preservare il suo comportamento di default (cambiare colore), e aggiungere il lavoro vero e proprio che vogliamo fargli fare nella nostra applicazione. Il modo è semplice: basta aspettare che l'evento arrivi al contenitore superiore (in questo caso ``panel``), e intercettarlo di nuovo (riga 20: qui usiamo il secondo stile!). 

Lo stile (3), infine, è incluso solo per maggiore chiarezza: infatti è identico allo stile (1) dal punto di vista della semantica. In entrambi i casi, colleghiamo un handler a un evento. Significa che l'handler gestirà quell'evento, ogni volta che passerà da lui, *non importa da dove provenga*. La differenza, chiaramente, è nel contesto. Nel caso dello stile (1), l'handler è un ``wx.Button`` o un altro widget specifico. E' altamente improbabile che un ``wx.Button`` sia parent di qualche altro ``wx.Button``, quindi gli unici ``wx.EVT_BUTTON`` che gli capiteranno mai sotto mano saranno quelli che emette lui stesso. D'altra parte, nel caso dello stile (3), l'handler è un contenitore che potrebbe avere al suo interno numerosi ``wx.Button``. L'handler gestirà i ``wx.EVT_BUTTON`` di *tutti* i pulsanti che sono (anche indirettamente) suoi figli. 

Naturalmente, all'interno del callback potete chiamare ``event.GetEventObject()`` e risalire così al pulsante specifico che ha emesso l'evento. Ecco un esempio::

    class TopFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            panel = wx.Panel(self)
            button_A = wx.Button(panel, -1, 'A', pos=(50, 50)) 
            button_B = wx.Button(panel, -1, 'B', pos=(50, 100))
            panel.Bind(wx.EVT_BUTTON, self.on_clic) 

        def on_clic(self, event): 
            print 'premuto', event.GetEventObject().GetLabel()


    app = wx.App(False)
    TopFrame(None).Show()
    app.MainLoop()

Ricapitolando: lo stile (1) e lo stile (3) dicono entrambi all'handler di gestire ogni evento di quel tipo, non importa da dove è partito. Lo stile (2) dice all'handler di gestire solo gli eventi di quel tipo che sono partiti da un posto specifico. Lo stile (1) e lo stile (3) sono in effetti identici nella semantica: lo stile (3) è semplicemente lo stile (1) applicato a un contenitore. 

Nella pratica, lo stile (1) è quello che va bene nella maggior parte dei casi. Lo stile (2) può aver senso se avete in mente di intercettare più di una volta lo stesso evento. Lo stile (3) è usato raramente, perché ha il problema di intercettare più di quanto in genere si vorrebbe. 


``Bind`` per gli eventi "non command". 
--------------------------------------

C'è un'altra ragione importante per cui lo stile (1) è quello più utilizzato. 

Di fatto, è **l'unico** stile di collegamento che potete usare per gli eventi non "command". Infatti, siccome questi non si propagano, la vostra unica chance di intercettarli è rivolgengovi all'handler dello stesso widget che li ha generati. 

Di conseguenza, lo stile (1) va bene per tutti gli eventi, "command" e no. 

Ricordatevi comunque di chiamare ``Skip`` nel callback degli eventi "non command", per permettere a wxPython di ricercare il comportamento predefinito nelle sovra-classi.

.. _esempio_finale_propagazione:

Un esempio finale per la propagazione degli eventi.
---------------------------------------------------

Questo esempio riassume quello che abbiamo detto fin qui sulla propagazione degli eventi. Fate girare questo codice, e osservate in che ordine vengono chiamati i callback::

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
          return True

      def onclic(self, evt):
          print 'clic dalla wx.App'
          evt.Skip()


  app = MyApp(False)
  Test(None).Show()
  app.MainLoop()

Questo esempio copre i casi comuni e alcuni scenari più avanzati. Tuttavia, non è ancora completo: quando verrà il momento di parlare degli :ref:`handler personalizzati<handler_personalizzati>`, ne scriveremo :ref:`una versione più ampia<esempio_finale_propagazione_aggiornato>`.
