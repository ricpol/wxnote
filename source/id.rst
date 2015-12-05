.. _gli_id:

.. highlight:: python
   :linenothreshold: 12

.. index::
   single: id in wxPython
   
Gli Id in wxPython.
===================

In wxPython, ogni widget che create ha un numero (Id) che lo identifica univocamente. E' una eredità del framework C++ sottostante, e nel mondo Python questo uso pervasivo di id globali sembra goffo, per non dire altro. Ma non dovete scordare che in C++ certe comodità di Python non ci sono. Per esempio, in Python voi potete passare il nome di una funzione come argomento di un'altra funzione, perché le funzioni sono "first class object". Quindi in wxPython è normale scrivere cose come::

    button.Bind(wx.EVT_BUTTON, self.on_clic)
    
dove appunto ``on_clic`` viene passata come argomento di ``Bind``. Ma in C++ questo proprio non si può fare, e quindi anche una cosa banale come collegare tra loro un oggetto, un evento e un callback diventa un complicato balletto eseguito da una macro che può lavorare solo con riferimenti statici: e il riferimento agli oggetti è appunto il loro Id univoco. 

Quindi gli Id ci sono, e ci saranno sempre. wxPython potrebbe decidere di nasconderli completamente (e in effetti ci sono piani per questo, in qualche punto nel futuro), ma per il momento invece li espone ancora. 

In questa pagina diamo uno sguardo alle cose fondamentali da sapere sugli Id, e poi vedremo qualche raro caso in cui possono ancora tornare comodi. 

.. index::
   single: wx.ID_ANY
   single: wx.NewId
   single: wx.ID_LOWEST
   single: wx.ID_HIGHEST
   single: id in wxPython; wx.ID_ANY
   single: id in wxPython; wx.NewId
   single: id in wxPython; wx.ID_LOWEST
   single: id in wxPython; wx.ID_HIGHEST

Assegnare gli Id.
-----------------

L'Id viene attribuito obbligatoriamente a tutti i widget al momento della loro creazione. In genere, è il secondo argomento che dovete passare al costruttore (il primo è il "parent", :ref:`come vediamo altrove <catenaparent>`). 

Potete scegliere:

* l'opzione più comune è lasciare che wxPython assegni automaticamente l'Id, senza preoccuparvi di sapere qual è. In questo caso, basta passare la costante ``wx.ID_ANY`` (o, più rapidamente, il valore ``-1``) al costruttore::

    button = wx.Button(self, -1, 'hello')
    
* se invece volete conoscere e conservare il valore dell'Id, lasciando comunque che sia wxPython a deciderlo, potete generare un nuovo Id con la funzione globale ``wx.NewId()``::

    button_id = wx.NewId()
    button = wx.Button(self, button_id, 'hello')
    
* infine, potete assegnare voi stessi manualmente un numero::

    button = wx.Button(self, 100, 'hello')
    
In quest'ultimo caso, però, dovete stare attenti a molte cose. Primo, wxPython conserva internamente molti Id già pre-assegnati, e dovete stare attenti a non sovrascriverli. Potete usare tutti i numeri che volete, purché non siano compresi tra ``wx.ID_LOWEST`` e ``wx.ID_HIGHEST`` (vi lascio il piacere di scoprire quali sono). 

Secondo, se impostate a mano certi Id, e lasciate a wxPython il compito settarne degli altri, dovete fare attenzione che wxPython non sovrascriva i vostri (o viceversa). La cosa più sicura è determinare tutti gli Id che vi servono *prima* che wxPython assegni il suo primo Id, e registrarli con la funzione ``wx.RegisterId``. In questo modo dite a wxPython di lasciar stare quei numeri. Per esempio, per riservare per il vostro uso cento numeri, potete fare::

    # questo prima di ogni altra cosa
    for x in range(100, 201):
        wx.RegisterId(x)
    # in futuro, posso usare gli Id dal 100 al 200
        
Tuttavia, questo è uno scrupolo inutile nella maggior parte dei casi. In genere wxPython assegna Id *negativi* progressivi (a partire da -200, ma può essere variabile). Vi basta assegnare numeri positivi, e siete a posto. 

Terzo, tenete conto che, tecnicamente, gli Id dovrebbero essere univoci *nello stesso frame*, ma tra diversi frame è permesso duplicarli. Ovviamente il consiglio è cercare comunque di mantenere Id univoci in tutta l'applicazione. Confesso di non aver mai controllato come si comporta wxPython con gli Id che genera lui: se ricomincia la numerazione a ogni nuovo frame, se si sente libero di riciclare gli Id quando voi distruggete un frame, e così via. 

