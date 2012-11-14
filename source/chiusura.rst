.. _chiusura:

.. highlight:: python
   :linenothreshold: 7
   
Chiudere i frame e gli altri widget.
====================================

Il momento della chiusura in wxPython è delicato. In questa pagina esaminiamo il processo di chiusura dei frame e dei dialoghi, e aggiungiamo qualche nota sulla chiusura dei widget in generale. Il discorso prosegue :ref:`in una pagina separata <chiusuraapp>` dove descriviamo il processo di chiusura della ``wx.App``. 

Prima di procedere, un avvertimento. Dopo aver letto questo capitolo, avrete l'impressione che chiudere le cose, in wxPython, sia un procedimento tortuoso. Rispondo subito: è vero. 

Ma non dovete dimenticare che wxPython è solo la superficie di un framework C++. Il punto è che in Python, quando de-referenziate un oggetto, automaticamente tutte le risorse collegate che non servono più vegono pulite dalla memoria dal garbage collector. Ma C++ non ha garbage collector, quindi la memoria va pulita "a mano". Ora, quando chiudete un frame, wxWidget naturalmente provvede da solo a eliminare anche tutti gli elementi di quel frame (pulsanti, caselle di testo, etc.). Ma tutte le risorse "esterne" eventualmente collegate e che non servono più (connessioni al database, strutture-dati presenti in memoria, etc.) devono essere cancellate a mano. 

Ecco perché wxWidget, nel mondo C++, offre numerosi hook lungo il processo di chiusura, dove è possibile intervenire per fare cleanup, o anche ripensarci e tornare indietro. wxPython eredita questo sistema, anche se, onestamente, è raro che un programmatore Python lo utilizzi appieno. 


La chiusura di una finestra.
----------------------------

La chiusura di una "finestra" (un frame o un dialogo) succede (di solito!) in due modi:

* perché l'utente fa clic sul pulsante di chiusura (quello con la X, per intenderci), o usa "Alt+F4" o altri equivalenti; 

* perché voi chiamate ``Close()`` sul frame. 

In entrambi i casi, si innesca un evento particolare, ``wx.EVT_CLOSE``, che segnala al sistema che la finestra sta per chiudersi. 

Se voi non fate nulla, la parola passa al gestore di default, che si comporta in due modi differenti:

* per un ``wx.Frame``, semplicemente chiama ``Destroy()``, e questo pone fine alla vita del frame e ovviamente di tutti i suoi figli;

* per un ``wx.Dialog``, invece, lo nasconde alla vista, *ma non lo distrugge*. Questo comportamento è voluto, per venire incontro alla situazione tipica in cui si vuole raccogliere dei dati dal dialogo, prima di distruggerlo. Resta il fatto che, fin quando non chiamate esplicitamente ``Destroy()``, il dialogo resta in vita. 

Questo è quello che succede se voi non fate nulla. Ma chiaramente, come qualsiasi altro evento, anche ``wx.EVT_CLOSE`` può essere catturato e gestito in un callback. 

In questo caso, diciamo subito la cosa più importante. Se decidete di raccogliere ``wx.EVT_CLOSE`` e gestire da soli il processo di chisura, allora dovete esplicitamente chiamare ``Destroy()`` *anche per i frame*, perché wxPython non farà più nulla al posto vostro. 
   
