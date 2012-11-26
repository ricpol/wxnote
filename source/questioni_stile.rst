Questioni varie di stile.
=========================

Raccogliamo in questa pagina alcune questioni forse più di stile che di sostanza, che tuttavia possono confondere chi è nuovo al mondo wxPython. 


To ``self`` or not to ``self``?
-------------------------------

Quando si costruisce :ref:`un contenitore <contenitori>` (un panel, frame, dialogo), in genere nell'``__init__`` si elencano i widget che deve contenere. E qui si pone un piccolo problema: è necessario che i loro nomi siano visibili in tutta l'istanza del contenitore, oppure solo all'interno del metodo ``__init__`` in cui li definiamo? Ovvero, è necessario sempre premettere ``self.`` al nome, oppure no?

La domanda si pone anche perché, all'inizio della propria esperienza con wxPython, molti purtroppo usano :ref:`strumenti sbagliati <non_usare>` come gui builder o RAD. Quando esaminate il codice prodotto da questi pessimi assistenti, trovate interminabili elenchi del genere::

    self.button_1 = wx.Button(...)
    self.button_2 = wx.Button(...)
    self.text_ctrl_1 = wx.TextCtrl(...)
    self.label_1 = wx.StaticText(...)
    self.label_2 = wx.StaticText(...)
    
e perfino con i sizer::

    self.sizer_1 = wx.BoxSizer(...)

Il principiante ne ricava spesso la sensazine che il ``self.`` sia necessario. In realtà wxPython non richiede assolutamente niente del genere. 

Regolatevi *come fareste per un normale programma a oggetti*: solo quando vi serve mantenere un riferimento visibile anche negli altri metodi della classe, allora usate il ``self.``. Altrimenti, potete benissimo farne a meno. 

Considerate per esempio un normale pulsante: di solito avete bisogno del suo nome solo per collegarlo a un evento, e per inserirlo in un sizer::

    button = wx.Button(...)
    button.Bind(wx.EVT_BUTTON, ...)
    sizer.Add(button, ...)
    
Se tutte queste operazioni avvengono nell'``__init__``, non avete bisogno di chiamarlo ``self.button``. 

Un altro esempio: è rarissimo che vi serva il nome di un sizer al di fuori del metodo in cui lo avete creato. Premettere ``self.`` ai nomi dei sizer è quasi sempre inutile. 

E ancora: le label (``wx.StaticText``) vengono dichiarate e inserite nel layout, e mai più toccate. E' un altro caso in cui il ``self.`` non serve a nulla. Addirittura, nel caso delle label è frequente trovare questo pattern::

    sizer.Add(wx.TextCtrl(...), ...)
    
ovvero, creare un label "anonima" solo nel momento in cui bisogna aggiungerla al layout. Il nome della label qui *non è specificato*, perché non serve neppure all'interno dell'``__init__``. 

In definitiva, è anche una questione di stile personale. Potete benissimo aggiungere ``self.`` ovunque: inquinerete un pochino il namespace della vostra classe, ma non è grave. Per quel che vale, io preferisco regolarmi in modo diverso: uso ``self.`` solo per i nomi che effettivamente utilizzo anche altrove, e mantengo locali tutti gli altri. Questo mi consente di vedere a colpo d'occhio i widget più "importanti" nella mia gui. 


Costruire il layout nell'``__init__`` o no?
-------------------------------------------

Ovviamente il layout di un frame, di un dialogo o di un panel va specificato nell'``__init__``, prima di mostrarlo all'utente. Tuttavia, alcuni preferiscono spostare il disegno "puro e semplice" del layout (creazione e popolamento dei sizer) in un metodo separato (``_do_layout`` o qualcosa del genere) che viene richiamato dall'``__init__``. 

Più o meno quindi il pattern è questo::

    def __init__(self, ...):
        self.button_A = wx.Button(...)
        self.text_A = wx.TextCtrl(...)
        # etc. etc. 
        self._do_layout()
        
    def _do_layout(self):
        sizer = wx.BoxSizer(...)
        sizer.Add(self.button_A, ...)
        sizer.Add(self.text_A, ...)
        # etc. etc.
        
Ovviamente si tratta di una separazione puramente estetica: se nel codice eliminate le due righe ``self._do_layout()`` e ``def _do_layout(self)``, tutto funziona esattamente come prima. E' uno schema molto usato nel codice generato automaticamente dagli stessi :ref:`pessimi assistenti <non_usare>` di cui sopra. 

Lo schema può estendersi ulteriormente: per esempio, aggiungere un metodo ``_set_properties`` per impostare colori, font, etc. dei vari widget; aggiungere un metodo ``_do_binding`` per raccogliere tutti i collegamenti degli eventi ai callback. 

Le ragioni addotte per queste separazioni sono sempre molto deboli: è vero, in questo modo l'``__init__`` è più snello e contiene solo la definizione dei widget contenuti. Tuttavia è solo una suddivisione grafica, a beneficio dell'occhio.

Ma allora basta usare qualche divisore "grafico", qualcosa del genere::

    def __init__(self, ...)
        button_A = wx.Button(...)
        text_A = wx.TextCtrl(...)
        # etc. etc. 

        # layout ------------------------------------------------------
        sizer = wx.BoxSizer(...)
        sizer.Add(button_A, ...)
        sizer.Add(text_A, ...)
        # etc. etc.
        
        # eventi ------------------------------------------------------
        button_A.Bind(wx.EVT_BUTTON, ...)
        # etc. etc.
        
Naturalmente lo svantaggio immediato dei vari ``_do_layout`` etc., è la proliferazione dei ``self.`` (vedi paragrafo precedente), perché ogni widget creato nell'``__init__`` deve essere visibile anche nel ``_do_layout``. 
    
Ma la cosa importante è capire che non si tratta di un reale processo di fattorizzazione: non una singola riga di codice viene rielaborata e ridotta a pattern comuni. 

Anzi, questa separazione artificiosa può addirittura ostacolare la fattorizzazione del codice. Considerate per esempio questo modo di procedere molto compatto, che genera una serie di pulsanti, li collega a eventi e li inserisce in un sizer, tutto in una volta::

    for label in ('foo', 'bar', 'baz'):
        b = wx.Button(self, -1, label)
        b.Bind(wx.EVT_BUTTON, self.callback)
        sizer.Add(b, 1, wx.EXPAND|wx.ALL, 5)
        
Chiaramente una cosa del genere non sarebbe più possibile con la divisione tra ``__init__`` e ``_do_layout``. 

In conclusione, lasciate perdere i vari ``_do_layout`` e iniziate a scrivere tutto quanto nell'``__init__``. Dopo di che, ponetevi il problema di una reale fattorizzazione del codice. Un buon esempio (forse troppo pignolo, a dire il vero) si trova :ref:`tra gli esempi della documentazione <altri_esempi>` tratti dal capitolo 5 del libro "wxPython in Action". Confrontate lo script ``badExample.py`` con ``goodExample.py`` per avere un'idea di come si possa riformulare lo stesso layout in modo più compatto e "astratto". 