.. index::
   single: wx.Window; GetId
   single: wx.Window; SetId
   single: wx.FindWindowById
   single: id in wxPython; wx.Window.GetId
   single: id in wxPython; wx.Window.SetId
   single: id in wxPython; wx.FindWindowById

Lavorare con gli Id.
--------------------

Una volta che il widget è stato creato, e quindi ha ricevuto il suo Id, ci sono pochi idiomi tipici che dovete conoscere. 

* per sapere l'Id di un widget, usate ``GetId()``

* per ri-assegnare un Id, potete usare ``SetId()`` (ma non dovreste mai averne bisogno)

* la funzione globlale ``wx.FindWindowById()`` restituisce un widget se conoscete il suo Id (o ``None`` se non trova niente). Siccome gli Id possono essere ripetuti tra i diversi frame, potete anche passare il riferimento al frame dentro cui volete cercare (per esempio, ``wx.FindWindowById(100, my_button)`` cerca solo all'interno del frame dove vive ``my_button``). Se non passate niente, la ricerca sarà globale, ma si arresta appena trova il primo widget con l'Id corrispondente (e non è detto che ce ne siano altri, o che questo sia proprio quello che vi serve). Se pensate che questo algoritmo sia un po' bacato, avete trovato un'altra buona ragione per non usare gli Id. 
                                           
Lo abbiamo già notato: cose come ``wx.FindWindowById()`` possono far sorridere il programmatore Python, che è abituato a passare in giro riferimenti alle istanze dei vari oggetti, come se fossero delle costanti qualunque. Ma ricordate che in C++ vi trovate a passare cose statiche (gli Id, appunto), e allora una funzione di ricerca può tornare utile. 


Quando gli Id possono tornare utili.
------------------------------------

Anche in wxPython, ci sono occasioni in cui lavorare direttamente con gli Id è comodo, o addirittura ancora necessario. Vediamo alcuni casi tipici. 


.. _stockbuttons:

.. index::
   single: stock buttons
   single: id in wxPython; stock buttons

StockButtons.
^^^^^^^^^^^^^

Voi potete scegliere di non usare gli Id, ma wxWidgets li usa eccome. Ci sono molti Id predefiniti per compiti particolari. Un caso tipico sono gli "StockButtons" (cercate nella demo). In pratica, se create un ``wx.Button`` passandogli come Id uno di quelli predefiniti del tipo ``wx.ID_*``, wxPython aggiungerà la label corrispondente (e userà lo StockButton nativo sulle piattaforme che supportano questo concetto). Per esempio::

    copy = wx.Button(parent, wx.ID_COPY)
    
produrrà un pulsante "copia", e così via. 

L'utilizzo di questo tipo di pulsanti può essere reso ancora più semplice dall'impiego di :ref:`un sizer generato automaticamente <createbuttonsizer>`.


.. index::
   single: wx.MessageDialog
   single: wx.ID_YES
   single: wx.ID_NO
   single: wx.Dialog
   single: dialogo; con risposte predefinite
   single: dialogo; wx.Dialog
   single: dialogo; wx.MessageDialog
   single: id in wxPython; wx.ID_YES
   single: id in wxPython; wx.ID_NO
   single: id in wxPython; dialogo con risposte predefinite

   
Dialoghi con risposte predefinite.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Un utilizzo simile degli Id predefiniti avviene nei dialoghi. Ci sono molti dialoghi "standard" che non avete bisogno di disegnare nel dettaglio; potete però impostarli perché abbiano certi pulsanti predefiniti. A seconda dei pulsanti che inserite, il dialogo restituisce alla chiusura l'Id (predefinito) del pulsante premuto, come risultato del metodo ``Show`` o ``ShowModal``: questo vi consente di conoscere la decisione dell'utente, e regolarvi di conseguenza. Per esempio::

    msg = wx.MessageDialog(None, -1, 'Vuoi il gelato?', 'Decisioni...',
                           # questo determina 3 pulsanti: si', no, annulla:
                           style = wx.YES|wx.NO|wx.CANCEL) 
    retcode = msg.ShowModal()
    if retcode == wx.ID_YES:   # ha premuto si'
        ...
    elif retcode == wx.ID_NO:  # ha premuto no
        ...
    else:                      # ha premuto annulla (sarebbe wx.ID_CANCEL)
        ...
    msg.Destroy() # dopo aver usato il dialogo, sempre ricordarsi...
    
Ovviamente l'uso di questi dialoghi (oltre a ``wx.MessageBox`` ne esistono altri simili: cercate "Dialog" nella demo per avere un'idea) è possibile solo grazie all'uso dei vari Id predefiniti. Ci sono ``wx.ID_OK``, ``wx.ID_CANCEL``, ``wx.ID_ABORT``, ``wx.ID_YES``, ``wx.ID_NO`` e altri ancora, che corrispondono alle scelte ``wx.OK``, ``wx.CANCEL``, ``wx.ABORT``, ``wx.YES``, ``wx.NO`` (e la combinazione ``wx.YES_NO``) del parametro ``style`` del dialogo. 

