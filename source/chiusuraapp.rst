.. _chiusuraapp:

.. highlight:: python
   :linenothreshold: 7

.. index::
   single: wx.App
   single: wx.App; MainLoop
   single: wx.App; OnExit
   single: wx.Window; Close
   single: wx.EVT_CLOSE
   single: chiusura; di una wx.App
   single: wx.App; chiusura
   single: eventi; wx.EVT_CLOSE
   
Terminare la ``wx.App``.
========================

In questa sezione analizziamo ciò che succede quando la ``wx.App`` termina, e con essa la nostra applicazione wxPython. Il discorso prosegue direttamente :ref:`da questa pagina <chiusura>`, che forse vi conviene leggere prima.


La chiusura "normale".
----------------------
          
La storia semplice è questa: quando il ``MainLoop`` percepisce che anche l'ultima :ref:`finestra "top level" <finestre_toplevel>` è stata chiusa, allora decide che il suo lavoro è terminato. Una volta usciti dal ``MainLoop``, c'è ancora l'opportunità di fare qualche operazione di pulizia nel ``wx.App.OnExit``, :ref:`come abbiamo già visto <wxapp_avanzata_onexit>`. Tuttavia non è più possibile, a questo punto, creare una nuova finestra e tenere in vita la ``wx.App``, il cui destino è ormai segnato. Terminato il ``wx.App.OnExit``, la nostra applicazione defunge definitivamente. Dentro il namespace del modulo Python resta ovviamente ancora un riferimento nel nome ``app`` (o quello che avete usato per istanziare la ``wx.App``), ma ormai non ha più alcuna utilità. 

Questa è la storia semplice. Ma ovviamente avete ancora molti modi per complicarvi la vita. 

