.. _chiusura:

.. highlight:: python
   :linenothreshold: 7
   
Chiudere frame e applicazioni in wxPython.
==========================================

Il momento della chiusura in wxPython è delicato. In questa pagina esaminiamo il processo di chiusura dei frame e dei dialoghi, e poi il processo di chiusura della ``wx.App``: cerchiamo di capire dove è possibile intervenire, come e quando si verifica una chiusura di emergenza. 

Prima di procedere, un avvertimento. Dopo aver letto questo capitolo, avrete l'impressione che chiudere le cose, in wxPython, sia un procedimento tortuoso. Rispondo subito: è vero. 

Ma non dovete dimenticare che wxPython è solo la superficie di un framework C++. Il punto è che in Python, quando de-referenziate un oggetto, automaticamente tutte le risorse collegate che non servono più vegono pulite dalla memoria dal garbage collector. Ma C++ non ha garbage collector, quindi la memoria va pulita "a mano". Ora, quando chiudete un frame, wxWidget naturalmente provvede da solo a eliminare anche tutti gli elementi di quel frame (pulsanti, caselle di testo, etc.). Ma tutte le risorse "esterne" eventualmente collegate e che non servono più (connessioni al database, strutture-dati presenti in memoria, etc.) devono essere cancellate a mano. 

Ecco perché wxWidget, nel mondo C++, offre numerosi hook lungo il processo di chiusura, dove è possibile intervenire per fare cleanup, o anche ripensarci e tornare indietro. wxPython eredita questo sistema, anche se, onestamente, è raro che un programmatore Python lo utilizzi appieno. 


La chiusura di una finestra.
----------------------------

La chiusura di una "finestra" (un frame o un dialogo) succede (di solito!) in due modi:

* perché l'utente fa clic sul pulsante di chiusura (quello con la X, per intenderci); 

