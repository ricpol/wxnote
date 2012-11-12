.. _wxapp_avanzata:

``wx.App``: concetti avanzati.
==============================

:ref:`Abbiamo già visto <wxapp_basi>` i concetti di base sulla ``wx.App``, e come usarla per avviare la nostra applicazione wxPython. 

In sostanza, si tratta di creare la ``wx.App``, creare e mostrare il frame principale (quello "top level": ma possono anche essere più di uno), e "avviare il motore" chiamando il ``MainLoop`` della nosrta ``wx.App``. 

Questo in genere è più che sufficiente per i casi più semplici. Tuttavia, per le applicazioni un po' più complesse, potreste volere qualche tipo di controllo in più su questo processo di avviamento. 


``wx.App.OnInit``: il bootstrap della vostra applicazione.
----------------------------------------------------------

Per fare questo, dovete creare una sotto-classe personalizzata di ``wx.App``, e sovrascrivere il metodo ``OnInit``. 

Il codice che scrivete in ``OnInit`` viene eseguito *non appena* la ``wx.App`` è stata istanziata, ma *prima* di entrare nel ``MainLoop``. E' il momento giusto, tipicamente, per inizializzare alcune risorse esterne (connessioni al database, log di sistema, file di configurazione, opzioni "globali"...). Infine, convine usare ``OnInit`` anche per istanziare e mostrare il frame principale dell'applicazione: infatti, farlo in questo momento assicura che la ``wx.App`` esiste già, e quindi la creazione di frame e altri elementi può avvenire senza problemi. 

Ecco un'idea di come potrebbero andare tipicamente le cose::

    class MyApp(wx.App):
        def OnInit(self):
            # avvio la connessione al database  
            self.db = connect(my_db, ...) 
            # apro un log   
            self.log = open('logfile', 'a') 
            # leggo un file di configurazione
            config = ConfigParser.ConfigParser(...) 
            # creo il frame principale
            top_frame = MyFrame(None) 
            # lo mostro
            top_frame.Show()  
            # esco da OnInit segnalando che tutto e' a posto        
            return True
            
    app = MyApp(False)   # istanzio la mia app personalizzata
    app.MainLoop()       # e invoco il MainLoop per avviarla
    
Questo modo di procedere presenta numerosi vantaggi. Per esempio, se una connessione al database viene aperta in ``OnInit``, "appartiene" alla ``wx.App``, e quindi è disponibile globalmente per tutti gli elementi presenti e futuri dell'applicazione. Da qualunque posto, per ottenere un riferimento al database basterà questo::

    db = wx.GetApp().db
    
Un altro vantaggio è che ``OnInit`` **deve** restituire esplicitamente ``True`` alla fine delle sue operazioni: solo se restituisce ``True`` la ``wx.App`` continuerà a vivere. Se invece restituisce ``False``, la ``wx.App`` verrà chiusa, e la nostra applicazione abortirà prematuramente. 

Questo può essere sfruttato per chiudere subito tutto, quando per esempio una risorsa esterna non è disponibile. Per esempio, potete fare questo::

    class MyApp(wx.App):
        def OnInit(self):
            try:
                self.db = connect(my_db, ...)
            except:
                return False
            top_frame = MyFrame(None) 
            top_frame.Show()     
            return True
            
Se per qualche ragione il db non è raggiungibile, ``OnInit`` esce restituendo ``False``, e tutto si ferma. 

Inoltre, siccome al momento di ``OnInit`` la ``wx.App`` esiste già, è anche possibile mostrare all'utente dei messaggi di emergenza per informarlo dello stato delle cose, e perfino chiedergli di prendere qualche decisione. Per esempio, qualcosa del genere::

    class MyApp(wx.App):
        def OnInit(self):
            try:
                self.db = connect(my_db, ...)
            except:
                wx.MessageBox('Non trovo il db, addio.', 
                              'Errore fatale', wx.ICON_STOP)
                return False
            try:
                config = ConfigParser.ConfigParser(...) 
            except ConfigParser.Error:
                msg = wx.MessageDialog(None, 
                        'Non trovo il file di configurazione. Procedo lo stesso?', 
                        'Errore trascurabile', wx.YES_NO|wx.ICON_EXCLAMATION)
                if msg.ShowModal() == wx.ID_NO:
                    return False
            top_frame = MyFrame(None) 
            top_frame.Show()     
            return True
            
Addirittura, potrebbe essere un buon momento per chiedere all'utente di effettuare il login::

    class MyLoginDialog(wx.Dialog):
        # etc etc
    
    class MyApp(wx.App):
        def OnInit(self):
            try:
                self.db = connect(my_db, ...)
            except:
                wx.MessageBox('Non trovo il db, addio.', 
                              'Errore fatale', wx.ICON_STOP)
                return False
            login = MyLoginDialog(None)
            if login.ShowModal() == wx.ID_OK:
                user, psw = login.GetValue()
                if self.db.get_user_psw(user) != psw:
                    wx.MessageBox('Password errata, addio.', 
                                  'Errore fatale', wx.ICON_STOP)
                    return False
            else:
                return False
            # finalmente, se tutto va bene...
            top_frame = MyFrame(None) 
            top_frame.Show()     
            return True

Come si vede, ``OnInit`` è molto flessibile, e consente di controllare un momento solitamente delicato come lo startup dell'applicazione in modo preciso, fornendo feedback all'utente ed eventualmente interagendo con lui. L'uso accorto di ``OnInit`` permette anche di velocizzare i tempi: se qualcosa deve andar storto, si può fermare tutto prima di caricare la parte più grossa dell'interfaccia. 

.. note:: Potreste chiedervi perché c'è bisogno di un metodo separato ``OnInit`` per queste operazioni di apertura, quando in genere in questi casi si lavora direttamente nell'``__init__`` della classe. Il punto è che l'``__init__`` è riservato al bootstrap della stessa ``wx.App``, e non è il posto giusto per metterci dentro anche il codice di inizializzazione della vostra applicazione. Per esempio l'``__init__`` deve sempre restituire ``None``, e quindi non è agevole gestire un errore di inizializzazione differenziandolo con un diverso codice di uscita. Se ve la sentite, potete pasticciare con l'``__init__`` a vostro rischio e pericolo, naturalmente. Ma ``OnInit`` fornisce già un comodo aggancio per tutte le vostre necessità. 


``wx.App.OnExit``: gestre le operazioni di chiusura.
----------------------------------------------------



















