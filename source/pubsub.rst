.. highlight:: python
   :linenothreshold: 15

.. _pubsub:

.. index::
   single: pub/sub
   
Pattern: Publisher/Subscriber.
==============================

Affrontiamo in questa pagina un design pattern di grande importanza nel mondo delle applicazioni gui: Publisher/Subscriber (pub/sub, per brevità). 

Questa pagina è un anello di congiunzione tra quelle, numerose, che abbiamo dedicato agli eventi, e quella sul pattern Model/Controller/View. E' consigliabile proseguire nella lettura solo se conoscete abbastanza bene il modello a eventi di wxPython: in particolare, :ref:`come si propagano<eventi_avanzati>`.

.. todo:: una pagina su MCV con riferimenti a questa.

I design pattern in generale sono molto importanti e studiati nell'ambito della programmazione a oggetti. Non è questa la sede per introdurre la filosofia dei pattern, spiegare cosa sono e quali problemi aiutano a risolvere. In rete e in libreria si può trovare moltissimo: qui diamo per scontato che sappiate orientarvi già a sufficienza nella programmazione a oggetti.

Che cosa è pub/sub.
-------------------

Detto molto in breve, pub/sub è un pattern per implementare un sistema di messaggistica molti-a-molti tra un numero arbitrario di oggetti. "Molti-a-molti" significa che ciascun oggetto può sia inviare messaggi a, sia ricevere messaggi da, potenzialmente tutti gli altri oggetti. 

Un "messaggio" è in definitiva la chiamata a una funzione (metodo) di un oggetto remoto. Di norma, affinché un oggetto B possa chiamare un metodo di un altro oggetto A, è necessario che B "conosca" A: ovvero, che conservi un riferimento interno a A. Per esempio::

    >>> class A (object): 
            def foo(self):
                return "sono A.foo"

    >>> class B (object): 
            def __init__(self, reference_to_a):
                self.a = reference_to_a # B adesso conosce A
            
            def call_foo(self):
                return self.a.foo()

    >>> a = A()
    >>> b = B(reference_to_a=a)
    >>> b.call_foo() # restituisce "sono A.foo"

Questo funziona, ma così A e B sono "accoppiati", come si dice. Il pattern pub/sub permette di scambiare messaggi tra oggetti senza che abbiano necessità di "conoscersi" tra loro, aiutando a mantenere quel disaccoppiamento tra le parti che è il cuore della programmazione a oggetti. 

Per raggiungere questo scopo, tutti gli oggetti interessati si rivolgono a un unico oggetto intermediario dei messaggi. L'intermediario mantiene al suo interno un elenco di tutti gli oggetti "iscritti" al sistema, e riceve i messaggi di ciascuno di loro. Quando l'intermediario riceve un messaggio, lo inoltra a tutti gli oggetti del suo elenco. Se un oggetto vuole partecipare al sistema dei messaggi, si iscrive presso l'intermediario. Tutto ciò che i partecipanti hanno bisogno di conoscere, è l'intermediario. 

Si possono trovare in rete molte implementazioni di pub/sub, anche in Python. Ecco un esempio molto rudimentale, solo per aiutare a visualizzare quanto detto fin qui::

    class Publisher(object):
        def __init__(self):
            self._subscribers = set()

        def subscribe(self, new_subscriber):
            self._subscribers.add(new_subscriber)

        def unsubscribe(self, old_subscriber):
            self._subscribers.discard(old_subscriber)

        def publish(self, message):
            for subscriber in self._subscribers:
                subscriber(message)

    class Foo(object):   # un subscriber
        def __init__(self, name, publisher):
            self.name = name
            self._publisher = publisher

        def make_subscription(self, subscribe=True):
            if subscribe:
                self._publisher.subscribe(self.deal_with_incoming_message)
            else:
                self._publisher.unsubscribe(self.deal_with_incoming_message)

        def say_hello(self):
            self._publisher.publish('Hello world da... ' + self.name)

        def deal_with_incoming_message(self, message):
            print 'Sono', self.name, 'e ho ricevuto:', message

    pub = Publisher()
    andrea = Foo('Andrea', pub)
    mario = Foo('Mario', pub)
    andrea.make_subscription()
    mario.make_subscription()
    andrea.say_hello()