* perché voi chiamate ``Close()`` sul frame (di solito in seguito a qualche azione dell'utente che siete in grado di gestire: un menu, un pulsante "chiudi", etc.). 

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
                                    
                                    
    app = wx.App(False)
    MyTopFrame(None).Show()
    app.MainLoop()

In questo esempio, il frame principale crea e poi cerca di chiudere (alla riga 15) un frame figlio. Il frame figlio però può decidere se chiudersi davvero, o rifiutare. Notate che, se decidiamo di non chiuderlo, chiamiamo ``Veto()`` (alla riga 30) in modo che ``Close()`` restituisca ``False``, e quindi il codice chiamante sappia come comportarsi (alle righe 15-18). 

Non chiudere un frame e "vietare" l'evento *sono due cose indipendenti*: se vietate ma poi chiudete lo stesso, ``Close()`` restituisce comunque ``False``, anche se la chiusura in effeti c'è stata. E viceversa. Quindi sta a voi non fare pasticci. (Dite la verità, vi sembra un po' cervellotico... ve l'avevo detto). 


Terminare la ``wx.App``: il modo normale.
-----------------------------------------

.. todo:: una pagina per le finestre top level, e le gerarchie parent, e 
          molti riferimenti in questo capitolo.
          
La storia semplice è questa: quando il ``MainLoop`` percepisce che anche l'ultima finestra "top level" è stata chiusa, allora decide che il suo lavoro è terminato. Una volta usciti dal ``MainLoop``, c'è ancora l'opportunità di fare qualche operazione di pulizia nel ``wx.App.OnExit``, :ref:`come abbiamo già visto <wxapp_avanzata_onexit>`. Tuttavia non è più possibile, a questo punto, creare una nuova finestra e tenere in vita la ``wx.App``, il cui destino è ormai segnato. Terminato il ``wx.App.OnExit``, la nostra applicazione defunge definitivamente. Dentro il namespace del modulo Python resta ovviamente ancora un riferimento nel nome ``app`` (o quello che avete usato per istanziare la ``wx.App``), ma ormai non ha più alcuna utilità. 

Questa è la storia semplice. Ma ovviamente avete ancora molti modi per complicarvi la vita. 

Per prima cosa, ricordiamo che la ``wx.App`` termina una volta che *tutte* le finestre top-level sono state chiuse, ovvero tutte le finestre che hanno ``parent=None``, come abbiamo già visto. Quindi fate attenzione a non lasciare qualche finestra top-level nascosta ma ancora viva. I casi tipici sono due: avete creato qualche dialogo top-level e non l'avete mai distrutto esplicitamente (ricordiamo che chiamare solo ``Close()`` su un dialogo lo nasconde, ma non lo distrugge). Oppure, avete creato la ``wx.App`` con l'opzione ``redirect=True``, e la finestra dello streaming output è ancora viva ma nascosta per qualche ragione (di solito perché, per tutta la durata della vostra applicazione, non c'è stato niente da scrivere sullo streaming!). In questi casi, l'utente chiude il frame "principale", ma la ``wx.App`` *non termina davvero*. Forse pensate che questo non è un grande problema: l'utente ha comunque finito di interagire con la gui, e prima o poi spegnerà il computer... Ma se invece riavvia e poi "chiude" un po' di volte il programma, ben presto si trova la memoria intasata dalle vostre istanze fantasma. 

E c'è dell'altro: se avete scritto qualcosa nel ``wx.App.OnExit``, *non verrà mai eseguito*, perché non si esce mai dal ``MainLoop``. Inutile dire che, se questo codice comprende operazioni di assestamento dei dati nel database, o delle scritture nel log, queste non verranno eseguite, e la prossima volta che si aprirà il programma ci si troverà con dati inconsistenti. 

Quindi fate sempre molta attenzione a non creare finestre top-level e poi lasciarle in giro senza sapere se ci sono ancora o no. Una strategia di emergenza è catturare il ``wx.EVT_CLOSE`` della finestra "principale" e, prima di distruggerla, verificare che non ci siano altre finestre top level ancora in vita (``wx.GetTopLevelWindows`` torna utile), ed eventualmente chiuderle. Anche in questo caso però fate attenzione perché non è detto che chiamare ``Close()`` basti a garantire la distruzione. La soluzione più brutale è chiamare direttamente ``Destroy()``, più o meno così::
    
    # nel callback dell'EVT_CLOSE della "finestra principale"
    def on_close(self, evt): 
        for window in wx.GetTopLevelWindows():
            if window != self:  # lascio me stesso per ultimo...
                window.Destroy()
        self.Destroy()

Questo funziona senz'altro, ma non è esente da altri rischi. Chiamare ``Destroy()`` sui dialoghi probabilmente va ancora bene: se sono ancora vivi e nascosti, vuol dire che ve ne siete semplicemente dimenticati, ma ormai non dovrebbero più avere nessuna funzione. Per i frame, d'altra parte, la situazione è più delicata. Forse prevedono del codice da eseguire in risposta a un ``EVT_CLOSE``, ma se chiamate ``Destroy()`` invece di ``Close()`` perderete quel passaggio. Questo potrebbe portare a inconsistenze di vario tipo. 

Nel dubbio, vi tocca controllare se si tratta di frame o di dialoghi, e agire con prudenza. Ma come faccio a sapere se una finestra è un frame o un dialogo? Di colpo, siamo nel campo della magia nera di Python::

    def on_close(self, evt):
        ok_to_close = True
        for window in wx.GetTopLevelWindows():
            if window != self: 
                if wx._windows.Frame in window.__class__.__mro__:
                    # e' un frame, proviamo a chiuderlo gentilmente
                    ret = window.Close()
                    if not ret:
                        # evidentemente non vuole chiudersi!
                        ok_to_close = False
                        break
                else:
                    # questo e' un dialogo: distruggiamolo senza pieta'
                    window.Destroy()
        if ok_to_close:
            self.Destroy()
        else:
            # c'e' in giro almeno una finestra che non vuole chiudersi
            wx.MessageBox('Non posso chiudermi!')
            evt.Veto()
            return
            
Come vedete (riga 5), siamo piombati nel difficile, molto difficile. E non è detto che funzioni: per esempio, se una delle finestre rifiuta di chiudersi, ma si "dimentica" di comunicare il suo ``Veto()``, allora ``window.Close()`` (riga 7) restituirà ``True``, e noi crederemo di averla chiusa quando invece è ancora in giro. Ci tocca aggiungere altri test per essere davvero sicuri... 

Ovviamente non sono ipotesi frequenti. Devo dire però di non aver mai usato, in pratica, un metodo come questo per accertarmi che tutte le finestre top-level siano chiuse al momento di uscire dall'applicazione. E francamente vi sconsiglio di provarci. 

**La soluzione corretta** è invece *tenere sempre traccia* di tutte le finestre che aprite, soprattutto quelle top-level, e di accertarvi sempre di chiuderle appena non servono più. In questo modo, quando arriva il momento di chiudere anche l'ultima finestra principale, siete sicuri che anche la ``wx.App`` terminerà la sua vita in modo onesto e dignitoso. 


Come mantenere in vita la ``wx.App``.
-------------------------------------

Ma c'è ancora dell'altro da sapere. Potrebbe capitarvi di *non* volere che la ``wx.App`` termini, ma che il suo ``MainLoop`` resti attivo anche dopo che l'ultima finestra è stata chiusa. (Dopo tutta la fatica che abbiamo fatto nel paragrafo precedente per assicurarci che la ``wx.App`` muoia davvero, sembra una beffa. Ma può succedere.) 

Per fare questo, vi basta chiamare ``SetExitOnFrameDelete(False)`` sulla ``wx.App``. Potete farlo proprio all'inizio, in ``OnInit``::

    class MyApp(wx.App):
        def OnInit(self):
            self.SetExitOnFrameDelete(False)
            return True
            
Oppure potete farlo successivamente, in un momento qualunque della vita del vostro programma, da dentro un frame qualsiasi::

    wx.GetApp().SetExitOnFrameDelete(False)
    
Potete farlo perfino, proprio all'ultimo, intercettando il ``wx.EVT_CLOSE`` dell'ultima finestra principale che sta per chiudersi. L'unico momento in cui ormai è troppo tardi è nel ``wx.App.OnExit``. 

Con questa opzione, il ``MainLoop`` non termina quando l'ultima finesta muore. A questo punto, se volete, potete andare avanti creando delle nuove finestre top-level. Ecco una possibile strategia::

    class MyApp(wx.App):
        def OnInit(self):
            self.SetExitOnFrameDelete(False)
            self.Bind(wx.EVT_IDLE, self.create_new_toplevel)
            wx.Frame(None, title='PRIMA GENERAZIONE').Show()
            return True
        
        def create_new_toplevel(self, evt):
            if not wx.GetTopLevelWindows():
                wx.Frame(None, title='SECONDA GENERAZIONE!!').Show()
                # dopo questa volta pero' basta...
                self.SetExitOnFrameDelete(True)
                            
    app = MyApp(False)
    app.MainLoop()

La procedura è chiara: all'inizio (riga 3) settiamo il flag a ``False``, e quindi creiamo e mostriamo il primo frame top-level. Tuttavia (riga 4) chiediamo anche alla ``wx.App`` di eseguire a ripetizione il metodo ``create_new_toplevel`` nei momenti liberi del ``MainLoop``. Questo metodo controlla se non sono più rimaste vive finestre top level (riga 9), e in questo caso crea e mostra una "seconda generazione" di finestre. Contestualmente (riga 12) riportiamo il flag a ``True``, in modo che alla prossima chiusura il ``MainLoop`` questa volta termini davvero. 

Ecco un altro possibile approccio::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.Bind(wx.EVT_CLOSE, self.on_close)

        def on_close(self, evt):
            wx.CallLater(1, wx.GetApp().create_new_toplevel)
            self.Destroy()
                
    class MyApp(wx.App):
        def OnInit(self):
            self.SetExitOnFrameDelete(False)
            MyFrame(None, title='PRIMA GENERAZIONE').Show()
            return True
        
        def create_new_toplevel(self):
            MyFrame(None, title='SECONDA GENERAZIONE!!').Show()
            self.SetExitOnFrameDelete(True)
        
    app = MyApp(False)
    app.MainLoop()

Qui invece è l'ultima finestra top-level che, al momento della sua chiusura (riga 7) utilizza ``wx.CallLater`` per chiedere alla ``wx.App`` di creare una "seconda generazione" di frame immediatamente dopo la sua morte. 

Notate l'utilizzo di ``wx.CallLater``, che aspetta un certo periodo (in questo caso, 1 ms, il minimo possibile) e poi chiama una funzione. Lo abbiamo scelto perché non tiene impegnato il ``MainLoop``, e quindi ci serve a dimostrare che il ``MainLoop`` resta vivo comunque, per ragioni sue (ossia, perché abbiamo settato il flag a ``False``). 

Avremmo potuto invece usare ``wx.CallAfter``, che è "quasi uguale", nel senso che chiama una data funzione dopo che tutti i gestori degli eventi correnti sono stati processati. Il punto però è che ``wx.CallAfter`` aggiunge la sua funzione in coda ai compiti del ``MainLoop``, e quindi lo tiene impegnato almeno fino a quel momento. E siccome nel nostro caso la funzione chiamata è ``create_new_toplevel`` che appunto crea una nuova finestra top-level, in sostanza il ``MainLoop`` non ha mai modo di terminare, indipendentemente da come è stato settato il flag ``SetExitOnFrameDelete``. 

Provate a sostituire la riga 7 dell'esempio precedente con::

    wx.CallAfter(wx.GetApp().create_new_toplevel)

Quando si distrugge la "prima generazione" compare la seconda, come previsto. Ma quando provate a distruggere anche questa, la ``wx.App`` non termina come prima, anche se il flag è ormai settato a ``True``. Invece, ogni volta appare una nuova "seconda generazione", all'infinito. Questo perché ``wx.CallAfter`` tiene in vita il ``MainLoop`` fino al momento di chiamare ``create_new_toplevel``, dove però si crea una nuova finestra top-level, e quindi il ``MainLoop`` trova un'altra ragione per proseguire la sua attività, e così all'infinito. 

In altri termini ``wx.CallAfter``, usato così, potrebbe essere un'altra strada per non far terminare il ``MainLoop``, senza dover usare ``SetExitOnFrameDelete``. L'esempio di sopra potrebbe essere scritto anche così:

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.Bind(wx.EVT_CLOSE, self.on_close)

        def on_close(self, evt):
            wx.CallAfter(wx.GetApp().create_new_toplevel)
            self.Destroy()
                
    class MyApp(wx.App):
        def OnInit(self):
            MyFrame(None, title='PRIMA GENERAZIONE').Show()
            return True
        
        def create_new_toplevel(self):
            MyFrame(None, title='SECONDA GENERAZIONE!!').Show()
        
    app = MyApp(False)
    app.MainLoop()

Naturalmente questo lascia aperto il problema di capire come terminare, a un certo punto, la ``wx.App``. Ma non è un problema enorme. Si potrebbe aggiungere un test nel gestore ``on_close``, in modo da chiamare ``wx.CallAfter`` una volta sola. Oppure si potrebbe chiamare ``wx.Exit()``... 

Ma questo è appunto l'argomento del prossimo paragrafo.


Altri modi di terminare la ``wx.App``.
--------------------------------------

sdfdfsdgf

