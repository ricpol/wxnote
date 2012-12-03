.. _eventibasi:

.. index::
   single: eventi
   
   
Gli eventi: le basi da sapere.
==============================

wxPython, come tutti gli altri, è un gui framework "event-driven": il suo ``MainLoop``, una volta avviato, si mette in ascolto degli eventi generati dall'utente, e risponde a essi nel modo che voi avete stabilito. 

Ogni istante della vita di un'applicazione wxPython è affollata di eventi, visto che praticamente ogni cosa ne innesca uno: non solo le interazioni "di alto livello" (premere un pulsante, scegliere una voce di menu, etc.), ma anche la pressione dei tasti, lo spostamento del mouse, il cambiamento di dimensioni di una finestra, e molte molte altre cose ancora, tuuo genera eventi. Perfino quando tutto il resto tace, viene generato di continuo un ``wx.EVT_IDLE``, per segnalare che il ``MainLoop`` in quel momento non ha niente da fare!

Come potete immaginare, wxPython offre moltissime possibilità di controllo sugli eventi. Il rovescio della medaglia è che il sistema è molto difficile da comprendere nei dettagli. In questa pagina diamo uno sguardo a volo d'uccello ai vari attori coinvolti, ma esaminiamo esclusivamente gli aspetti più semplici, che vi servono a gestire le situazioni normali. Rimandiamo :ref:`a una pagina separata <eventi_avanzati>` l'analisi degli aspetti più complessi. 


Gli attori coinvolti.
---------------------

.. index::
   single: wx; Event
   single: eventi; wx.Event()
   
Che cosa è un evento.
^^^^^^^^^^^^^^^^^^^^^

Ecco, questo sarebbe già uno degli aspetti complessi. Per il momento vi basta sapere che gli eventi sono degli oggetti (che altro?), istanze della classe ``wx.Event``,  o più probabilmete di una delle sue molteplici sottoclassi. Questi oggetti sono in effetti dei segnali: vengono creati quando "succede qualcosa", e viaggiano liberamente nello spazio (davvero: non vi serve sapere altro). Se qualcuno è interessato al messaggio che portano, lo intercetta. Altrimenti, poco male. Per esempio, quando l'utente fa clic su un pulsante, il pulsante lancia una istanza di ``wx.CommandEvent`` che contiene informazioni sul pulsante che è stato premuto. 

Tuttavia, a causa del complesso sistema con cui wxWidgets (il framework C++ su cui wxPython è basato) gestisce gli eventi, voi non incontrerete mai di persona un oggetto-evento, almeno finché vi limitate alle basi. 

E allora, che cosa incontrate nella vita di tutti i giorni? Ancora un po' di pazienza, prego.

.. index::
   single: eventi; callback
   
Che cosa è un callback.
^^^^^^^^^^^^^^^^^^^^^^^

Questo è facile. Un callback è un pezzo di codice che volete che sia eseguito in risposta a un dato evento. E' semplicemente una funzione, o un metodo di una classe, che scrivete voi stessi. Per essere qualificato come callback, è necessario che la funzione *riceva uno e un solo argomento* (oltre a ``self`` se è un metodo, naturalmente). E questo argomento deve essere un riferimento all'oggetto-evento stesso. Quindi, qualcosa come::

    def my_callback(event):
        # etc etc
        
oppure::

    def my_callback(self, event):
        # etc etc
        
Ovviamente all'interno della vostra funzione potete anche non usare per nulla il riferimento all'evento. 

I callback saranno chiamati automaticamente da wxPython quando sarà necessario. Tuttavia, non c'è niente di magico in un callback: se talvolta volete chiamarlo manualmente (in assenza di qualunque evento), potete farlo passando per esempio ``None`` al posto dell'evento::

    my_callback(None) # esegue manualmente il callback
    
Addirittura, se pensate che questo modo di chiamare il callback avverrà spesso, potete far uso dei valori di default, e definire il callback così::

    def my_callback(self, event=None):
        # etc etc
        
In questo modo, wxPython non avrà comunque problemi, e voi all'ccorrenza potete chiamarlo anche solo così::

    my_callback() # esegue manualmente il callback
    
Resta inteso che, se il codice del callback fa davvero uso del riferimento all'evento, e quindi si trova disorientato quando gli passate ``None``, questo è un problema vostro. 