Potete anche decidere di *non* chiudere la finestra, dopo tutto. Questo, per esempio, è un procedimento tipico (anche se, dal punto dell'usabilità, è una pessima pratica che vi sconsiglio)::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.Bind(wx.EVT_CLOSE, self.on_close)
        
        def on_close(self, evt):
            msg = wx.MessageDialog(self, 'Sei proprio sicuro?', 'Uscita', 
                                   wx.ICON_QUESTION|wx.YES_NO)
            if msg.ShowModal() == wx.ID_YES:
                self.Destroy()
            msg.Destroy()

Alla riga 10, chiamiamo esplicitamente ``self.Destroy()`` solo se l'utente ha risposto affermativamente. In caso contrario, chiamiamo comunque ``Destroy()`` almeno sul ``MessageDialog`` che abbiamo creato, perché altrimenti resterebbe in vita.

Come abbiamo detto, ``wx.EVT_CLOSE`` si innesca anche quando voi chiamate ``Close()``. Per vederlo, possiamo aggiungere un semplice pulsante che chiama ``Close`` nel suo callback::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            b = wx.Button(self, -1, 'chiudimi!')
            b.Bind(wx.EVT_BUTTON, self.on_click)
            self.Bind(wx.EVT_CLOSE, self.on_close)
        
        def on_click(self, evt): 
            self.Close()
            
        def on_close(self, evt):
            msg = wx.MessageDialog(self, 'Sei proprio sicuro?', 'Uscita', 
                                   wx.ICON_QUESTION|wx.YES_NO)
            if msg.ShowModal() == wx.ID_YES:
                self.Destroy()
            msg.Destroy()

Anche quando agite sul pulsante, il ``self.Close()`` della riga 9 scatena comunque il ``wx.EVT_CLOSE``, e di conseguenza viene eseguito il codice del callback ``on_close``.


Chiamare ``Veto()`` se non si vuole chiudere.
---------------------------------------------

Se alla fine decidete di non chiudere la finestra, è buona norma chiamare sempre ``Veto()`` sull'evento ``wx.EVT_CLOSE``, per segnalare al resto del sistema che la richiesta di chiusura è stata respinta. 

Per esempio, nel codice appena visto, dovreste aggiungere ``evt.Veto()`` alla fine del gestore ``on_close``. Ora, in questo specifico caso non vi serve comunque a nulla, perché nessun'altra parte del vostro codice è interessata alla chiusura di quella finestra. 

Ma ``Veto()`` diventa utile, per esempio, quando chiamate ``Close()`` su una finestra *da un'altra finestra*: in questo caso, la finestra che ordina la chiusura potrebbe essere interessata a sapere se l'ordine è stato eseguito o rifiutato. 

``Close()`` restituisce sempre ``True`` se la chiusura è andata a buon fine. Ma se voi chiamate ``Veto()`` (e non chiudete la finestra, chiaramente), allora ``Close()`` restituisce ``False``, e fa sapere in questo modo come sono andate le cose. 

Ecco un esempio pratico::

    class MyTopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.do_child = wx.Button(self, -1, 'crea un frame figlio')
            self.do_child.Bind(wx.EVT_BUTTON, self.on_child)
            self.child = None
            
        def on_child(self, evt):
            if not self.child:
                self.child = MyChildFrame(self, title='Figlio', size=(150, 150), 
                                    style=wx.DEFAULT_FRAME_STYLE & ~wx.CLOSE_BOX)
                self.child.Show()
                self.do_child.SetLabel('CHIUDI il frame figlio')
            else:
                closed_successful = self.child.Close()
                if closed_successful:
                    self.do_child.SetLabel('crea un frame figlio')
                    self.child = None

    class MyChildFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.Bind(wx.EVT_CLOSE, self.on_close)
            
        def on_close(self, evt):
            msg = wx.MessageDialog(self, 'Sei proprio sicuro?', 'Uscita', 
                                   wx.ICON_QUESTION|wx.YES_NO)
            if msg.ShowModal() == wx.ID_NO:
                evt.Veto()
            else:
                self.Destroy()
            msg.Destroy()
                                    
                                    
    app = wx.App(False)
    MyTopFrame(None).Show()
    app.MainLoop()

In questo esempio, il frame principale crea e poi cerca di chiudere (alla riga 15) un frame figlio. Il frame figlio però può decidere se chiudersi davvero, o rifiutare. Notate che, se decidiamo di non chiuderlo, chiamiamo ``Veto()`` (alla riga 29) in modo che ``Close()`` restituisca ``False``, e quindi il codice chiamante sappia come comportarsi (alle righe 15-18). 

Non chiudere un frame e "vietare" l'evento *sono due cose indipendenti*: se vietate ma poi chiudete lo stesso, ``Close()`` restituisce comunque ``False``, anche se la chiusura in effeti c'è stata. E viceversa. Quindi sta a voi non fare pasticci. 

Dite la verità, vi sembra un po' cervellotico... ve l'avevo detto. E non è ancora finita. 


Ignorare il ``Veto()`` se si vuole chiudere lo stesso.
------------------------------------------------------

E non è ancora finita, dicevamo. Chiamare semplicemente ``Veto()`` su un evento di chiusura potrebbe non essere sicuro. Infatti, talvola l'evento *non ha il potere di "vietare" la chiusura della finestra*. 

Attenzione! Se chiamate ``Veto()`` alla cieca, e l'evento in realtà non può "vietare" un bel niente, wxPython solleva un'eccezione e tutto si pianta... 

Quindi la cosa giusta è verificare sempre se l'evento può "vietare", prima di chiamare ``Veto()``. La verifica può essere fatta chiamando ``CanVeto()`` sull'evento stesso. Ecco come deve essere modificato il callback dell'esempio precedente::

    def on_close(self, evt):
        if evt.CanVeto():
            msg = wx.MessageDialog(self, 'Sei proprio sicuro?', 'Uscita', 
                                   wx.ICON_QUESTION|wx.YES_NO)
            if msg.ShowModal() == wx.ID_NO:
                evt.Veto()
            else:
                self.Destroy()
            msg.Destroy()
        else: # se non possiamo vietare, dobbiamo distruggere per forza...
            self.Destroy()

Uhm... in verità l'annotazione della riga 10 non è del tutto corretta. Anche se non possiamo "vietare" l'evento, possiamo sempre scegliere di non distruggere la finestra, e fare qualcos'altro. Ma questa sarebbe proprio una cosa da non fare. Primo perché ovviamente, se non distruggiamo mai in risposta a un ``wx.EVT_CLOSE``, la nostra finestra non si chiuderà mai (a meno di non distruggerla esplicitamente chiamando ``Destroy()`` anziché ``Close()``). Secondo, perché se non chiamiamo ``Veto()`` (perché non possiamo) e non distruggiamo neppure la finestra, la chiamata a ``Close()`` restituirà comunque ``True`` (perché l'evento non è stato "vietato"), *anche se la finestra non è stata davvero chiusa*. Quindi il codice chiamante potrebbe avere problemi a regolarsi. 

