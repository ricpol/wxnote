.. _wxapp_avanzata:

.. index::
   single: wx.App
   single: wx.App; MainLoop
   
``wx.App``: concetti avanzati.
==============================

:ref:`Abbiamo già visto <wxapp_basi>` i concetti di base sulla ``wx.App``, e come usarla per avviare la nostra applicazione wxPython. 

In sostanza, si tratta di creare la ``wx.App``, creare e mostrare il frame principale, e "avviare il motore" chiamando il ``MainLoop`` della nosrta ``wx.App``. 

Questo in genere è più che sufficiente per i casi più semplici. Tuttavia, per le applicazioni più complesse, potreste volere qualche tipo di controllo in più su questo processo di avviamento. 

.. index::
   single: wx.App; OnInit
   
``wx.App.OnInit``: il bootstrap della vostra applicazione.
----------------------------------------------------------

Per questo, dovete creare una sotto-classe personalizzata di ``wx.App``, e sovrascrivere il metodo ``OnInit``. 

Il codice che scrivete in ``OnInit`` viene eseguito *non appena* la ``wx.App`` è stata istanziata, ma *prima* di entrare nel ``MainLoop``. E' il momento giusto, tipicamente, per inizializzare alcune risorse esterne (connessioni al database, log di sistema, file di configurazione, opzioni "globali"...). Infine, convine usare ``OnInit`` anche per istanziare e mostrare il frame principale dell'applicazione: infatti, farlo in questo momento garantisce che la ``wx.App`` esiste già, e quindi la creazione di frame e altri elementi può avvenire senza problemi. 

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
    
    if __name__ == '__main__':
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
        pass # etc etc
    
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

Come si vede, ``OnInit`` è molto flessibile, e consente di controllare un momento solitamente delicato come lo startup dell'applicazione in modo preciso, compreso il feedback all'utente ed eventuali interazioni con lui. L'uso accorto di ``OnInit`` permette anche di velocizzare i tempi: se qualcosa deve andar storto, si può fermare tutto prima di caricare la parte più gravosa dell'interfaccia. 

Infine, una piccola eleganza: avete notato che quando chiudiamo ``MyLoginDialog`` la nostra applicazione continua a vivere (almeno fin quando, eventualmente, non decidiamo di ``return False``), nonostante abbiamo appena chiuso l'unica finestra "top level" presente? In effetti questa è un'eccezione alla regola: wxPython non inizia il processo di chiusura, se non è mai entrato nel ``MainLoop``. Questo ci consente di aprire e chiudere finestre a nostro piacimento in ``OnInit`` senza paura di conseguenze spiacevoli.

.. note:: Potreste chiedervi perché c'è bisogno di un metodo separato ``OnInit`` per queste operazioni di apertura, quando in genere in questi casi si lavora direttamente nell'``__init__`` della classe. Il punto è che l'``__init__`` è riservato al bootstrap della stessa ``wx.App``, e non è il posto giusto per metterci dentro anche il codice di inizializzazione della vostra applicazione. Per esempio l'``__init__`` deve sempre restituire ``None``, e quindi non è agevole gestire un errore di inizializzazione differenziandolo con un diverso codice di uscita. Se ve la sentite, potete pasticciare con l'``__init__`` a vostro rischio e pericolo, naturalmente. Ma ``OnInit`` fornisce già un comodo aggancio per tutte le vostre necessità. 

.. _wxapp_avanzata_onexit:

.. index::
   single: wx.App; OnExit
   
``wx.App.OnExit``: gestire le operazioni di chiusura.
-----------------------------------------------------

In modo speculare, la ``wx.App`` fornisce anche un hook per il codice che volete eseguire subito prima della chiusura. ``OnExit`` verrà eseguito *dopo* che l'ultima finestra top-level è stata chiusa, ma *prima* di distruggere la ``wx.App``. 

In ``OnExit`` potete inserire il vostro codice di chiusura personalizzato: chiudere le connessioni al database, chiudere i log, salvare le configurazioni e le preferenze... 