Attenzione, ancora un po' di confusione: spesso nei testi inglesi trovate "handler" per dire semplicemente "callback". Il significato è in genere ovvio dal contesto. E' ancora più chiaro quando trovate "handler function" o "handler method": questo vuol dire senz'altro "callback". Tuttavia, a rigore un "handler" è un'altra cosa, come vedremo subito.

Ora, come potete collegare effettivamente il callback all'evento che volete intercettare? Ancora un po' di pazienza! 

.. index::
   single: eventi; handler
   single: wx; EvtHandler()

Che cosa è un handler.
^^^^^^^^^^^^^^^^^^^^^^

All'estremo opposto degli oggetti-evento, ci sono gli "handler" (gestori). Gli handler sono classi (derivate dal genitore astratto ``wx.EvtHandler``) che conferiscono la capacità di gestire un evento, appunto. La cosa interessante è che *tutta la gerarchia dei widget wxPython* deriva anche da ``wx.EvtHandler``. Questo è come dire che, in wxPython, ogni widget ha la capacità di gestire gli eventi provenienti da ogni altro widget. 

Di nuovo, non incontrerete mai un handler nella vita di tutti i giorni. Ma questa volta il motivo è che gli handler "da soli" non esistono proprio: invece, è corretto dire che tutti i widget (pulsanti, frame, menu, liste...) *sono anche handler*. Quindi è corretto dire che, quando volete gestire un evento, a questo scopo usate le capacità di handler di un widget (di solito proprio lo stesso che ha anche emesso l'oggetto-evento!). 

E come fate a usare queste capacità di handler? Ancora un attimo di pazienza... ci siamo quasi. 

.. index::
   single: eventi; event type
   single: wx; wxEVT_*
   
Che cosa è un event type.
^^^^^^^^^^^^^^^^^^^^^^^^^

Semplicemente, una costante numerica univoca che rappresenta un evento *specifico per un certo tipo di widget*. Detto più rapidamente: un certo tipo di evento. Qui occorre una precisazione. Le classi-evento (e i conseguenti oggetti-evento) sono poche, e molti widget possono innescare lo stesso evento. Per esempio, quando fate clic su un pulsante e quando scegliete una voce di menu, in entrambi i casi si origina un ``wx.CommandEvent``. 

Un "event type", d'altra parte, identifica univocamente il tipo di evento in relazione al tipo di widget che lo emette. Per esempio::

    >>> import wx
    >>> wx.wxEVT_COMMAND_BUTTON_CLICKED
    10008

è l'id per un ``wx.CommandEvent`` quando viene emesso da un ``wx.Button``. 

Gli event type sono costanti che vivono nel namespace ``wx`` nella forma ``wx.wxEVT_*``. Ce ne sono molti, come potete immaginare::

    >>> len([i for i in dir(wx) if i.startswith('wxEVT_')])
    219

Gli event type sono un'altra delle cose che non entreranno a far parte della vostra vita quotidiana di programmatori wxPython. Ma wxPython in realtà li usa internamente per consentirvi di riferirvi, in modo trasparente, agli eventi *non in quanto tali*, ma *in quanto emessi da uno specifico widget*. Il che è in genere quello che volete. 

Ma per capire come, in pratica, potete riferirvi agli eventi... ehm, dovete pazientare un'ultima volta. 

.. index::
   single: eventi; binder
   single: wx; PyEventBinder()
   single: wx; EVT_*

Che cosa è un binder.
^^^^^^^^^^^^^^^^^^^^^

Un binder è un oggetto usato per legare uno specifico event type, uno specifico handler e uno specifico callback. I binder sono istanze della classe ``wx.PyEventBinder``, e sono creature tipiche solo di wxPython. In effetti i binder sono il modo in cui wxPython semplifica il processo di gestione degli eventi di wxWidget. 

I binder sono gli oggetti che potete incontrare davvero (finalmente!) nella normale programmazione wxPython. Tuttavia, nella vita di tutti i giorni, non vi troverete mai a creare o manipolare direttamente un binder. 

In effetti tutti i binder necessari sono già creati da wxPython nella fase di startup (quando viene eseguita l'istruzione iniziale ``import wx``), e vivono pronti all'uso nel namespace ``wx``, sotto forma di simboli del tipo ``wx.EVT_*``. La loro nomenclatura mappa in effetti i nomi delle macro c++ che wxWidget utilizza dietro le quinte per fare i collegamenti. Inoltre, dal momento che non dovete mai creare o modificare un binder, dal vostro punto di vista sono un po' come delle costanti, e quindi ha senso che abbiano nomi tutti maiuscoli. Tuttavia in realtà basta poco per capire che sono oggetti a tutti gli effetti::

    >>> import wx
    >>> wx.EVT_BUTTON
    <wx._core.PyEventBinder object at ....>

Notate anche che::

    >>> wx.EVT_BUTTON.evtType
    [10008]
    
ossia ``wx.EVT_BUTTON`` rappresenta l'event type ``wx.wxEVT_COMMAND_BUTTON_CLICKED`` che abbiamo visto sopra, a testimoniare che un binder è legato a un event type specifico.  

Il binder, in apparenza, porta con sé soltanto l'indicazione del suo event type. Tuttavia, non è solo una sovrastruttura inutile intorno alla costante numerica dell'event type. Prima di tutto, un binder può riferirsi a più di un event type. Per esempio, ``wx.EVT_MOUSE_EVENTS`` è un binder collettivo che raggruppa tutti gli event type del mouse (clic, clic a destra, doppio clic, movimento, rotella...)::

    >>> wx.EVT_MOUSE_EVENTS.evtType
    [10025, 10026, 10027, 10028, 10029, 10030, 10031, 10034, 10035, 
     10036, 10032, 10033, 10040]

Inoltre, come vedremo presto, il binder ha anche un metodo ``Bind``, che è il motore che lega insieme eventi, handler e callback. 

Ma prima, ancora un pizzico di confusione, questa volta però comprensibile e sana. Proprio perché nella vita di tutti i giorni non incontrare oggetti-eventi, nel linguaggio comune di wxPython è consueto riferirsi ai ``wx.EVT_*`` come "eventi", anche se sono più precisamente degli oggetti-binder. Tuttavia questa piccola licenza descrive la situazine più accuratamente, in un certo senso. Per esempio, quando premete un pulsante, questo innesca un generico ``wx.CommandEvent`` (che, per dire, è la stessa cosa che si innesca anche quando selezionate un menu). D'altra parte, il binder ``wx.EVT_BUTTON`` porta in sé non solo la nozione del ``wx.CommandEvent``, ma anche quella di "generato da un ``wx.Button``" (ed è molto differente dal binder ``wx.EVT_MENU``). 

.. note:: Perché c'è bisogno dei binder (e degli event type)? Non basterebbero gli eventi da soli? In realtà la presenza degli event type permette di mantenere ridotto il numero delle classi-evento, lasciando che la loro gerarchia si sviluppi secondo le logiche proprie degli eventi, e senza star dietro alla proliferazione dei widget, sempre in corso. 

Detto questo, finalmente siamo pronti per rispondere a tutte le domande!

.. index::
   single: eventi; Bind()
   single: wx.EvtHandler; Bind()
   single: wx.PyEventBinder; Bind()

``Bind``: collegare eventi e callback, in pratica.
--------------------------------------------------

E veniamo al dunque. Come faccio a collegare un evento a un callback? 

Ricapitoliamo: quando faccio clic su un pulsante, viene creato un oggetto-evento. La prima cosa che devo fare è scegliere un handler per quell'evento: siccome però tutti i widget in wxPython sono degli handler, in genere succede che si sceglie il pulsante stesso come handler degli eventi che genera. Ovviamente un pulsante può generare diversi eventi; e d'altra parte, un evento può essere generato da diversi widget oltre al pulsante. Per fortuna abbiamo anche a disposizione un binder specifico, che identifica l'oggetto-evento che ci interessa *in quanto emesso* da un pulsante. 

Tutto ciò che dobbiamo fare è chiamare il metodo ``Bind`` dell'handler che scegliamo (ossia, come abbiamo detto, il pulsante stesso), e usarlo per connettere il binder e il nostro callback::

    button = wx.Button(...)
    button.Bind(wx.EVT_BUTTON, callback)
    
``wx.EVT_BUTTON``, ormai lo sappiamo, è il binder che identifica il particolare evento che si genera quando un pulsante è premuto. ``callback`` è il nostro callback (di solito è un metodo della stessa classe in cui vivono le due righe di codice che abbiamo appena scritto, per cui lo scrivete in genere nella forma ``self.callback``). ``button`` è il nostro pulsante, del quale però stiamo qui utilizzando le sue capacità di handler. ``Bind`` è il metodo implementato da ``wx.EvtHandler`` (e pertanto ereditato anche da ``button``) che compie la magia del collegamento. 

.. note:: a prima vista sembra contradditorio. Non avevamo detto che erano i binder a collegare eventi, handler e callback? E non abbiamo visto che i binder hanno anche loro un metodo ``Bind``? E allora perché stiamo usanto ``wx.EvtHandler.Bind`` per fare il collegamento? In realtà ``wx.EvtHandler.Bind`` chiama semplicemnte ``wx.PyEventBinder.Bind``, quindi in definitiva sì, sono i binder a fare il collegamento dietro le quinte. Qui occorre una precisazione di carattere storico. I binder non solo hanno un loro ``Bind``, ma implementano anche un metodo ``__call__`` che consente di chiamarli come una funzione, e che internamente chiama ``Bind``. Nelle vecchie versioni di wxPython, il collegamento era fatto in questo modo:

    ::

        wx.EVT_BUTTON(button.GetId(), callback)
    
    che era equivalente a:

    :: 

        wx.EVT_BUTTON.Bind(button.GetId(), callback)
    
    e si vedeva chiaramente che era proprio il binder a lavorare. Tuttavia, questo sistema appariva poco "object-oriented", perché sembrava di chiamare direttamente un oggetto, e per di più un oggetto che sembra una costante. In effetti però ``wx.PyEventBinder.__call__`` è ancora lì per retrocompatibilità, e potete ancora vedere questo stile di collegamento nel codice più vecchio (e questa è anche la ragione di questa nota un po' pedante). 

.. index::
   single: eventi; Bind()
   
Altri modi di usare ``Bind``.
-----------------------------

Abbiamo visto che::

    button = wx.Button(...)
    button.Bind(wx.EVT_BUTTON, callback)
    
è il modo consueto di usare ``Bind``, e presuppone di aver scelto il widget stesso come handler dell'evento che si origina da esso. 

Si può anche scegliere un altro handler, però. Per esempio, se il pulsante sta dentro un panel, o un frame, potete scegliere il suo contenitore come handler, e scrivere::

    button = wx.Button(self, ...) # 'self' e' un frame, dialog, panel...
    self.Bind(wx.EVT_BUTTON, callback, button)

Notate che adesso ``Bind`` è stato chiamato passando ``button`` come terzo argomento. E' come dare questo ordine: handler ``self``, devi collegare a ``callback`` tutti i ``wx.EVT_BUTTON`` che provengono da ``button``. 

Il terzo argomento è opzionale. Se però avessimo scritto soltanto::

    self.Bind(wx.EVT_BUTTON, callback) 

questo avrebbe voluto dire: handler ``self``, devi collegare a ``callback`` tutti i ``wx.EVT_BUTTON`` che provengono *da qualsiasi tuo "figlio"*. E naturalmente questa è una cosa utile talvolta, pericolosa di solito.

Che differenza c'è tra ``button.Bind(...)`` e ``self.Bind(..., button)``? Talvolta possono esserci differenze sottili, come vedremo :ref:`nella seconda parte <eventi_avanzati>` quando parleremo della propagazione degli eventi. Nella maggior parte dei casi, però non c'è alcuna differenza pratica. 

Ancora una domanda: abbiamo visto che è possibile collegare a un evento anche l'handler di un altro widget "genitore" (o "progenitore" nella catena dei parent) del widget che lo ha emesso. E' possibile invece collegare l'evento all'handler di un widget "figlio", o all'handler di un widget che non ha niente a che vedere con chi ha emesso l'evento (per esempio, vive in un'altra finestra)? La risposta è no, perché l'evento non si propagherà mai in quella direzione. E' un'altra cosa che vedremo meglio parlando :ref:`di propagazione degli eventi <eventi_avanzati>`.


Sapere quali eventi possono originarsi da un widget.
----------------------------------------------------

Ecco una domanda comune. Come faccio a sapere quali eventi (nel senso di binder ``wx.EVT_*``) possono originarsi da un certo widget? L'unica risposta è :ref:`leggere la documentazione disponibile <documentarsi>`. Anche l'utility EventsInStyle può essere molto utile. 

In generale, un widget può originare alcuni eventi "caratteristici" suoi propri. Spesso questi iniziano con un prefisso comune, per esempio gli eventi tipici di un ``wx.ListCtrl`` iniziano con ``wx.EVT_LC_*``, e quelli di un ``wx.ComboBox`` con ``wx.EVT_CB_*``, etc. Questi sono quelli che trovate nella documentazione del widget. 

Tuttavia, ci sono molti altri eventi di livello più basso che il widget può generare, come quelli del mouse o della tastiera. 

Ispezionare i diversi binder non aiuta, perché un binder è indifferente alla riuscita del matrimonio che è chiamato a celebrare: potete tranquillamente accoppiare un ``wx.EVT_BUTTON`` a una casella di testo, per dire. Semplicemente, l'evento non si verificherà mai. 

Un'altra strada è quella di esaminare la documentazione per le varie classi-evento (ossia quelle derivate da ``wx.Event``). Si possono elencare facilmente::

    >>> import wx
    >>> [i for i in dir(wx) if 'Event' in i]
    
Nella documentazione di ciascuna, ci sono i nomi dei vari binder che possono riferirsi a quell'evento. 

In definitiva, è facile trovare subito gli eventi più comuni per un certo widget, ma occorre un po' di esperienza per scoprire gli altri. 

Infine, :ref:`ho scritto una ricetta apposta <catturaeventi>` per cercare di risolvere questo problema: provatela, potrebbe tornarvi utile. 

.. index::
   single: eventi; metodi e proprietà
   
Estrarre informazioni su un evento nel callback.
------------------------------------------------

Come abbiamo visto, i callback devono accettare come argomento un riferimento all'evento che li ha invocati:
 
    def callback(self, event):
        # etc etc
        
L'argomento ``event`` non è altro che l'istanza dell'oggetto-evento che si è originata dal widget, è stata processata, e adesso raggiunge finalmente il callback. 

Questo oggetto può portare con sé molte informazioni utili: quali esattamente, dipende dall'evento. Consultate la documentazione relativa a ciascuna sottoclasse di ``wx.Event`` per sapere che cosa potete recuperare. 

Per esempio, un ``wx.ListCtrl`` emette vari tipi di eventi della classe ``wx.ListEvent``. Sfogliando la documentazione, trovate per esempio il metodo ``wx.ListEvent.GetColumn``, che vi dice, tra l'altro, la colonna che è stata cliccata. Di conseguenza, nel vostro callback potete recuperarla scrivendo::

    def callback(self, event):
        clicked_column = event.GetColumn()
        
La stessa classe-madre astratta ``wx.Event`` ha dei metodi utili, che tutte le altre classi-evento ereditano. Per esempio, ``GetEventObject()`` vi restituisce un riferimento al widget che ha emesso l'evento. ``GetEventType()`` vi dice l'event type esatto. 

Non è detto che un oggetto-evento contenga informazioni utili per ciascun metodo previsto dalla sua classe, naturalmente. Per esempio, ``wx.CommandEvent.IsChecked()`` è significativo quando il ``wx.CommandEvent`` è stato emesso da una checkbox (o da una voce di menu che si può "flaggare"). Naturalmente, se il ``wx.CommandEvent`` proviene da un pulsante, questo metodo non conterrà niente di utile.

Infine, se non siete sicuri di quale evento sta arrivando al callback, probabilmente siete ancora in fase di sviluppo. Quindi, un bel ``print event`` (o un più raffinato ``print event.__class__.__name__``, se preferite) basteranno a togliervi ogni dubbio.


Un esempio conclusivo.
----------------------

Queste note non sono un tutorial su wxPython e suppongono che siate in grado di documentarvi da soli, vedere esempi di codice in giro, etc. Tuttavia, in conclusione di questa lunga cavalcata sugli eventi, ecco un esempio minimo per far vedere come si fa di solito. Molti altri esempi, naturalmente, si trovano :ref:`nella demo e nella documentazione <documentarsi>`. 

:: 

    class TopFrame(wx.Dialog):
        def __init__(self, *a, **k):
            wx.Dialog.__init__(self, *a, **k)
            button1 = wx.Button(self, -1, 'pulsante 1', pos=(10, 10), name='button 1')
            button2 = wx.Button(self, -1, 'pulsante 2', pos=(10, 50), name='button 2')
            button1.Bind(wx.EVT_BUTTON, self.on_button1)
            button2.Bind(wx.EVT_BUTTON, self.on_button2)
            
        def on_button1(self, evt):
            print 'evento', evt.__class__.__name__
            print 'oggetto', evt.GetEventObject().GetName()
            
        def on_button2(self, evt):
            print 'evento', evt.__class__.__name__
            print 'oggetto', evt.GetEventObject().GetName()
        
    app = wx.App(False)
    TopFrame(None).Show()
    app.MainLoop()
    
    
