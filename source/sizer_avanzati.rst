.. index:: 
   single: sizer
   
.. _sizer_avanzati:

I sizer: seconda parte.
=======================

Questa pagina riprende il discorso da dove lo avevamo interrotto :ref:`nella pagina introduttiva <sizer_basi>` sui sizer e sul ``wx.BoxSizer`` in particolare. Per avere un quadro completo sui sizer, è utile anche leggere la pagina dedicata :ref:`alle dimensioni dei widget <dimensioni>`. 

.. index:: 
   single: sizer; wx.GridSizer
   single: wx.GridSizer
   
``wx.GridSizer``: una griglia rigida.
-------------------------------------

Se ``wx.BoxSizer`` è una colonna (o una riga) singola, ``wx.GridSizer`` è invece una griglia di celle. Al contrario del ``wx.BoxSizer``, al momento di creare un ``wx.GridSizer`` dovete specificare in anticipo il numero di righe e di colonne. Per esempio::

    sizer = wx.GridSizer(3, 2, 5, 5)
    
avrà 3 righe e 2 colonne. Il terzo e il quarto argomento specificano lo spazio (verticale e orizzontale) da lasciare tra le celle, in pixel. 

Una volta che avete creato il sizer, potete inserire i vari elementi usando ``Add`` come di consueto. Il sizer si riempirà da sinistra a destra e dall'alto in basso. 

Il ``wx.GridSizer`` è una struttura rigida: il widget più grande determina la dimensione di tutte le celle. Se gli altri widget hanno flag ``wx.EXPAND`` e/o priorità superiore a 0, allora occuperanno l'intero spazio della cella. Altrimenti, resteranno più piccoli della cella (con eventuale allineamento se hanno flag ``wx.ALIGN_*``). 

Una considerazione ulteriore sui bordi. Questo sizer permette di specificare uno spazio tra le righe e/o tra le colonne, ma non uno spazio "di cornice". Avete due opzioni per rimediare: la prima è non specificare gli spazi, e inserire ciascun widget con il proprio bordo. La seconda è specificare gli spazi, e poi inserire il sizer completo in un ``wx.BoxSizer`` di una sola cella, con il bordo adeguato. L'esempio che segue illustra questa seconda tecnica. 

Il ``wx.GridSizer`` non è molto usato in pratica. La sua struttura rigida è limitante, e di solito lo rende utile solo quando siete sicuri che tutti i widget abbiano le stesse dimensioni. Il caso da manuale sono i pulsanti di una calcolatrice::

    class TopFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            p = wx.Panel(self)
            sizer = wx.GridSizer(4, 4, 2, 2)  
            for lab in '789/456*123-0.=+':
                b = wx.Button(p, -1, lab, size=(30, 30), name=lab)
                b.Bind(wx.EVT_BUTTON, self.on_clic)
                sizer.Add(b, 1, wx.EXPAND)
            boxsizer = wx.BoxSizer()
            boxsizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 5) # un bordo di cornice
            p.SetSizer(boxsizer)
            sizer.Fit(self)
        
        def on_clic(self, evt): print evt.GetEventObject().GetName(), 

    if __name__ == '__main__':
        app = wx.App(False)
        TopFrame(None).Show()
        app.MainLoop()


.. index:: 
   single: sizer; wx.FlexGridSizer
   single: wx.FlexGridSizer
   
   
``wx.FlexGridSizer``: una griglia elastica.
-------------------------------------------

``wx.FlexGridSizer`` è una versione più flessibile di ``wx.GridSizer``, ed è quella che si utilizza più spesso. E' possibile infatti definire una o più righe (e/o colonne) che possono espandersi occupando lo spazio ancora disponibile dopo che tutte quelle "normali" avranno occupato lo spazio minimo richiesto (basandosi sul widget più grande che devono contenere, come per il ``wx.GridSizer``). 