Resta solo una domanda: in quali casi un evento potrebbe non avere il potere di ``Veto``? 

Ebbene, le cose stanno così: di solito un ``wx.CLOSE_EVENT`` ha il potere di ``Veto``. Questo, per esempio, accade quando l'evento si innesca in seguito al clic sul pulsante di chiusura, alla combinazione "Alt+F4" nei sistemi Windows, etc. oppure quando voi chiamate ``Close()`` su una finestra. 

Tuttavia, se voi chiamate ``Close`` con l'opzione ``Close(force=True)``, allora il ``wx.EVT_CLOSE`` che si genera *non ha il potere di "vietare"* un bel niente (più precisamente, restituisce ``False`` quando testate per ``CanVeto()``). 

Questo, come vedete, può essere un bel problema per il codice che gestisce la chiusura: non potete sapere se sarà eseguito in seguito a una chiamata ``Close()`` o a una chiamata ``Close(True)``. Per questo, l'unica soluzione è appunto *testare sempre* se l'evento ``CanVeto()`` prima di chiamare eventualmente il ``Veto()``. 


Essere sicuri che una finestra si chiuda davvero.
-------------------------------------------------

Ancora una precisazione. L'opzione ``force=True`` del metodo ``Close`` è un pochino ingannevole. Non significa affatto, di per sé, che la chiusura della finestra verrà forzata e quindi garantita in ogni caso. Vuol dire solo che l'evento non avrà il potere di "vietare" la chiusura. Ma, come abbiamo visto, se voi intercettate l'evento e nel callback finite per non chiudere la finestra, ebbene la finestra resterà viva anche in seguito a un ``Close(force=True)``. 

Ovviamente scrivere un callback che non chiude la finestra, nonostante l'evento non abbia il potere di ``Veto``, deve essere considerato una cattiva pratica, se non un errore di programmazione vero e proprio. Ma wxPython non ha modo di rilevare una cosa del genere a runtime, e voi non potete sapere se state chiamando ``Close`` su una finestra con un callback scritto male (da qualcun altro, ovviamente!). 

In definitiva, l'unico modo per essere certi che una finestra si chiuda davvero è chiamare direttamente ``Destroy()``, ma così facendo vi perdete l'eventuale gestione dell'evento di chiusura. In generale, non lo consiglio.

Questo lascia aperto il problema: come faccio a sapere se una finestra è stata davvero distrutta?