Per prima cosa, ricordiamo che la ``wx.App`` termina una volta che *tutte* le :ref:`finestre top-level <finestre_toplevel>` sono state chiuse, ovvero tutte le finestre che hanno ``parent=None``, come abbiamo già visto. Quindi fate attenzione a non lasciare qualche finestra top-level nascosta ma ancora viva. I casi tipici sono due: avete creato qualche dialogo top-level e non l'avete mai distrutto esplicitamente (ricordiamo che chiamare ``Close()`` su un dialogo :ref:`lo nasconde ma non lo distrugge <chiusura>`). Oppure, avete creato la ``wx.App`` con l'opzione ``redirect=True``, e la finestra dello streaming output è ancora viva ma nascosta per qualche ragione (forse perché, per tutta la durata della vostra applicazione, non c'è stato niente da scrivere sullo streaming!). In questi casi, l'utente chiude il frame "principale", ma la ``wx.App`` *non termina davvero*. Forse pensate che questo non è un grande problema: l'utente ha comunque finito di interagire con la gui, e prima o poi spegnerà il computer... Ma se invece riavvia e poi "chiude" un po' di volte il programma, ben presto si troverà la memoria intasata dalle vostre istanze fantasma. 

E c'è dell'altro: se avete scritto qualcosa nel ``wx.App.OnExit``, *non verrà mai eseguito*, perché non si esce mai dal ``MainLoop``. Inutile dire che, se questo codice comprende operazioni di assestamento dei dati nel database, o delle scritture nel log, queste non verranno eseguite, e la prossima volta che si aprirà il programma ci si troverà con dati inconsistenti. 

Quindi fate sempre molta attenzione a non creare finestre top-level e poi lasciarle in giro senza sapere se ci sono ancora o no. Una strategia di emergenza è catturare il ``wx.EVT_CLOSE`` della finestra "principale" e, prima di distruggerla, verificare che non ci siano altre finestre top-level ancora in vita (``wx.GetTopLevelWindows`` torna utile), ed eventualmente chiuderle. Anche in questo caso però fate attenzione perché non è detto che chiamare ``Close()`` basti a garantire la distruzione (abbiamo già visto perché :ref:`in un'altra pagina <chiusura_forzata>`). La soluzione più brutale è chiamare direttamente ``Destroy()``, più o meno così::
    
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

Ovviamente non sono ipotesi frequenti. Devo dire di non aver mai usato, in pratica, un metodo come questo per accertarmi che tutte le finestre top-level siano chiuse al momento di uscire dall'applicazione. E francamente vi sconsiglio di provarci. 

**La soluzione corretta** è invece *tenere sempre traccia* di tutte le finestre che aprite, soprattutto quelle top-level, e di accertarvi sempre di chiuderle appena non servono più. In questo modo, quando arriva il momento di chiudere anche l'ultima finestra principale, siete sicuri che anche la ``wx.App`` terminerà la sua vita correttamente.

E' opportuno ricordare che l'eventuale non-terminazione della ``wx.App`` non deve essere considerata come un'eventualità da gestire, ma come un vero e proprio baco da correggere. 

.. index::
   single: wx.App; SetExitOnFrameDelete
   single: wx.CallLater
   single: wx.CallAfter
   single: chiusura; wx.App.SetExitOnFrameDelete
   
Come mantenere in vita la ``wx.App``.
-------------------------------------

Ma c'è ancora dell'altro da sapere. Potrebbe capitarvi di *non* volere che la ``wx.App`` termini, ma che invece il suo ``MainLoop`` resti attivo anche dopo che l'ultima finestra è stata chiusa. 

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

Notate l'utilizzo di ``wx.CallLater``, che aspetta un certo periodo (in questo caso, 1 ms, il minimo possibile) e poi chiama una funzione. Lo abbiamo scelto perché ``wx.CallLater`` non tiene impegnato il ``MainLoop``, e quindi ci serve a dimostrare che il ``MainLoop`` resta vivo comunque, per altri motivi (ossia, perché abbiamo settato il flag a ``False``). 

Avremmo potuto invece usare ``wx.CallAfter``, che è "quasi uguale", nel senso che chiama una data funzione dopo che tutti i gestori degli eventi correnti sono stati processati. Il punto però è che ``wx.CallAfter`` aggiunge la sua funzione in coda ai compiti del ``MainLoop``, e quindi lo tiene impegnato almeno fino a quel momento. E siccome nel nostro caso la funzione chiamata è ``create_new_toplevel`` che appunto crea una nuova finestra top-level, in sostanza il ``MainLoop`` non ha mai modo di terminare, indipendentemente da come è stato settato il flag ``SetExitOnFrameDelete``. 

Provate a sostituire la riga 7 dell'esempio precedente con::

    wx.CallAfter(wx.GetApp().create_new_toplevel)

Quando si distrugge la "prima generazione" compare la seconda, come previsto. Ma quando provate a distruggere anche questa, la ``wx.App`` non termina come prima, anche se il flag è ormai impostato a ``True``. Invece, ogni volta appare una nuova "seconda generazione", all'infinito. Questo perché ``wx.CallAfter`` tiene in vita il ``MainLoop`` fino al momento di chiamare ``create_new_toplevel``, dove però si crea una nuova finestra top-level, e quindi il ``MainLoop`` trova un'altra ragione per proseguire la sua attività, all'infinito. 

In altri termini ``wx.CallAfter``, usato così, potrebbe essere un'altra strada per non far terminare il ``MainLoop``, senza dover usare ``SetExitOnFrameDelete``. L'esempio di sopra potrebbe essere scritto anche così::

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

Naturalmente questo lascia aperto il problema di capire come terminare, a un certo punto, la ``wx.App``. Ma non è un problema enorme. Si potrebbe aggiungere un test nel callback ``on_close``, in modo da chiamare ``wx.CallAfter`` una volta sola. Oppure si potrebbe chiamare ``wx.Exit()``... 

Ma questo è appunto l'argomento del prossimo paragrafo.

.. _wxexit:

.. index::
   single: wx.Exit
   single: wx.App; ExitMainLoop
   single: chiusura; wx.Exit
   single: chiusura; wx.App.ExitMainLoop

Altri modi di terminare la ``wx.App``.
--------------------------------------

Ci sono almeno altri due modi per terminare una ``wx.App``, entrambi sconsigliati nella pratica, ma utili da conoscere come ultima risorsa. 

Il primo è chiamare ``wx.GetApp().Exit()`` (oppure la scorciatoia equivalente ``wx.Exit()``). Questo termina immediatamente il ``MainLoop``. Funziona, e lascia anche il tempo di eseguire il codice eventualmente contenuto in ``wx.App.OnExit``. Però chiude tutte le finestre top-level *senza generare* ``wx.EVT_CLOSE``. Quindi, qualsiasi codice di pulizia potevate aver scritto in risposta alla chiusura della finestra, verrà saltato. 

Il secondo è chiamare ``wx.GetApp().ExitMainLoop()``. Questo si comporta come ``Exit()``, ma è un po' più gentile, perché aspetta che il ciclo corrente del ``MainLoop`` sia terminato prima di uscire. Da un lato, questo significa la garanzia che gli eventi ancora pendenti saranno gestiti. Dall'altro, vuole anche dire che non c'è garanzia che il programma sarà terminato proprio immediatamente. 


