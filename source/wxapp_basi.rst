.. highlight:: python
   :linenothreshold: 5

.. _wxapp_basi:

.. index:: 
   single: wx; App()
   single: wx.App; MainLoop()
   
``wx.App``: le basi da sapere.
==============================

Questa pagina racconta le pochissime cose assolutamente da sapere sulla ``wx.App``, che è il cuore di ogni applicazione wxPython. Se non avete mai toccato wxPython in vita vostra, dovete iniziare di qui. 


Che cosa è una ``wx.App`` e come lavorarci.
-------------------------------------------

La classe ``wx.App`` è il motore della nostra interfaccia grafica. Ogni applicazione wxPython deve avere una ``wx.App`` istanziata e funzionante. 

* La ``wx.App`` deve essere creata (istanziata) prima di istanziare ogni altra cosa, altrimenti wxPython darà errore; 

* La ``wx.App`` dovrebbe essere "messa in moto" (chiamando il suo ``MainLoop`` come vedremo tra pochissimo) immediatamente dopo aver mostrato l'interfaccia, altrimenti tutto resterà inerte. 

Esaminiamo questo codice, che crea e mostra un frame con un bottone che cambia colore quando viene premuto::

    from random import randint
    import wx

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.button = wx.Button(self, -1, 'Hello word!')
            self.button.Bind(wx.EVT_BUTTON, self.on_clic)

        def on_clic(self, evt):
            self.button.SetBackgroundColour((randint(0, 255), 
                                             randint(0, 255), 
                                             randint(0, 255)))
                                                
    app = wx.App(False)
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()

Concentriamoci solo sulle ultime quattro righe. Tutto il resto è abbastanza intuitivo, ma in ogni caso non ci interessa: basta dire che è il codice necessario per definire le caratteristiche del nostro frame con il pulsante cambia-colore. 

La riga 15 crea una istanza della ``wx.App`` (non preoccupatevi per il momento di quel ``False`` nel costruttore). Solo a questo punto è possibile creare (istanziare) qualsiasi altro elemento wxPython (se non ci credete, provate a scambiare tra loro le righe 15 e 16...). 

La riga successiva crea una istanza del nostro frame (di nuovo... non preoccupatevi del significato di quel ``None``), e la riga dopo lo mostra sullo schermo. Tutto sembra a posto, ma in realtà niente si è ancora messo in moto. Provate a togliere l'ultima riga, e fate girare lo script: il frame si visualizza come prima, ma quando provate a cliccare sul pulsante, nulla accade. 

E' solo quando, alla riga 18, invochiamo il ``MainLoop`` della nostra ``wx.App`` che le cose si mettono davvero in moto. 


Il ``MainLoop``: il motore della gui.
-------------------------------------

Il ``MainLoop`` della ``wx.App`` è il ciclo principale della nosta applicazione wxPython. Potete pensarlo come un grande ``while True`` senza fine. A ogni iterazione del ciclo, wxPython controlla se gli elementi della gui si sono mossi, se sono partiti degli eventi a cui bisogna rispondere, e insomma gestisce tutte le fasi della vita della nostra gui. 

Il ciclo termina solo quando l'ultimo elemento della gui viene distrutto (tipicamente, quando l'utente chiude l'ultimo frame facendo clic sul pulsante di chiusura, con un menu, una scorciatoia da tastiera, o in qualsiasi altro modo). 

.. highlight:: python
   :linenothreshold: 15
   
Prima e dopo il ``MainLoop``, il controllo è mantenuto normalmente dal modulo Python in cui vive il codice. Ma da quando invocate il ``MainLoop``, il controllo dell'applicazione passa a wxPython, che non lo restituisce fino a quando non si è usciti dal ``MainLoop``. Per rendervene conto, modificate le ultime righe dell'esempio precedente in questo modo::
 
    print 'qui siamo fuori dal MainLoop'
    print "e il controllo non e' ancora passato a wxPython..."
    raw_input('...premere <invio> per tuffarsi dentro wxPython!')
    
    app = wx.App(False)
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()
    
    print '...e adesso siamo usciti da wxPython:'
    raw_input('premere <invio> per terminare lo script Python.')
    
Prima di entrare nel ``MainLoop``, la vostra gui non funziona. Ma una volta che ci siete entrati, non è possibile eseguire altro codice Python che risiede "fuori" da wxPython (a meno di non metterlo in un thread separato, si capisce... ma questo per il momento è fuori portata per noi). 

Questo comportamento è tipico delle gui, e degli altri framework che devono rispondere a eventi (PyGame, per esempio). Devono stare in attesa delle interazioni dell'utente, e per questo "occupano" costantemente il flusso del programma con il loro mainloop. 

In sostanza, una volta entrati dentro wxPython, tutto deve essere pilotato da "dentro" wxPython. Questo rende più complicato separare le funzioni delle varie parti del codice, per esempio applicando il pattern Model-View-Controller. Vedremo in una lezione più avanzata come adattare MVC al contesto di wxPython (e dei gui framework in genere). 

.. todo:: una pagina su MVC!

Per il momento, non è molto quello che occorre sapere: il più delle volte, basta ricordarsi di creare la ``wx.App`` e quindi invocare il suo ``MainLoop``. Tutto il resto può essere pilotato direttamente dalla finestra principale della vostra gui.

Quindi, per "ingranare" la nostra applicazione, bastano di solito le tre righe magiche::

    app = wx.App(False)
    MainFrame(None).Show() # dove MainFrame e' il frame principale dell'applicazione
    app.MainLoop()

Ci sono però ancora parecchie cose da sapere sulla ``wx.App``: ma sono :ref:`argomenti più avanzati <wxapp_avanzata>` che per il momento non vi servono. 

Per completare il quadro, abbiamo detto: si esce dal ``MainLoop`` quando l'ultimo elemento della gui viene distrutto. Dovremmo specificare meglio: quando l'ultima finestra "top level" viene chiusa e distrutta. Ma per questo bisogna prima spiegare meglio il concetto di "top level frame", e, più in generale, della catena dei "parent". Dedichiamo a questo argomento :ref:`una pagina separata <catenaparent>`. 