Ebbene, dopo che avete chiamato ``Close()`` (magari con l'aggiunta di ``force=True``), l'unico modo di sapere se la finestra è stata davvero distrutta, è... chiamarla, ovviamente! Sul "lato Python" di wxPython, il riferimento all'oggetto resterà ancora nel namespace corrente. Ma sul "lato C++" di wxWidgets, quando una finestra è distrutta, semplicemente smetterà di funzionare. Quindi una chiamata successiva a un metodo qualsiasi dovrebbe sollevare un'eccezione ``PyDeadObjectError``, che voi opportunamente intrappolerete in un ``try/except``. Per andare sul sicuro, scegliete un metodo che ogni widget deve avere per forza, per esempio ``GetId``. Qualcosa come::
                                        
    try:
        my_widget.GetId()
    except PyDeadObjectError:
        # siamo sicuri che e' davvero morto
                                        
Ma ci sarebbe ancora un problema (ve lo aspettavate, dite la verità). Quando chiamate ``Close`` o addirittura ``Destroy``, questo impegna wxPython a distruggere la finestra... *appena possibile*, ma non necessariamente subito. Di sicuro la distruzione avverrà entro il prossimo ciclo del ``MainLoop``, ma se chiamate ``GetId`` su un frame *immediatamente dopo* averlo distrutto, la chiamata per il momento andrà ancora a segno. 

Provate questo codice, per esempio::

    class MyTopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            kill = wx.Button(self, -1, 'uccidi il figlio', pos=(10, 10))
            kill.Bind(wx.EVT_BUTTON, self.on_kill)
            autopsy = wx.Button(self, -1, "verifica se e' morto", pos=(10, 50))
            autopsy.Bind(wx.EVT_BUTTON, self.on_autopsy)
            
            self.child = wx.Frame(self, -1, 'FRAME FIGLIO')
            self.child.Show()
            
        def on_kill(self, evt):
            self.child.Destroy() # andiamo sul sicuro...
            self.child.GetId()
            
        def on_autopsy(self, evt):
            self.child.GetId()
        
    app = wx.App(False)
    MyTopFrame(None, size=(150, 150)).Show()
    app.MainLoop()

Sorprendentemente, la chiamata della riga 14 andrà ancora a segno, anche se avete appena distrutto il frame. Se invece, dopo aver distrutto il frame, premete il pulsante "verifica", la chiamata della riga 17 solleverà il tanto sospirato ``PyDeadObjectError``. 

In definitiva, non c'è modo di sapere esattamente *quando* un widget verrà distrutto. Tuttavia, dopo un ragionevole intervallo di tempo, è molto facile capire *se* è stato distrutto. 


Distruggere un singolo widget.
------------------------------

Praticamente tutti i widget in wxPython hanno un metodo ``Close`` e un metodo ``Destroy``. Se volete distruggere un pulsante, per esempio, potete regolarvi come abbiamo visto sopra. 

In genere preferite chiamare direttamente ``Destroy``, perché non avete bisogno di catturare il ``wx.EVT_CLOSE`` di un widget qualsiasi. Tuttavia, nessuno vi vieta di sottoclassare un widget, e prescrivere un comportamento particolare da tenere quando qualcuno cerca di chiuderlo. 

Tuttavia, è raro distruggere un singolo widget. In genere si preferisce disabilitarlo, al limite nasconderlo: distruggerlo lascia un "buco" nel layout sottostante, che bisogna riaggiustare. 

Un caso limite sono i ``Panel``, ovviamente. Questi contenitori sono "quasi" dei frame, e quindi talvolta potrebbe aver senso distruggerli, e perfino gestire qualche raffinatezza con ``Close``. Personalmente, io consiglio di non distruggere mai neppure i ``Panel``. Ovviamente, se distruggete un ``Panel`` (o un altro widget qualsiasi) anche tutti i suoi "figli" verranno spazzati via. 

Ecco un esempio di ``Panel`` "schizzinoso" che potrebbe opporsi alla sua distruzione::

    class MyPanel(wx.Panel):
        def __init__(self, *a, **k):
            wx.Panel.__init__(self, *a, **k)
            self.SetBackgroundColour(wx.RED) # per distinguerlo...
            self.Bind(wx.EVT_CLOSE, self.on_close)

        def on_close(self, evt):
            msg = wx.MessageDialog(self, 'Sei proprio sicuro?', 'Distruggi Panel', 
                                   wx.ICON_QUESTION|wx.YES_NO)
            if msg.ShowModal() == wx.ID_NO:
                evt.Veto()
            else:
                self.Destroy()
            msg.Destroy()

    class TopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b = wx.Button(p, -1, 'distruggi panel')
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            self.b = b
            
            self.mypanel = MyPanel(p)
            s = wx.BoxSizer(wx.VERTICAL)
            s.Add(wx.TextCtrl(self.mypanel, -1, 'figlio di MyPanel'), 
                  0, wx.EXPAND|wx.ALL, 15)
            self.mypanel.SetSizer(s)
            
            s = wx.BoxSizer(wx.VERTICAL)
            s.Add(self.mypanel, 1, wx.EXPAND)
            s.Add(b, 0, wx.EXPAND|wx.ALL, 5)
            p.SetSizer(s)
            
        def on_clic(self, evt):
            ret = self.mypanel.Close()
            if ret:
                pass # etc. etc.

    app = wx.App(False)
    TopFrame(None).Show()
    app.MainLoop()

Come si vede, se il ``Panel`` si chiude davvero, resta un buco. Alla riga 38, bisognerà fare qualcosa: riempire il buco, riaggustare il layout, etc. 

Per finire, una menzione per ``DestroyChildren``: quest'arma di distruzione di massa, usata su un widget qualsiasi, lascia in vita lui ma distrugge automaticamente tutti i suoi "figli". Naturalmente, la distruzione di ciascun figlio comporta a catena la morte anche dei figli del figlio, e così via fino alla totale estinzione dell'albero dei discendenti. Può tornare comodo, per esempio, per svuotare un ``wx.Panel`` senza però distruggerlo, e quindi ripopolarlo daccapo. 