.. index::
   single: wx.ID_OK
   single: wx.ID_CANCEL
   single: id in wxPython; wx.ID_OK
   single: id in wxPython; wx.ID_CANCEL
   single: wx.Dialog
   single: dialogo; wx.Dialog
   single: dialogo; con pulsanti predefiniti
   single: id in wxPython; dialogo con pulsanti predefiniti

.. _idpredefiniti: 

Dialoghi personalizzati con pulsanti predefiniti.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Chiaramente potete usare questi pulsanti predefiniti (ossia questi Id predefiniti) anche nei dialoghi disegnati da voi. Ecco un esempio::

    class IceCreamDialog(wx.Dialog):
        def __init__(self, *a, **k):
            wx.Dialog.__init__(self, *a, **k)
            self.flavor = wx.ComboBox(self, -1, 'crema', style=wx.CB_READONLY,
                                      choices=['crema', 'cioccolato', 'stracciatella'])
            ok = wx.Button(self, wx.ID_OK, 'dammi subito il mio gelato!')
            cancel = wx.Button(self, wx.ID_CANCEL, 'sono a dieta...')
            
            s = wx.BoxSizer(wx.VERTICAL)
            s.Add(self.flavor, 0, wx.EXPAND|wx.ALL, 15)
            s1 = wx.BoxSizer()
            s1.Add(ok, 1, wx.EXPAND|wx.ALL, 5)
            s1.Add(cancel, 1, wx.EXPAND|wx.ALL, 5)
            s.Add(s1, 0, wx.EXPAND|wx.ALL, 10)
            self.SetSizer(s)
            s.Fit(self)
        
        def GetValue(self): return self.flavor.GetStringSelection()
            
            
    class MyTopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            b = wx.Button(self, -1, 'scelta gelati')
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            
        def on_clic(self, evt):
            msg = IceCreamDialog(self, title='gelati!')
            retcode = msg.ShowModal()
            if retcode == wx.ID_OK:
                print 'gelato gusto %s in arrivo!' % msg.GetValue()
            else:
                print 'abbiamo i sorbetti al limone...'
            
                            
    app = wx.App(False)
    MyTopFrame(None, size=(150, 150)).Show()
    app.MainLoop()

Notate che non abbiamo bisogno di collegare esplicitamente i nostri due pulsanti a qualche evento. Basta assegnare loro i corretti Id "predefiniti" (righe 6 e 7), e wxPython sa già cosa fare: chiude il dialogo e restituisce l'Id del pulsante premuto. 

Ovviamente questo funziona solo per il pulsanti con Id "predefiniti": se aggiungete un pulsante con un Id qualsiasi, per farlo funzionare dovrete collegarlo normalmente a un evento. 

.. index::
   single: wx.Dialog
   single: dialogo; wx.Dialog
   single: dialogo; con validazione automatica
   single: wx.PyValidator
   single: validatore; validazione automatica
   single: validatore; wx.PyValidator
   single: id in wxPython; dialogo con validazione automatica

.. _validazione_automatica:

Validatori.
^^^^^^^^^^^

Ai validatori :ref:`dedichiamo una sezione apposta <validatori>`, ma qui basta un appunto per ricordare un altro vantaggio dell'Id predefinito ``wx.ID_OK``. Se nel vostro dialogo inserite un pulsante con questo Id, oltre ai benefici visti sopra, quando si preme questo pulsante wxPython inserisce anche una validazione automatica del dialogo, prima di chiuderlo. 

Ovviamente dovete impostare qualche validatore che faccia davvero un controllo. Per esempio, aggiungete al codice del paragrafo precedente questo validatore che impedisce di selezionare il gusto "crema"::

    class NoCreamValidator(wx.PyValidator):
        def __init__(self): wx.PyValidator.__init__(self)
        def Clone(self): return NoCreamValidator()
        def TransferToWindow(self): return True
        def TransferFromWindow(self): return True
        
        def Validate(self, win):
            if self.GetWindow().GetStringSelection() == 'crema': 
                wx.MessageBox('Gusto terminato!', 'Oh no!')
                return False
            else: 
                return True