Potete fare un po' di prove con questo giocattolo, aggiungendo altre istanze di ``Foo``, o scrivendo altre classi da aggiungere al sistema di messaggistica. In realtà ci sono poche regole: la "sottoscrizione" consiste in sostanza nel fornire all'intermediario un riferimento a un metodo da chiamare ogni volta che bisogna consegnare un messaggio (nel nostro caso, ``deal_with_incoming_message``). Un dettaglio importante è la signature del metodo da usare per la sottoscrizione: nella nostra implementazione, il metodo deve accettare esattamente un solo argomento (``message``), perché l'intermediario lo chiamerà "alla cieca" fidandosi che l'interfaccia sia giusta (nel nostro esempio, la chiamata ``subscriber(message)``).

.. index::
   single: pub/sub; wx.lib.pubsub
   single: wx.lib; pubsub

``wx.lib.pubsub``: l'implementazione wxPython di pub/sub.
---------------------------------------------------------

Avere un sistema di messaggistica tra i componenti, implementato secondo la logica di pub/sub, è un aspetto molto importante per un gui framework, per ragioni che saranno chiare tra poco. 

Per questo wxPython mette a disposizione una sua versione di pub/sub: si tratta di una libreria completamente indipendente dal resto del framework, e quindi si può usare anche in progetti non legati al mondo wx (si può anche scaricare e installare a parte: la documentazione completa si trova `sul sito <http://pubsub.sourceforge.net/>`_).

Per lavorare con questa versione di pub/sub, basta importare::

    from wx.lib.pubsub import pub

``wx.lib.pubsub`` si basa su una classe ``Publisher`` simile alla nostra, ma molto più raffinata. Prima di tutto, ``Publisher`` è implementata come `Singleton <https://it.wikipedia.org/wiki/Singleton>`_: solo una istanza di Publisher può vivere nel nostro programma. Questo ci risparmia la noia di creare noi stessi una prima istanza, e poi passarla in giro (nel nostro esempio di sopra, in ``Foo.__init__``). Addirittura, l'api di ``wx.lib.pubsub`` nasconde completamente la classe ``Publisher``: basta importare ``pub`` per avere accesso, dietro le quinte, a una istanza unica di ``Publisher``.

.. note:: le versioni precedenti di ``wx.lib.pubsub`` avevano un'api diversa, che esponeva direttamente ``Publisher``. La libreria si usava importando ``from wx.lib.pubsub import Publisher``, in sostanza con le stesse funzionalità. La nuova api è stata inclusa in wxPython a partire dalla versione 2.9. Già a partire dalla versione 2.8.11.0, la nuova api poteva tuttavia essere abilitata con ``import wx.lib.pubsub.setupkwargs; from wx.lib.pubsub import pub``. Se avete una versione ancora più vecchia (o se trovate in giro degli esempi vecchi), potete comunque seguire questa pagina senza problemi, dal momento che la conversione è immediata. 

In secondo luogo, ``Publisher`` conserva il suo "elenco degli abbonati" come una lista di `weak references <https://docs.python.org/2/library/weakref.html>`_. Questo ci risparmia il disturbo di cancellare la sottoscrizione di un oggetto, prima di distruggerlo (altrimenti il riferimento esistente dentro la lista degli abbonati non ci permetterebbe di distruggerlo!). Ancora meglio, quando distruggiamo un oggetto abbonato, ``Publisher`` se ne accorge e lo rimuove automaticamente dalla sua lista.

In terzo luogo, ``Publisher`` è in grado di differenziare i messaggi per "argomento" (topic): quando si pubblica un messaggio, si deve specificare anche il suo topic. E d'altra parte, ci si può abbonare anche solo ad alcuni topic. In questo modo è possibile separare le comunicazioni di oggetti diversi in ambiti diversi, senza obbligare ciascun componente ad ascoltare tutto il traffico dei messaggi.