Proprio come avviene in ``OnInit``, anche in ``OnExit`` potete approfittarne per chiedere ancora qualche decisione all'utente. Potete ancora mostrare un ``wx.Dialog`` modale (ossia mostrato con ``ShowModal()``).

Se però cercate di creare e mostrare un nuovo frame "top level" a questo punto, nella speranza di prevenire la chiusura della ``wx.App``, ormai è troppo tardi. Il frame verrà mostrato per un attimo, ma poi si chiuderà subito e tutto terminerà. 

.. note:: Avvertenza per gli spericolati: non vale neppure cercare di prevenire la chiusura dell'applicazione settando ``self.SetExitOnFrameDelete(False)`` *prima* di mostrare il nuovo frame top-level. Effettivamente il frame resta visibile, ma l'applicazione si pianta. Questo codice, per esempio, *non funziona*:

    ::

        class MyApp(wx.App):
            def OnInit(self):
                wx.Frame(None).Show()
                return True
                
            def OnExit(self):
                self.SetExitOnFrameDelete(False)
                wx.Frame(None).Show()
                self.SetExitOnFrameDelete(True)

Parlare di ``OnExit`` ci porta naturalmente a parlare più nel dettaglio del processo di chiusura delle applicazioni wxPython... ma a questo argomento dedichiamo :ref:`una pagina separata <chiusuraapp>`. 


.. _reindirizzare_stdout:

.. index::
   single: stdout/err; wx.PyOnDemandOutputWindow
   single: wx.PyOnDemandOutputWindow
   single: stdout/err; wx.App.RedirectStdio
   single: wx.App; RedirectStdio
   single: stdout/err; wx.App.outputWindowClass
   single: wx.App; outputWindowClass


Re-indirizzare lo standard output/error.
----------------------------------------

Durante tutto il ciclo di vita di una applicazione wxPython, lo standard output e lo standard error sono normalmente utilizzati, e per default restano come di consueto indirizzati verso la shell da cui avete invocato lo script Python del vostro programma. 

Il costruttore di ``wx.App`` accetta tuttavia un argomento ``redirect`` che determina se l'output dell'applicazione deve essere re-indirizzato altrove:

* se ``redirect=False`` (default su Unix), l'output è inviato alla shell;

* se ``redirect=True`` (default su Windows) e l'argomento ``filename`` è impostato, l'output è inviato a un file;

* infine, se ``redirect=True`` e ``filename`` non è impostato, l'output è inviato a una apposita finestra dell'interfaccia grafica. 

Cominciamo a vedere un esempio di re-indirizzamento verso un file::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b = wx.Button(p, -1, 'clic', pos=(20, 20))
            b.Bind(wx.EVT_BUTTON, self.on_clic)

        def on_clic(self, evt):
            print '\n\nEcco un esempio di standard output...\n'
            print '... segue un esempio di standard ERROR: '
            print 1/0

    if __name__ == '__main__':
        app = wx.App(redirect=True, filename='output.txt')
        MyFrame(None).Show()
        app.MainLoop()

Per provare invece il re-indirizzamento verso una finestra della gui, provate semplicemente a usare lo stesso frame con questa ``wx.App``::

    if __name__ == '__main__':
        app = wx.App(True) # re-indirizzamento verso una finestra
        MyFrame(None).Show()
        app.MainLoop()

Notate che all'inizio la finestra dell'output non è visibile: si apre la prima volta che viene scritto qualcosa su uno dei due stream. 

La finestra che ospita l'output, per default, è gestita da ``wx.PyOnDemandOutputWindow``. Si tratta di una classe che, non appena è necessario, crea, mostra e gestisce un semplice frame con un ``wx.TextCtrl`` multi-linea e di sola lettura. Le scritture degli stream nel ``wx.TextCtrl`` sono thread-safe: se provengono da thread secondari, sono chiamate attraverso ``wx.CallAfter``. 