e poi modificate la creazione di ``self.flavor`` aggiungendo il validatore::

    self.flavor = wx.ComboBox(self, -1, 'crema', style=wx.CB_READONLY, 
                              choices=['crema', 'cioccolato', 'stracciatella'], 
                              validator=NoCreamValidator())

Come vedete, adesso quando premete il pulsante contrassegnato con ``wx.ID_OK``, ottenete gratis una validazione del dialogo. 

.. _gli_id_nei_menu:

.. index::
   single: menu; uso degli id
   single: wx.EVT_MENU
   single: wx.EVT_MENU_RANGE
   single: menu; wx.EVT_MENU
   single: menu; wx.EVT_MENU_RANGE
   single: eventi; lambda binding
   single: id in wxPython; uso nei menu
   
Menu.
^^^^^

Lasciamo alla fine il caso di utilizzo più frequente per gli Id: i menu. Abbiamo dedicato :ref:`una pagina separata<menu_basi>` per approfondire l'uso dei menu. Qui ci limitiamo a qualche nota specifica sugli Id.  

Intendiamoci, potete fare del tutto a meno degli Id quando lavorate con i menu. Se create ogni voce separatamente, e collegate ogni voce a un callback separato, le cose procedono senza intoppi::

    menu_item = my_menu.Append(-1, 'crema')
    self.Bind(wx.EVT_MENU, self.crema_selected, menu_item)
    menu_item = my_menu.Append(-1, 'cioccolato')
    self.Bind(wx.EVT_MENU, self.cioccolato_selected, menu_item)
    # etc. etc.
    
Notate l'Id ``-1`` passato a tutte le voci aggiunte. 

Capita spesso però che vogliate collegare più voci di menu a uno stesso callback, perché c'è anche un po' di lavoro in comune da fare, oppure perché si tratta di voci collegate tra loro (del tipo "check" o "radio", per intenderci). Tuttavia, prima o poi nel callback volete capire da quale voce esattamente è partito l'evento. E qui il classico modo ``event.GetEventObject()``, non funziona nel caso di un ``wx.EVT_MENU``: in effetti, ma non fa altro che restituire l'istanza del frame in cui appare il menu. 

Tuttavia l'evento ``wx.EVT_MENU`` trasporta con sé l'Id (e solo quello) della voce che è stata selezionata, per cui se invece chiedete ``event.GetId()`` ottenete un'informazione più precisa... a patto naturalmente di conoscere gli Id delle singole voci di menu. 

Ecco perché spesso si finisce per assegnare esplicitamente gli Id a tutte le voci del menu (a mano, o con ``wx.NewId()``; i più minimalisti assegnano Id solo alle voci che effettivamente verranno raggruppate nei callback). 

Oltretutto, se avete l'accortezza di assegnare Id *consecutivi* alle voci che volete raggruppare in un solo callback, wxPython offre l'opportunità di collegarle tutte insieme usando ``wx.EVT_MENU_RANGE``, che accetta soltanto Id (appunto!) come parametri. Qualcosa del genere::
    
    # al momento di creare il menu:
    menu.Append(100, 'crema')
    menu.Append(101, 'cioccolato') 
    menu.Append(102, 'stracciatella')
    self.Bind(wx.EVT_MENU_RANGE, self.on_menu, id=100, id2=102)
    
    # e poi, nel callback:
    def on_menu(self, evt):
        caller = evt.GetId()
        # etc. etc.

``wx.EVT_MENU_RANGE`` vi evita di collegare le voci una per una allo stesso callback. Naturalmente, un programmatore Python potrebbe semplicemente fare::

    for id, label in enumerate(('crema', 'cioccolato', 'stracciatella')):
        menu.Append(id+100, label)
        self.Bind(wx.EVT_MENU, self.on_menu, id=id)

senza ricorrere a ``wx.EVT_MENU_RANGE``... Ma di nuovo, dovete considerare che avete dalla vostra l'espressività e la compattezza di Python... 

E a proposito di espressività e compattezza, aggiungo che potete evitare del tutto l'uso degli Id con i menu (anche quando intendete collegare più voci allo stesso callback), facendo uso del :ref:`trucco del "lambda binding" <lambda_binding>` per passare a ``Bind`` un parametro in più::

    # al momento di creare il menu:
    for label in ('crema', 'cioccolato', 'stracciatella'):
        item = menu.Append(-1, label)
        self.Bind(wx.EVT_MENU, 
                  lambda evt, label=label: self.on_menu(evt, label), 
                  item)
    
    # e poi, nel callback:
    def on_menu(self, evt, label):
        print label # -> restituisce la voce selezionata