Ma c'è di più: è possibile creare delle gerarchie di topic, per esempio "notizie", "notizie.sport", "notizie.politica", "notizie.spettacolo", etc. In questo modo, chi si abbona a "notizie.politica" riceverà solo i messaggi con questo topic. Chi invece si abbona a "notizie" riceverà i messaggi del topic più generale, e quelli di tutti i sub-topic.

Per tutti i dettagli di ``wx.lib.pubsub`` vi rimandiamo alla documentazione on-line: `quella di wxPython "classic" <http://www.wxpython.org/docs/api/wx.lib.pubsub-module.html>`_ purtroppo documenta solo la vecchia api, ed è pertanto superata. Ma la `documentazione di Phoenix <http://wxpython.org/Phoenix/docs/html/lib.pubsub.pub.html#module-lib.pubsub.pub>`_ (la futura versione di wxPython, ancora da completare) è invece aggiornata. La documentazione migliore, tuttavia, è `nel sito stesso <http://pubsub.sourceforge.net/usage/usage_basic.html#label-usage-basic>`_ di ``pubsub``. 

Un esempio di architettura pub/sub in wxPython.
-----------------------------------------------

Una situazione tipica dove pub/sub si può usare con successo in una gui, è quando volete mantenere sincronizzato lo stato di molti diversi componenti: potrebbero essere dei widget all'interno di una finestra, o anche in finestre separate. Questo esempio minimo dovrebbe aiutare a chiarire i termini del problema::

    from wx.lib.pubsub import pub

    TOPIC_VALUE_UPDATED = 'value-updated'

    class Test(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            self.slider = wx.Slider(p, -1, 50, 0, 100, 
                                    style=wx.SL_VERTICAL)
            check = wx.CheckBox(p, -1, 'connesso')
            button = wx.Button(p, -1, 'nuovo')

            self.slider.Bind(wx.EVT_SLIDER, self.on_slider)
            check.Bind(wx.EVT_CHECKBOX, self.on_check)
            button.Bind(wx.EVT_BUTTON, self.on_clic)

            s = wx.BoxSizer(wx.VERTICAL)
            for ctl in (self.slider, check, button):
                s.Add(ctl, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, 20)
            p.SetSizer(s)
            s.Fit(self)

            pub.subscribe(self.update_value, TOPIC_VALUE_UPDATED)
            check.SetValue(True)

        def update_value(self, message):
            self.slider.SetValue(message)

        def on_slider(self, evt):
            pub.sendMessage(TOPIC_VALUE_UPDATED, 
                            message=self.slider.GetValue())

        def on_check(self, evt):
            if evt.IsChecked(): 
                pub.subscribe(self.update_value, TOPIC_VALUE_UPDATED)
            else:
                pub.unsubscribe(self.update_value, TOPIC_VALUE_UPDATED)

        def on_clic(self, evt):
            Test(self).Show()

    if __name__ == '__main__':
        app = wx.App(False)
        Test(None).Show()
        app.MainLoop()

Per mantenere più compatto il codice, qui le finestre da sincronizzare sono in realtà istanze diverse dalla stessa classe ``Test``: ma potete naturalmente sperimentare per conto vostro esempi più elaborati. 

La meccanica di base di ``wx.lib.pubsub``, come si vede, è molto facile da capire. Un "messaggio" può essere in realtà qualsiasi oggetto python (nel nostro caso trasmettiamo un semplice valore numerico, ma nulla vieta di passare strutture dati più complesse). Un "topic" è una semplice stringa di testo: per praticità, conviene astrarre i topic in variabili globali dichiarate all'inizio del modulo, soprattutto quando i topic cominciano a diventare numerosi. Una gerarchia di topic si crea con la tipica sintassi "col punto": "topic", "topic.sub-topic", "topic.sub-topic.sub-sub-topic", etc. ``wx.lib.pubsub`` offre alcune funzionalità più avanzate, che qui non descriviamo, rimandandovi alla documentazione. 

Più interessante è capire come ``wx.lib.pubsub`` implementa in pratica il pattern pub/sub. Come si vede, ogni componente può abbonarsi e cancellare l'abbonamento in qualsiasi momento, a run-time. Il sistema è completamente indifferente a quali e quanti componenti sono abbonati. Ciascun componente è in grado di trasmettere e ricevere. Un componente potrebbe trasmettere di volta in volta messaggi con topic diversi. Al limite, nulla vieta di abbonare lo stesso metodo per l'ascolto di diversi topic (ma questa non è una buona pratica: conviene riservare metodi separati per l'ascolto di topic separati. Oppure, se si è interessati all'ascolto di più topic, conviene raggrupparli in una gerarchia). 

.. index::
   single: pub/sub; confronto con gli eventi
   single: parent, catena dei
   single: eventi; propagazione

Messaggi pub/sub ed eventi wxPython.
------------------------------------

Pub/sub è un pattern che permette di scambiare messaggi tra componenti. Questa è però anche la funzione svolta dal sistema degli eventi, a cui abbiamo dedicato molte pagine. Un evento è simile a un messaggio pub/sub nel senso che si origina in un componente, e provoca la chiamata a un metodo remoto (callback) precedentemente collegato mediante una registrazione (è il compito di ``Bind``, come sappiamo). Proprio l'esempio qui sopra ci permette di approfondire alcune differenze importanti tra i messaggi di ``wx.lib.pubsub`` e gli eventi wxPython. 

In primo luogo, si noti che i messaggi di ``wx.lib.pubsub`` si trasmettono senza nessun riguardo per la :ref:`catena dei parent<catenaparent>`. Nel nostro esempio, ogni nuova finestra è figlia di quella in cui abbiamo cliccato sul pulsante "nuovo", e quindi si possono facilmente creare anche finestre "cugine": tuttavia, i messaggi si trasmettono indifferentemente non solo lungo la linea genitori/figli, ma anche ai cugini più lontani. Per contrasto, si ricordi invece che gli eventi :ref:`si propagano<eventi_avanzati>` solo lungo la catena dei parent (torneremo su questo tra poco).

In secondo luogo, ``wx.lib.pubsub`` è un sistema di messaggistica molti-a-molti: ogni componente può iscriversi all'ascolto dei messaggi di tutti gli altri, e mandare a sua volta messaggi a tutti. Per contrasto, ricordiamo che gli eventi possono essere collegati solo in modalità uno-a-uno o al massimo uno-a-molti. E' possibile registrare lo stesso "ascoltatore" (callback) a ricevere più eventi::

    button.Bind(wx.EVT_BUTTON, self.listener)
    another_button.Bind(wx.EVT_BUTTON, self.listener)
    # self.listener ascolta gli eventi da due pulsanti diversi

Ma non è possibile registrare due ascoltatori diversi per intercettare lo stesso evento, per esempio::

    button.Bind(wx.EVT_BUTTON, self.listener)
    button.Bind(wx.EVT_BUTTON, self.another_listener)
    # qui l'ultimo a registrarsi è quello che riceverà l'evento

A voler essere precisi, sappiamo già che questo non è del tutto vero: un evento si propaga, e diversi callback possono intercettarlo in successione, ma solo se gli event handler da cui sono chiamati appartengono alla catena dei parent, e solo se ogni callback ha cura di chiamare ``Skip``.

In ogni caso, l'impressione complessiva è che pub/sub offra una soluzione più universale e al contempo elegante di gestire i messaggi tra i componenti di un'applicazione gui. La domanda spontanea è: ma non sarebbe possibile fare del tutto a meno degli eventi, e gestire ogni cosa attraverso ``wx.lib.pubsub``?

Beh, no. Non sarebbe possibile, e forse neanche troppo conveniente. 

Prima di tutto, wxPython si basa comunque sugli eventi: quando l'utente fa clic su un pulsante, è un ``wx.CommandEvent`` che viene innescato, non un messaggio pub/sub. Anche nel nostro esempio qui sopra, siamo comunque partiti da un ``wx.EVT_SLIDER``, e solo nel callback collegato abbiamo avviato la macchina di ``wx.lib.pubsub``. Inoltre, wxPython usa gli eventi anche per tutti i suoi "messaggi di servizio": per segnalare che una porzione di interfaccia deve essere ridisegnata (``wx.EVT_UPDATE_UI``); per segnalare che le dimensioni della finestra stanno cambiando (``wx.EVT_SIZE``); perfino per dire che non sta facendo nulla (``wx.EVT_IDLE``), e molto altro ancora. Non è realistico pensare di sostituire integralmente la macchina degli eventi con qualcos'altro. 

Ma c'è di più. Gli eventi (``wx.Event`` e derivati) sono oggetti complessi, organizzati in gerarchie, fatti apposta per conservare molte informazioni sul contesto che li ha generati. Un messaggio di ``wx.lib.pubsub``, di per sé, non conserva neppure il riferimento all'oggetto da cui è partito. Naturalmente anche con pub/sub si potrebbe implementare una gerarchia di classi "messaggio", istanziare la classe appropriata, riempirla delle necessarie informazioni, e infine trasmetterla come messaggio - ma appunto, è una cosa che andrebbe implementata da zero. 

Inoltre, proprio l'estrema libertà di propagazione dei messaggi pub/sub potrebbe non essere la cosa più desiderabile nel contesto di una applicazione gui. C'è un motivo per cui solo i ``wx.CommandEvent`` si propagano, e si propagano solo lungo la catena dei parent: nel 90% dei casi è proprio quello che vi serve. Le tipiche interfacce grafiche sono organizzate in finestre che contengono panel che contengono pulsanti e altri widget: il rispetto di questa gerarchia vi permette di evitare che componenti estranei possano essere disturbati da messaggi che non li riguardano. E' facile e comodo contenere i messaggi degli eventi in flussi separati. Naturalmente anche i topic di ``wx.lib.pubsub`` hanno una funzione analoga: tuttavia, bisognerebbe costruire una gerarchia di topic elastica, che si adatti alla creazione e distruzione di nuove finestre, alla disattivazione occasionale di parti dell'interfaccia, etc. E ancora una volta, tutto questo andrebbe implementato a partire da zero. 

Infine, vale la pena di ricordare che ``wx.lib.pubsub`` non dà nessuna garanzia di recapitare un messaggio ai suoi destinatari in un ordine predefinito. Gli eventi, d'altra parte, vengono processati nell'ordine determinato dalla catena dei parent; ed è possibile manipolare ulteriormente lo stack degli handler, :ref:`come sappiamo<handler_personalizzati>`. 

.. index::
   single: Qt
   single: pub/sub; confronto con signal/slot

Qt e Wx: diversi approcci agli eventi (una digressione).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ma questo non vuol dire che quello di wxPython sia l'unico approccio possibile per gli eventi in ambito di applicazioni gui. Per esempio, Qt percorre una strada differente. 

Qt è una delle principali alternative a wxWidgets per quanto riguarda la costruzione di interfacce grafiche desktop. Come wxWidgets, Qt è un framework scritto in C++. Come wxWidgets, Qt è un framework vasto, robusto e anziano (Qt è del 1991, Wx del 1992). `PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_ e `PySide <https://wiki.qt.io/PySide>`_ sono due binding per Python di Qt (come wxPython è un binding di wxWidgets). 

La gestione degli eventi in Qt avviene interamente con un meccanismo di tipo pub/sub, che loro chiamano "Signals & Slots". L'implementazione di pub/sub di Qt ha avuto un enorme successo e si è estesa anche ad altri ambiti, al punto che "signal/slot" è un sinonimo comune per "pub/sub". 

`In questa pagina <http://doc.qt.io/qt-5/signalsandslots.html>`_ si legge, per esempio (traduzione mia, abbreviata e depurata dagli aspetti troppo legati a C++): 

    Il meccanismo signal/slot è forse la parte che più si differenzia dagli altri framework. (...)
    Gli altri framework implementano questo tipo di comunicazioni grazie ai callback. (...) I callback hanno due problemi fondamentali: (...) In secondo luogo, il callback è fortemente accoppiato alla funzione chiamante, dal momento che questa deve conoscere il callback da chiamare. 

Il bersaglio principale, qui, è naturalmente wxWidgets. "Callback" è un termine generico, e inoltre è difficile tradurre in Python questi concetti legati al mondo C++: tuttavia, il primissimo esempio che abbiamo fatto in questa pagina (quello con ``class A`` e ``class B``) potrebbe dare l'idea di un callback "classico", con i relativi problemi di accoppiamento a cui alludono gli autori di Qt. 

Questa pagina della documentazione Qt fa riferimento, in effetti, a un mondo che nel frattempo è cambiato parecchio. wxWidgets ha abbandonato il suo originale modello rigido basato sui callback, e un fattore scatenante di questa trasformazione è stato proprio wxPython con il suo ``Bind``, che è stato introdotto da Robin Dunn e solo in seguito implementato anche nella versione "madre" del framework (a partire da wxWidgets 2.9). In effetti, :ref:`un binder<cosa_e_binder>` svolge una funzione un po' simile a quella di un "Publisher" in pub/sub: è un oggetto mediatore che permette di disaccoppiare eventi, event handler e callback. 

In un certo senso, quindi, la gestione degli eventi in wxWidgets è diventata anch'essa più simile al modello pub/sub. Da un lato, probabilmente, la versione "signal/slot" di Qt resta più elegante e coerente: per esempio, è possibile usare lo stesso modello per gestire gli eventi nativi dell'interfaccia (clic sui pulsanti, etc.) e per qualsiasi altro messaggio occorre scambiare tra i componenti. Dall'altro, wxWidgets mette a disposizione un sistema più strutturato e adeguato alle normali esigenze degli eventi nativi. Quando però c'è bisogno di qualcosa di diverso, occorre integrare in altri modi. 

.. index::
   single: eventi; Event Manager
   single: wx.lib.evtmgr; eventManager

Event Manager: a metà strada tra eventi e pub/sub.
--------------------------------------------------

:ref:`Abbiamo già introdotto<eventmanager>` ``wx.lib.evtmgr``: si tratta di una piccola libreria che si appoggia internamente a ``wx.lib.pubsub`` per offrire un modo più elegante di collegare gli eventi, e alcune funzionalità in più rispetto al tradizionale ``Bind``.

Event Manager non offre comunque tutta la libertà di pub/sub. In effetti, non è facile replicare esattamente la funzionalità del nostro esempio con gli slider sincronizzati, usando solo Event Manager. Una possibile approssimazione, che ci mostra comunque degli aspetti interessanti, è questa::

    from wx.lib.evtmgr import eventManager

    class Test(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            self.slider = wx.Slider(p, -1, 50, 0, 100, 
                                    style=wx.SL_VERTICAL)
            check = wx.CheckBox(p, -1, 'connesso')
            button = wx.Button(p, -1, 'nuovo')

            parent = self.GetParent()
            self.target = parent.slider if parent else self.slider
            
            eventManager.Register(self.update_value, wx.EVT_SLIDER, self.target)
            # usiamo il vecchio Bind per gli altri eventi di routine
            # ma potremmo usare Event Manager per tutti
            check.Bind(wx.EVT_CHECKBOX, self.on_check)
            button.Bind(wx.EVT_BUTTON, self.on_clic)

            s = wx.BoxSizer(wx.VERTICAL)
            for ctl in (self.slider, check, button):
                s.Add(ctl, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, 20)
            p.SetSizer(s)
            s.Fit(self)

            check.SetValue(True)

        # confronto: EventMananger             |   pub/sub
        def update_value(self, evt):           # def update_value(self, message):
            self.slider.SetValue(evt.GetInt()) #     self.slider.SetValue(message)

        def on_check(self, evt):
            if evt.IsChecked(): 
                eventManager.Register(self.update_value, wx.EVT_SLIDER, self.target)
            else:
                eventManager.DeregisterListener(self.update_value)

        def on_clic(self, evt):
            Test(self).Show()

    if __name__ == '__main__':
        app = wx.App(False)
        Test(None).Show()
        app.MainLoop()

E' interessante confrontare il modo in cui comunichiamo il valore da assegnare allo slider: con pub/sub, il valore è il contenuto del messaggio. Con Event Manager, d'altra parte, trasferiamo pur sempre degli eventi wxPython, e quindi recuperiamo il valore che ci interessa direttamente dall'evento. 

A parte questo, la limitazione di Event Manager è chiara: siccome stiamo comunque registrando eventi wxPython, dobbiamo sapere quale event handler utilizzare. Nel nostro esempio, abbiamo scelto di sfruttare il fatto che ogni finestra "conosce" il suo parent diretto, e quindi il "target" è lo slider del parent (tranne per la finestra iniziale, che non ha nessun parent). Questo però limita la trasmissione dell'evento alla catena dei parent: gli slider non restano sincronizzati tra finestre "cugine". Per ottenere una sincronizzazione completa, dovremmo gestire noi stessi la contabilità delle finestre aperte in qualche tipo di registro globale, magari da conservare nella ``wx.App`` - ma allora, tanto vale ricorrere direttamente a pub/sub. 

Anche se Event Manager non permette tutta la flessibilità di pub/sub, offre comunque qualcosa in più rispetto a ``Bind``: in particolare, con Event Manager è possibile registrare più ascoltatori per un singolo evento. Potete verificarlo con l'esempio qui sopra: se generate diverse finestre figlie da una stessa finestra, noterete che un solo parent è in grado di "comandare" tutti i figli contemporaneamente. Questo non sarebbe possibile collegando l'evento nel modo tradizionale: potete verificarlo cambiando una riga nel codice dell'esempio qui sopra::

    # sostituite questo...
    eventManager.Register(self.update_value, wx.EVT_SLIDER, self.target)
    # ... con questo:
    self.target.Bind(wx.EVT_SLIDER, self.update_value)

Adesso, se provate a generare più figli dallo stesso parent, noterete che il parent comanda solo l'ultimo della serie. 

.. note:: se avete compreso fino in fondo come funzionano gli eventi in wxPython, forse vi sarà già venuta in mente una scappatoia. Nel nostro caso specifico, siccome stiamo cercando di sincronizzare widget legati in una catena di parent, potremmo ancora raggiungere l'effetto desiderato chiamando ``evt.Skip()`` nel callback ``update_value``. Tuttavia questa tecnica è valida solo per questo esempio particolare. Se volessimo registrare, per uno stesso evento, molti ascoltatori non legati da nessuna particolare parentela, ``Bind`` non potrebbe più aiutarci, ed Event Manager sarebbe l'unica soluzione (oltre a pub/sub, naturalmente).

A conti fatti, Event Manager non è probabilmente lo strumento giusto da usare quando volete notificare un evento ad ascoltatori arbitrariamente lontani e generati dinamicamente. Se vi serve davvero questo tipo di flessibilità, probabilmente vi conviene usare direttamente ``wx.lib.pubsub``. 

Tuttavia, in una tipica applicazione gui, questo scenario non è così frequente. E' più comune il caso in cui serve notificare un evento da un "generatore" a un certo numero di "subordinati": in casi del genere, Event Manager è perfettamente a suo agio. Potete trovare un esempio del genere nella demo di wxPython (cercate "Event Manager"), ma il codice è un po' barocco e difficile da leggere. Ecco una versione estremamente semplificata della stessa idea:: 

    from wx.lib.evtmgr import eventManager

    class MySlider(wx.Slider):
        def __init__(self, parent, id, value, minValue, maxValue, target):
            wx.Slider.__init__(self, parent, id, value, minValue, 
                               maxValue, style=wx.SL_VERTICAL)
            eventManager.Register(self.update, wx.EVT_SLIDER, target)

        def update(self, evt):
            self.SetValue(evt.GetInt())

    class Test(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            master_slider = wx.Slider(p, -1, 50, 0, 100, 
                                      style=wx.SL_VERTICAL)
            s = wx.BoxSizer(wx.HORIZONTAL)
            for i in range(10):
                slider = MySlider(p, -1, 50, 0, 100, master_slider)
                s.Add(slider, 1, wx.EXPAND|wx.ALIGN_CENTRE_HORIZONTAL, 10)
            s1 = wx.BoxSizer(wx.VERTICAL)
            s1.Add(master_slider, 1, wx.ALIGN_CENTRE_HORIZONTAL, 10)
            s1.Add(s, 1, wx.EXPAND|wx.ALL, 5)
            p.SetSizer(s1)

    if __name__ == '__main__':
        app = wx.App(False)
        Test(None).Show()
        app.MainLoop()

In conclusione...
-----------------

wxPython mette a disposizione un insieme articolato (anche se obiettivamente disarmonico) di strumenti per gestire la comunicazione tra i componenti. 

Nel caso più semplice (e frequente), gli eventi e ``Bind`` sono tutto ciò che vi serve. 

Occasionalmente, potreste voler creare un :ref:`evento personalizzato<eventi_personalizzati>` e postarlo nella coda degli eventi. Questo avviene tipicamente quando sottoclassate un widget per personalizzarlo; ma è comune anche usare questo metodo per inviare messaggi personalizzati non-nativi. Inoltre, ``wx.PostEvent`` è una delle due tecniche classiche per la comunicazione inter-thread (l'altra è wrappare una semplice chiamata di funzione in ``wx.CallAfter``). 

.. todo:: una pagina sui thread.

Più raramente ancora, :ref:`qualche trucco con gli event handler<handler_personalizzati>` potrebbe aiutarvi, soprattutto a gestire l'ordine di esecuzione dei callback.

Se avete bisogno che diversi widget possano rispondere allo stesso evento, la semplice accoppiata di ``Bind`` e ``Skip`` dovrebbe bastare, almeno fino a quando riuscite a organizzare tutti gli attori coinvolti nella stessa catena dei parent. 

Ma se questo non fosse possibile (o se risultasse in un'organizzazione troppo innaturale; o se semplicemente non avete voglia di complicarvi la vita con ``Skip``), allora Event Manager molto probabilmente è ciò che vi serve. 

Nei casi in cui neppure Event Manager può darvi una mano, non esitate a ricorrere direttamente a ``wx.lib.pubsub``. Vi conviene comunque usare pub/sub per tutte le notifiche che non nascono direttamente dagli eventi nativi dell'interfaccia (oppure potete usare eventi personalizzati e postarli in coda: ma spesso è un'alternativa scomoda). Ricordate che pub/sub non potrà mai sostituire completamente gli eventi, quindi la vostra applicazione sarà sempre ibrida: spetta a voi capire fino a che punto usare pub/sub, e quando invece vi conviene lasciare le cose in mano alla propagazione degli eventi. Inoltre, un messaggio pub/sub è di per sé meno strutturato di un evento wxPython: è possibile che dobbiate definire delle api precise per dare una struttura ai vostri messaggi. Anche la strategia dei topic di ``wx.lib.pubsub`` non è sovrapponibile alla logica di propagazione degli eventi. Ricordate infine che pub/sub non è thread-safe: se un messaggio pub/sub proveniente da un thread secondario ha come effetto di modificare la gui, dovete sempre inserirlo in un ``wx.CallAfter`` (ma in ogni caso, usare pub/sub per comunicare tra i thread è una strategia un po' avventurosa).

In conclusione, l'importante è capire che tutti questi strumenti, usati in modo intelligente, vi aiutano nel fondamentale compito di mantenere disaccoppiati i componenti, e separare gli ambiti di interesse delle varie sezioni della vostra applicazione. Questo è il cuore della programmazione a oggetti, e in particolare del pattern Model/Controller/View di cui parliamo in una pagina separata. 