La finestra di output, una volta creata, è una :ref:`finestra top-level<finestre_toplevel>`: questo è necessario, perché al momento di istanziare la ``wx.App`` con ``redirect=True`` nessun frame principale è ancora stato creato. Tuttavia è una limitazione fastidiosa: anche quando l'utente ha chiuso la finestra principale dell'applicazione, la ``wx.App`` (e quindi in sostanza il programma) resterà in vita, finché non viene chiusa anche la finestra dell'output. Se questo per voi è un problema, potete chiamare ``wx.PyOnDemandOutputWindow.SetParent`` per assegnare un parent alla finestra di output. Tuttavia questo va fatto in un momento preciso: dovete chiamare ``SetParent`` *dopo* aver creato almeno il frame principale (per forza: altrimenti non avete nessun parent da assegnare alla finestra di output); ma *prima* che la finestra sia creata la prima volta (ovvero, prima che venga scritto qualcosa nell'output). Un esempio chiarirà forse meglio: usate ancora una volta il frame dell'esempio precedente, ma avviate l'applicazione in questo modo::

    if __name__ == '__main__':
        app = wx.App(True) # re-indirizzamento verso una finestra
        frame = MyFrame(None)
        # questo e' il momento giusto per impostare il parent della stdioWin
        app.stdioWin.SetParent(frame)
        frame.Show()
        app.MainLoop()

Come si vede dal questo esempio, quando creiamo una ``wx.App`` con il parametro ``redirect=True``, questa crea subito una istanza di ``wx.PyOnDemandOutputWindow`` e ne conserva un riferimento in ``wx.App.stdioWin``. Possiamo quindi usare questa variabile per impostare il parent della finestra di output *prima* che ``wx.PyOnDemandOutputWindow`` abbia il tempo di crearla (cosa che avviene automaticamente la prima volta che viene scritto qualcosa nello stream): per maggior sicurezza, in questo caso abbiamo preferito impostare il parent prima ancora di mostare la finestra principale dell'applicazione. 

Il re-indirizzamento dell'output può essere deciso anche a run-time, in un momento successivo alla creazione della ``wx.App``. Per questo basta chiamare il metodo ``wx.App.RedirectStdio``, che accetta un argomento opzionale ``filename`` (se impostato, l'output viene scritto su un file; altrimenti, viene mostrata la finestra). Analogamente, ``wx.App.RestoreStdio`` ripristina il normale indirizzamento dell'output verso la shell::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b = wx.Button(p, -1, 'clic', pos=(20, 20))
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            c = wx.CheckBox(p, -1, "re-indirizzamento output", pos=(20, 60))
            c.Bind(wx.EVT_CHECKBOX, self.on_check)

        def on_check(self, evt):
            app = wx.GetApp()
            if evt.IsChecked():
                app.RedirectStdio()
                # provate anche:
                # app.RedirectStdio('output.txt') 
            else:
                app.RestoreStdio()
                # questo e' necessario perche' la finestra non si chiude da sola
                app.stdioWin.close() # notare la "c" minuscola!

        def on_clic(self, evt):
            print '... uno standard output ...'

    if __name__ == '__main__':
        app = wx.App(False)
        MyFrame(None).Show()
        app.MainLoop()

Se poi ``wx.PyOnDemandOutputWindow`` vi sembra troppo spartana e volete mostrare l'output in un modo più elegante, anche questo si può fare. Il tipo di finestra impiegata è determinato dall'attributo ``wx.App.outputWindowClass``. Si tratta di un attributo di classe, e pertanto può essere impostato perfino prima di istanziare la ``wx.App``::

    if __name__ == '__main__':
        wx.App.outputWindowClass = MyOutputClass # una classe personalizzata
        app = wx.App(True) 
        # etc etc

Oppure, se volete sotto-classare ``wx.App``::

    class MyApp(wx.App):
        MyApp.outputWindowClass = MyOutputClass
        def OnInit(self):
            # etc etc

La vostra classe personalizzata può essere qualsiasi cosa: potete sotto-classare ``wx.App.outputWindowClass`` oppure creare da zero. Dovete tuttavia impegnarvi a rispettare l'api di ``wx.App.outputWindowClass``, mettendo a disposizione i seguenti metodi:

* ``CreateOutputWindow(self, txt)`` dove create effettivamente la finestra di output, e ci scrivete il primo messaggio ricevuto (``txt``);

* ``write(self, txt)`` dove scrivete il testo nella finestra di output (che se non c'è ancora, deve essere creata). Ricordatevi che questo metodo potrebbe essere chiamato da thread secondari, e quindi dovrebbe essere thread-safe (e se non lo è, come minimo ricordatevi di non usare i thread!);

* ``close()`` dove chiudete la finestra di output;

* ``flush()`` che viene chiamato per i file e quindi dev'esserci, ma non dovrebbe essere necessario per una finestra grafica (e infatti nell'implementazione di ``wx.App.outputWindowClass`` è una NOP).

Inoltre, dovreste come minimo ricordarvi di intercettare il ``wx.EVT_CLOSE`` che si genera quando l'utente chiude la finestra per conto proprio (oppure, rendere la finestra non chiudibile in qualche modo).

Nell'esempio che segue proponiamo una semplice alternativa, che aggiunge un pulsante per pulire la finestra e uno per salvare l'output su un file. Notate come abbiamo implementato tutti i metodi richiesti, e ci siamo anche assicurati che le scritture siano thread-safe::

    class MyOutputWindow(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            self.text = wx.TextCtrl(p, style=wx.TE_MULTILINE|wx.TE_READONLY)
            clear = wx.Button(p, -1, 'cancella')
            save = wx.Button(p, -1, 'salva...')
            clear.Bind(wx.EVT_BUTTON, self.on_clear)
            save.Bind(wx.EVT_BUTTON, self.on_save)

            s = wx.BoxSizer(wx.VERTICAL)
            s.Add(self.text, 1, wx.EXPAND|wx.ALL, 5)
            s1 = wx.BoxSizer(wx.HORIZONTAL)
            s1.Add(clear, 1, wx.EXPAND|wx.ALL, 5)
            s1.Add(save, 1, wx.EXPAND|wx.ALL, 5)
            s.Add(s1, 0, wx.EXPAND)
            p.SetSizer(s)

        def on_clear(self, evt):
            self.text.Clear()

        def on_save(self, evt):
            filename = wx.FileSelector('Salva output', wildcard='TXT files|*.txt', 
                                       flags=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
            if filename.strip():
                with open(filename, 'a') as f:
                    f.write(self.text.GetValue())

        def write(self, txt):
            self.text.AppendText(txt)


    class MyOutputManager(object):
        def __init__(self):
            self.frame = None
            self.parent = None

        def SetParent(self, parent):
            self.parent = parent

        def CreateOutputWindow(self, txt):
            self.frame = MyOutputWindow(self.parent, -1, title='stdout/stderr')
            self.frame.write(txt)
            self.frame.Show(True)
            self.frame.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
            
        def OnCloseWindow(self, event):
            if self.frame is not None:
                self.frame.Destroy()
            self.frame = None
            self.parent = None

        def write(self, txt):     
            if self.frame is None:
                if not wx.Thread_IsMain(): # le scritture sono thread-safe!
                    wx.CallAfter(self.CreateOutputWindow, txt)
                else:
                    self.CreateOutputWindow(txt)
            else:
                if not wx.Thread_IsMain(): # le scritture sono thread-safe!
                    wx.CallAfter(self.frame.write, txt)
                else:
                    self.frame.write(txt)

        def close(self):
            if self.frame is not None: # anche la chiusura deve essere thread-safe
                wx.CallAfter(self.frame.Close)

        def flush(self): pass


    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b = wx.Button(p, -1, 'clic', pos=(20, 20))
            b.Bind(wx.EVT_BUTTON, self.on_clic)

        def on_clic(self, evt):
            print '... uno standard output ...'


    if __name__ == '__main__':
        # impostiamo MyOutputManager come finestra dell'output
        wx.App.outputWindowClass = MyOutputManager
        app = wx.App(True)
        MyFrame(None).Show()
        app.MainLoop()

.. todo:: una pagina sui thread.