Le righe/colonne "flessibili" si contendono lo spazio disponibile in base alla stessa regola delle priorità che abbiamo visto per il ``wx.BoxSizer``. Quindi, per esempio::

    sizer = wx.FlexGridSizer(5, 5, 2, 2) # una griglia 5 x 5
    sizer.AddGrowableCol(0, 1)
    sizer.AddGrowableCol(1, 2)
    sizer.AddGrowableRow(4) # e' sottinteso sizer.AddGrowableRow(4, 1)
    
vuol dire che la prima e la seconda colonna si spartiranno 1/3 e 2/3 dello spazio orizzontale disponibile, mentre la quinta riga occuperà tutto lo spazio extra verticale. 

Il ``FlexGridSizer`` è lo strumento più usato in tutte le situazioni in cui occorre creare una griglia dove, per esempio, una colonna ha maggiore importanza. Il caso tipico è l'entry-form::

    class TopFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            p = wx.Panel(self)
            sizer = wx.FlexGridSizer(4, 2, 5, 5)  
            sizer.AddGrowableCol(1)
            for lab in ('nome', 'cognome', 'indirizzo', 'telefono'):
                sizer.Add(wx.StaticText(p, -1, lab), 0, wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(wx.TextCtrl(p, -1, name=lab), 0, wx.EXPAND)
            boxsizer = wx.BoxSizer()
            boxsizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 5) # un bordo di cornice
            p.SetSizer(boxsizer)

    if __name__ == '__main__':
        app = wx.App(False)
        TopFrame(None).Show()
        app.MainLoop()


.. index:: 
   single: sizer; wx.GridBagSizer
   single: wx.GridBagSizer
   
   
``wx.GridBagSizer``: una griglia ancora più flessibile.
-------------------------------------------------------

Un ``wx.GridBagSizer`` è come un ``wx.FlexGridSizer``, con due proprietà aggiuntive:

* è possibile specificare una cella precisa in cui inserire il widget;

* è possibile fare in modo che un widget si estenda in più celle adiacenti (come si comportano le tabelle HTML).

La prima proprietà può essere comoda in certi casi, ma se usate un ``wx.GridBagSizer`` solo per crearlo e riempirlo una volta per sempre, allora è più ordinato utilizzare un semplice `wx.(Flex)GridSizer``. La seconda, d'altra parte, può essere interessante. 

Entrambe le proprietà sono ottenute modificando il metodo ``Add``, che ora vuole due argomenti nuovi. Il primo (obbligatorio!) è ``pos``, una tupla per specificare la posizione di inserimento. Il secondo (facoltativo) è ``span``, per specificare per quante righe (o colonne) adiacenti occorre estendere il widget, a partire dalla cella di inserimento.

Per esempio::

    sizer.Add(widget, pos=(0, 0), span=(3, 2))
    
vuol dire che il widget, a partire dalla prima cella in alto a sinistra, si espande per tre righe e due colonne. 

In compenso, ``Add`` perde l'argomento ``proportion``, per cui dovete risolvere tutto con ``AddGrowableCol/Row`` e specificando lo ``span``.

Usare i ``wx.GridBagSizer`` può essere comodo da un lato, fonte di confusione dall'altro. Ovviamente tutto ciò che potete fare con un ``wx.GridBagSizer`` potete farlo anche con la composizione di sizer più semplici. In generale, quando il layout che avete in mente assomiglia a una griglia con forti irregolarità, potete prendere in considerazione il ``wx.GridBagSizer``. Questo, comunque, è il genere di layout che dovete disegnare prima su un foglio di carta, per non confondervi troppo. 


.. index:: 
   single: sizer; wx.StaticBoxSizer
   single: wx.StaticBoxSizer
   
   
``wx.StaticBoxSizer``: un sizer per raggruppamenti logici.
----------------------------------------------------------

Lasciamo per ultimo il ``wx.StaticBoxSizer``, che è semplicemente un``wx.BoxSizer`` applicato a uno ``wx.StaticBox``. 

L'aspetto grafico è quello di un consueto ``wx.StaticBox``, ossia una linea rettangolare che circonda gli elementi inclusi, con una label in alto. 

Lo ``wx.StaticBoxSizer`` va usato solo in accoppiata con il suo ``wx.StaticBox``, che va creato per primo. Infatti il costruttore dello ``wx.StaticBoxSizer`` richiede un argomento in più rispetto al normale ``wx.BoxSizer``, ossia appunto un riferimento allo ``wx.StaticBox``::

    box = wx.StaticBox(parent, -1, 'opzioni')
    sbs = wx.StaticBoxSizer(box, wx.VERTICAL)
    
Per il resto, l'uso di questo sizer è normalissimo::

    class TopFrame(wx.Frame): 
        def __init__(self, *a, **k): 
            wx.Frame.__init__(self, *a, **k) 
            p = wx.Panel(self)
            
            box = wx.StaticBox(p, -1, 'opzioni')
            sizer = wx.StaticBoxSizer(box, wx.VERTICAL)  
            for i in range(3):
                sizer.Add(wx.Button(p), 1, wx.EXPAND|wx.ALL, 5)
            p.SetSizer(sizer)


.. index:: 
   single: sizer; wx.StdDialogButtonSizer
   single: sizer; wx.Window.CreateButtonSizer
   single: wx.StdDialogButtonSizer
   single: wx.Window; CreateButtonSizer
   single: stock buttons
   
.. _createbuttonsizer:

``StdDialogButtonSizer`` e ``CreateButtonSizer``: sizer per pulsanti generici.
------------------------------------------------------------------------------

:ref:`Abbiamo già incontrato <stockbuttons>` il concetto di pulsanti con Id predefiniti, da usare tipicamente nei dialoghi. Per maggiore comodità, è possibile inserirli automaticamente in un sizer orizzontale chiamato ``StdDialogButtonSizer``. 

Il metodo ``CreateButtonSizer``, chiamato su un dialogo, restituisce automaticamente un ``StdDialogButtonSizer`` già completo e pronto da inserire nel resto del layout. 

Per esempio, questo::

    btn_sizer = self.CreateButtonSizer(wx.OK|wx.CANCEL) # 'self' e' un dialogo
    main_sizer.Add(btn_sizer, ...)
    
restituisce un sizer completo di due pulsanti con Id predefiniti ("ok" e "cancella"). 

Gli Id predefiniti che è possibile utilizzare sono ``wx.ID_OK``, ``wx.ID_CANCEL``, ``wx.ID_YES``, ``wx.ID_NO``, ``wx.ID_HELP``. 


.. index:: 
   single: sizer; wx.WrapSizer
   single: wx.WrapSizer

``wx.WrapSizer``: un ``BoxSizer`` che sa quando "andare a capo".
----------------------------------------------------------------

Concludiamo con quello che è probabilmente il più sconosciuto e meno documentato dei sizer di wxPython. ``wx.WrapSizer`` si comporta in modo quasi identico a ``wx.BoxSizer``, ma quando raggiunge il bordo del contenitore a cui è assegnato (per esempio, il bordo di una finestra) "va a capo" aggiungendo un'altra riga o un'altra colonna, a seconda dell'orientamento. 

Provate questo semplice esempio, per capire come si comporta::

    class TopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            s = wx.WrapSizer(wx.VERTICAL, 2)
            for i in range(10):
                s.Add(wx.Button(p, -1, str(i)), 0, wx.ALL, 5)
            # s.Add((50, 50))
            for i in range(10, 20):
                s.Add(wx.Button(p, -1, str(i)), 0, wx.ALL, 5)
            p.SetSizer(s)

Se provate a cambiare le dimensioni della finestra, vedrete che i pulsanti si distribuiscono su una o più colonne, a seconda dello spazio che hanno. E' facile immaginare che un ``wx.WrapSizer`` potrebbe tornare comodo, per esempio, per visualizzare un elenco di piccole immagini (thumbnail) o in situazioni analoghe. 

``wx.WrapSizer`` ha poi alcune particolarità che meritano di essere ricordate. Purtroppo bisogna dire che wxPython non implementa in modo completo questo sizer: di conseguenza, alcune delle proprietà che si possono leggere nella documentazione di wxWidgets in realtà non funzionano in wxPython; può darsi che in futuro saranno implementate, ma in ogni caso conviene sempre sperimentare direttamente. 

La prima cosa che salta all'occhio, è che ``wx.WrapSizer`` si può istanziare con due argomenti: il primo è il consueto flag di orientamento (come per ``wx.BoxSizer``, può essere orizzontale o verticale). Il secondo è una serie di flag di stile che possono essere:

- nessun flag settato (valore ``1``);
- flag ``EXTEND_LAST_ON_EACH_LINE`` (valore ``0``);
- flag ``REMOVE_LEADING_SPACES`` (valore ``3``);
- ``WRAPSIZER_DEFAULT_FLAGS`` (entrambi i flag settati, valore ``2``).

Purtroppo però wxPython non esporta queste costanti (per esempio, non esiste ``wx.EXTEND_LAST_ON_EACH_LINE``, come è facile controllare). Di conseguenza, occorre usare direttamente il loro valore numerico, come abbiamo fatto nell'esempio qui sopra. La documentazione di wxWidgets sostiene che il comportamento di default è di avere entrambi i flag settati: in wxPython tuttavia sembra che il valore di default sia al contrario di non avere nessun flag settato, e inoltre i valori numerici delle costanti sembrano differire tra wxPython e wxWidgets (qui sopra abbiamo indicato quelli di wxPython, naturalmente). Quindi conviene sempre dichiarare esplicitamente quali flag si desiderano attivi (di solito è più utile settare il secondo, o entrambi: potete comunque sperimentare le alternative).

``REMOVE_LEADING_SPACES`` serve se introducete degli spazi vuoti nel vostro sizer: in questo caso, il flag impedisce che lo spazio vuoto finisca all'inizio di una riga o di una colonna. Nell'esempio qui sopra, de-commentate la riga ``s.Add((50, 50))`` per introdurre uno spazio a metà dei pulsanti: potrete verificare che effettivamente lo spazio non finirà mai in una posizione anti-estetica. Di solito, quindi, è utile mantenere settato questo flag.

``EXTEND_LAST_ON_EACH_LINE`` serve a estendere l'ultima riga o colonna, fino a occupare tutto lo spazio disponibile. E' un comportamento che talvolta è desiderabile, talvolta no: vi conviene sperimentare, e verificare se fa al caso vostro caso per caso. 

Infine occorre segnalare che la documentazione di wxWidget menziona anche un metodo ``wxWrapSizer::IsSpaceItem``, che si può sovrascrivere per dire al sizer di considerare anche altri elementi specifici come se fossero degli spazi, ai fini del calcolo invocato dal flag ``REMOVE_LEADING_SPACES``. In wxPython però questo metodo non è presente, e quindi dobbiamo accontentarci del comportamento di default, che, come abbiamo visto, considera "spazi" in un sizer solo gli elementi del tipo "Spacer" (ovvero quelli inseriti con ``wx.Sizer.AddSpacer`` o ``wx.Sizer.AddStretchSpacer``).

Esempi di utilizzo dei sizer.
-----------------------------

Nella :ref:`documentazione <documentarsi>` trovate vari esempi di layout realizzati con i sizer. In particolare, potete cercare "sizer" nella demo. Inoltre, il capitolo 11 del libro "wxPython in action" è dedicato ai sizer, per cui tutti gli esempi della documentazione tratti da quel capitolo sono interessanti. In particolare, ``realworld.py`` mostra un tipico esempio di come i sizer possono essere usati nel "mondo reale". 


.. index:: 
   single: sizer; wx.SizerItem
   single: wx.SizerItem
   single: wx.Sizer; Add
   single: sizer; wx.Sizer.Add
   single: wx.Window; SendSizeEvent
   single: sizer; wx.Window.SendSizeEvent

.. _sizeritem:

``wx.SizerItem``, e modificare il layout a runtime.
---------------------------------------------------

Riprendiamo qui il discorso su ``wx.Sizer.Add`` che avevamo lasciato in sospeso nella :ref:`precedente pagina<sizer_basi>` sui sizer. Finora infatti non abbiamo mai menzionato il fatto che ``wx.Sizer.Add``, oltre ad aggiungere un widget (o uno spazio) a un sizer, restituisce anche un valore di ritorno che occasionalmente può tornarci utile. 

``wx.Sizer.Add`` restituisce una istanza della classe ``wx.SizerItem`` che, come il nome suggerisce, incapsula il concetto di "widget inserito in un sizer". In genere non abbiamo bisogno di questo valore di ritorno, ma volendo possiamo conservarlo assegnandolo a una variabile: qualcosa come::

    s = wx.BoxSizer()
    # in genere ci basta aggiungere i widget al sizer così:
    s.Add(widget, 1, wx.EXPAND|wx.ALL, 5)
    # ma talvolta è utile conservare il wx.SizerItem corrispondente:
    self.sizer_item = s.Add(widget, 1, wx.EXPAND|wx.ALL, 5)
    # etc. etc.

Un oggetto ``wx.SizerItem`` ha alcuni metodi che possono tornarci utili per manipolare il layout dopo che è stato disegnato la prima volta: per esempio, 

- ``SetDimension`` assegna posizione e dimensione del widget all'interno del sizer;
- ``SetBorder`` stabilisce il bordo da attribuire al widget;
- ``SetFlag`` attribuisce i flag del widget;
- ``SetProportion`` ridefinisce la dimensione relativa del widget in confronto agli altri.

Ecco un esempio che mostra qualche variazione di layout "al volo"::

    class Test(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b1 = wx.Button(p, -1, '1')
            b2 = wx.Button(p, -1, '2')
            b3 = wx.Button(p, -1, '3')
            b1.Bind(wx.EVT_BUTTON, self.on_clic_b1)
            b2.Bind(wx.EVT_BUTTON, self.on_clic_b2)
            b3.Bind(wx.EVT_BUTTON, self.on_clic_b3)
            s = wx.BoxSizer(wx.VERTICAL)
            self.sizer_item_b1 = s.Add(b1, 1, wx.EXPAND|wx.ALL, 5)
            self.sizer_item_b2 = s.Add(b2, 1, wx.EXPAND|wx.ALL, 5)
            self.sizer_item_b3 = s.Add(b3, 1, wx.EXPAND|wx.ALL, 5)
            p.SetSizer(s)
            self.p = p

        def on_clic_b1(self, evt):
            self.sizer_item_b1.SetProportion(0)
            self.p.SendSizeEvent()

        def on_clic_b2(self, evt):
            self.sizer_item_b2.SetFlag(0)
            self.p.SendSizeEvent()

        def on_clic_b3(self, evt):
            self.sizer_item_b3.SetFlag(wx.EXPAND|wx.LEFT|wx.RIGHT)
            self.sizer_item_b3.SetBorder(25)
            self.p.SendSizeEvent()

Si noti l'uso di ``wx.Window.SendSizeEvent`` per invocare il ridisegno del layout anche quando la finestra non ha effettivamente cambiato dimensioni. 

In pratica, tuttavia, queste tecniche di manipolazione del layout non sono consigliabili. E' buona norma non modificare l'interfaccia in modo vistoso dopo averla mostrata la prima volta: l'utente ha bisogno di ambientarsi e ricordare la posizione dei widget, farsi una mappa mentale degli aspetti più importanti della vostra gui e dei pattern di utilizzo per lui più consueti. Se voi alterate profondamente il layout a runtime, aggiungendo e togliendo, spostando e modificando i widget, l'utente ne ricaverà solo un senso di disordine e irritazione. Spesso i programmatori inesperti pensano che sia utile, per esempio, far sparire i widget non necessari (o inattivi) in quel momento, e farli riapparire solo quando servono: ma in realtà ci sono sempre modi migliori per organizzare il layout, e wxPython non è certo carente di soluzioni intelligenti (per esempio, si possono organizzare i widget in "pagine" usando un ``wx.Notebook`` o altri analoghi contenitori a schede).
