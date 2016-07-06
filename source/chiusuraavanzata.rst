.. _chiusura_avanzata:

.. index::
   single: wx.EVT_CLOSE
   single: eventi; wx.EVT_CLOSE
   single: wx.Window; Close
   single: wx.Window; Destroy
   single: chiusura; wx.Window.Close
   single: chiusura; wx.Window.Destroy
   single: chiusura; di finestre a cascata


Chiudere i widget: aspetti avanzati.
====================================

Questa pagina riprende il discorso :ref:`sulla chiusura dei widget<chiusura>`, esaminando alcuni scenari che si verificano di rado ma che è meglio conoscere per evitare sorprese. 

Anche se in questa pagina non facciamo esempi espliciti, è chiaro che alcuni comportamenti che descriviamo potrebbero, in determinate circostanze, innescare dei ``wx.PyDeadObjectError``: vi conviene quindi leggere anche :ref:`la pagina sulle eccezioni wxPython<eccezioni2>` subito dopo o subito prima di questa. 


Distruzione di finestre a cascata.
----------------------------------

Quando chiudete una finestra, naturalmente wxPython distrugge a cascata anche tutti i widget "figli" nella :ref:`catena dei parent<catenaparent>`. Attenzione però: non solo i pulsanti, caselle di testo etc. dentro la finestra, ma anche eventuali altre finestre figlie di quella che state chiudendo. 

Ma qui c'è una trappola: la distruzione di tutti i widget figli (e quindi anche delle finestre figlie) avviene chiamando direttamente ``wx.Window.Destroy``, e non il più gentile ``wx.Window.Close``. Dopo :ref:`aver visto tutte le complicate sottigliezze<chiusura>` legate a ``wx.Window.Close``, probabilmente capirete perché wxPython sceglie di tagliar corto: preferisce assicurarsi che, per esempio, quando l'utente chiude la finestra "top level" il programma termini davvero, senza rimanere impigliato in qualche veto proveniente da finestre secondarie aperte magari solo per dimenticanza. 

Tuttavia, questa procedura sbrigativa rischia di saltare qualche importante passaggio nelle vostre operazioni di chiusura. Ecco un esempio pratico di quello che potrebbe succedere::

    class ChildFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.Bind(wx.EVT_CLOSE, self.on_close)

        def on_close(self, evt):
            evt.Skip()
            print 'sono ' + self.GetTitle() + ' e mi sto chiudendo!'


    class MainFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.SetTitle('FINESTRA PRINCIPALE')
            child = ChildFrame(self)
            child.SetTitle('FINESTRA FIGLIA')
            child.Show()


    if __name__ == '__main__':
        app = wx.App(False)
        MainFrame(None).Show()
        app.MainLoop()

Quando chiudete la finestra figlia, il ``wx.EVT_CLOSE`` viene generato e intercettato regolarmente. Ma quando invece chiudete direttamente la finestra principale, questo non succede perché la finestra figlia viene distrutta con ``wx.Window.Destroy``. 

wxPython vi offre quindi un comportamento di default ragionevole ma sbrigativo: nella maggior parte dei casi è sufficiente, ma quando invece avete la necessità di garantire la corretta procedura di chiusura delle finestre figlie, non vi resta che intercettare il ``wx.EVT_CLOSE`` della finestra principale, e intervenire voi stessi. La strategia esatta dipende dall'architettura del vostro programma. Ecco una traccia molto semplificata::

    class ChildFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.Bind(wx.EVT_CLOSE, self.on_close)
            self.SetTitle('FINESTRA ' + str(self.GetId()))

        def on_close(self, evt):
            evt.Skip()
            print 'sono ' + self.GetTitle() + ' e mi sto chiudendo!'
            self.GetParent().child_list.remove(self)


    class MainFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            b = wx.Button(p, -1, 'genera figlio', pos=(20, 20))
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            self.Bind(wx.EVT_CLOSE, self.on_close)
            self.SetTitle('FINESTRA PRINCIPALE')
            self.child_list = []

        def on_clic(self, evt):
            child = ChildFrame(self)
            self.child_list.append(child)
            child.Show()

        def on_close(self, evt):
            evt.Skip()
            for child in self.child_list[:]:
                child.Close()
            
Beninteso, in un'applicazione vera avrete bisogno di una strategia meno rudimentale (probabilmente un :ref:`sistema di messaggistica pub/sub<pubsub>` in un'architettura MVC). Ma qui il punto importante è che abbiamo intercettato il ``wx.EVT_CLOSE`` della finestra principale per impedire a wxPython di distruggere sbrigativamente le finestre figlie. Invece, chiamiamo manualmente ``wx.Window.Close`` su tutte le finestre figlie ancora aperte, garantendo così l'esecuzione dei callback con le operazioni di chiusura. 


Trappole legate alla distruzione dei widget.
--------------------------------------------

Specialmente quando wxPython distrugge i widget a cascata, il momento esatto della distruzione di ciascuno non è garantito, e in linea di principio non dovreste cercare di intervenire troppo nel processo di distruzione. 


.. index::
   single: chiusura; wx.Window.IsBeingDeleted
   single: wx.Window; IsBeingDeleted

La differenza tra ``Close`` e ``Destroy``.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

La chiusura di una finestra è un evento importante, al quale spesso desiderate reagire in qualche modo. wxPython mette a disposizione un hook ben preciso per questo scopo, ed è ``wx.Window.Close``. La chiamata a questo metodo (causata dal vostro codice, o dall'utente che fa clic sul pulsante di chiusura), provoca l'emissione di un ``wx.EVT_CLOSE`` che potete intercettare: :ref:`abbiamo anche visto<chiusura>` che molti virtuosismi sono possibili durante questa fase. 

In ogni caso, finché si resta allo stadio di ``wx.Window.Close``, la finestra è ancora "in vita", stabile e pronta per essere usata. Per esempio, se nel callback del ``wx.EVT_CLOSE`` volete prelevare il contenuto di una casella di testo nella finestra, potete farlo senza timore che nel frattempo sia già stata distrutta. 

Le cose cambiano non appena si chiama ``wx.Window.Destroy`` (cosa che avviene automaticamente nel gestore di default del ``wx.EVT_CLOSE``, se voi non stabilite diversamente). Da questo momento, la finestra entra in una fase transitoria, e non ne viene garantito il normale funzionamento: wxPython procede a distruggere tutti i suoi figli chiamando direttamente ``wx.Window.Destroy`` su ciascuno di essi. In questa fase, di regola non viene emesso nessun evento che possiate intercettare: wxPython fa tutto da solo, ed è saggio non cercare di intromettersi nel processo. 

Potete verificare se una finestra è sul punto di essere distrutta testando ``wx.Window.IsBeingDeleted``: se ottenete ``True``, dovreste considerarla ormai perduta, anche se potreste ancora accedere a certe sue proprietà. In wxWidgets, dove è possibile manipolare più da vicino il processo di distruzione, questo strumento è spesso necessario. In wxPython la sua utilità è molto ridotta, ma vedremo alcuni esempi in cui può ancora servire.


Eventi da oggetti in fase di distruzione.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

La distruzione di una finestra, in wxPython, non è un evento né immediato, né "atomico". La chiamata a ``wx.Window.Destroy`` imposta un flag testabile con ``wx.Window.IsBeingDeleted``, e programma il widget per la distruzione. Il processo di distruzione avviene in momenti successivi. wxPython utilizza le pause del suo main loop (ovvero, i cicli di ``wx.EVT_IDLE`` successivi), in modo da essere certo che nessun evento resti in coda da processare quando procede con la distruzione. Ma la distruzione completa di una finestra può richiedere diversi cicli di questo tipo. 

Tra il momento in cui ``wx.Window.Destroy`` viene chiamato e il momento in cui anche l'ultimo "pezzo" della finestra è effettivamente distrutto, è possibile avere il tempo per fare qualcosa di sbagliato? Di regola, no. Però dove c'è una regola, c'è anche un'eccezione. 

Per esempio immaginate che, nel corso della sua distruzione, il widget abbia il tempo di :ref:`postare un evento<eventi_personalizzati>` nella coda: l'evento farebbe riferimento a un oggetto la cui esistenza è... discutibile. Se un callback intercettasse l'evento e chiamasse per esempio ``wx.Event.GetEventObject``, non è chiaro che cosa potrebbe succedere. Forse state pensando di scrivere voi stessi una trappola di questo tipo, per esempio estendendo ``wx.Window.Destroy`` in una sotto-classe. Qualcosa come questo::

    # questo NON funziona davvero come immaginate...
    class MyButton(wx.Button):
        def Destroy(self):
            wx.PostEvent(.....)
            # fatto il danno, procedo a distruggere il widget normalmente
            wx.Button.Destroy(self)

Purtroppo o forse per fortuna questo codice non fa proprio quello che vi aspettate. Il fatto è che non potete semplicemente sovrascrivere il proxy Python (in wxPython) di un metodo virtuale C++ (in wxWidgets), e sperare di aver sovrascritto anche l'originale. E così, se provate a implementare l'esempio qui sopra, otterrete due comportamenti differenti: 

1) quando chiamate ``MyButton.Destroy`` dal vostro codice Python, allora sicuramente la vostra versione di ``Destroy`` verrà eseguita;

2) quando invece wxWidgets chiama internamente ``wxWindow::Destroy`` per distruggere il pulsante (magari perché l'utente ha chiuso la finestra che lo contiene), allora verrà eseguito il codice C++ sottostante, e il vostro ``MyButton.Destroy`` sarà completamente ignorato.  

.. todo:: una pagina su SWIG e l'oop Python/C++.

Anche se wxPython vi impedisce di percorrere il sentiero più pericoloso, non è comunque difficile trovarsi in situazioni imbarazzanti. Proviamo a implementare concretamente la nostra idea::

    import wx.lib.newevent
    TestEvent, EVT_TEST = wx.lib.newevent.NewCommandEvent()

    class MyButton(wx.Button):
        def __init__(self, *a, **k):
            wx.Button.__init__(self, *a, **k)
            self.Bind(wx.EVT_BUTTON, self.on_clic)

        def on_clic(self, evt):
            event = TestEvent(self.GetId())
            wx.PostEvent(self.GetEventHandler(), event)

        def Destroy(self):
            event = TestEvent(self.GetId())
            wx.PostEvent(self.GetEventHandler(), event)
            return wx.Button.Destroy(self)


    class MainFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            self.test = MyButton(p, -1, 'test', pos=(20, 20))
            b = wx.Button(p, -1, 'distruggi test', pos=(20, 60))
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            self.Bind(EVT_TEST, self.on_evt_test)

        def on_evt_test(self, evt):
            print 'EVT_TEST emesso da ', evt.GetId()

        def on_clic(self, evt):
            self.test.Destroy()

Adesso ``MyButton`` emette l'evento anche in risposta al clic (solo per consentirci di testarlo), e il frame principale lo intercetta. Abbiamo già capito che l'evento non verrà emesso quando wxWidgets distruggerà il pulsante al momento di chiudere la finestra. Tuttavia ci aspettiamo di vedere l'evento quando siamo noi a distruggere manualmente il pulsante chiamando ``self.test.Destroy()`` nel nostro codice. E invece no: sicuramente il nostro codice viene eseguito, e possiamo vedere che in effetti il pulsante si distrugge; tuttavia non riusciamo a intercettare l'evento. Il motivo, in questo caso, è che ``wx.PostEvent`` :ref:`posta l'evento nella coda<lanciare_evento_personalizzato>` senza processarlo immediatamente. Subito dopo il widget viene distrutto: siccome però il primo handler dell'evento è il widget stesso, quando viene il momento di processare l'evento l'handler non si trova più. Volendo, possiamo assegnare all'evento un primo handler differente, per esempio il suo parent (che nel nostro esempio è il panel della finestra principale)::

    wx.PostEvent(self.GetParent().GetEventHandler(), event)

Oppure possiamo usare ``wx.EvtHandler.ProcessEvent`` (invece di ``wx.PostEvent``) per processare immediatamente l'evento::

    self.GetEventHandler().ProcessEvent(event)

Entrambe le tecniche funzionano ma sono spericolate e potrebbero avere effetti collaterali indesiderati. 

Emettere eventi da un widget in fase di distruzione è certamente uno scenario molto raro. In ogni caso il punto dovrebbe essere chiaro: non è mai conveniente maneggiare direttamente ``wx.Window.Destroy``. Quando volete reagire alla chiusura di un widget, usate piuttosto ``wx.Window.Close`` e il relativo ``wx.EVT_CLOSE``. 


.. _trappole_chiusura:

Esempi di trappole che potreste incontrare davvero.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In alcuni casi potreste davvero incontrare delle situazioni simili a quella descritta sopra: approfondiamo adesso un paio di esempi rari ma relativamente ben conosciuti. L'importante è imparare a riconoscere il pattern, nel caso doveste imbattervi in situazioni analoghe. 

``wx.TreeCtrl`` serve a visualizzare strutture ad albero. In ambiente Windows wxPython utilizza il widget nativo, mentre sulle altre piattaforme ripiega su un widget generico. ``wx.TreeCtrl`` emette, tra gli altri, un evento ``wx.EVT_TREE_SEL_CHANGED`` ogni volta che l'utente seleziona un diverso elemento dell'albero. Quando wxPython deve distruggere questo widget, per prima cosa procede a eliminare il contenuto, un elemento alla volta; fatto questo, distrugge il widget vero e proprio. Ora, ecco il problema: il widget nativo di Windows, quando viene distrutto un elemento dell'albero che in quel momento è selezionato, provvede a spostare la selezione sull'elemento più vicino, e naturalmente per questo emette un ``wx.EVT_TREE_SEL_CHANGED``. Quando wxPython svuota completamente l'albero, nel processo di distruzione, questo fenomeno di solito passa inosservato: infatti, siccome in genere l'albero ha una sola radice e lo svuotamento procede dalla radice alle foglie, una volta eliminata la radice non esiste più un elemento valido su cui spostare la selezione. 

Ma se invece il vostro albero ha più di una radice... Allora si verifica un fenomeno bizzarro: la distruzione del widget provoca una raffica di ``wx.EVT_TREE_SEL_CHANGED``, in numero variabile a seconda di quante radici ci sono, e quale elemento era selezionato al momento della distruzione. Un esempio chiarirà forse meglio::

    # ricordate, questo effetto si vede solo in Windows!
    class MyFrame(wx.Frame): 
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.tree = wx.TreeCtrl(self, 
                                    # TR_HIDE_ROOT per avere molte radici
                                    style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
            root = self.tree.AddRoot('')
            for i in range(10):
                item = self.tree.AppendItem(root, 'nodo %d' % i)
            self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
            # in alternativa, provate anche:
            # self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
            self.Refresh() # adatta il widget alla finestra

        def on_sel_changed(self, evt):
            print "Selezione cambiata: ", self.tree.GetItemText(evt.GetItem())

Quando chiudete la finestra, vedrete la traccia di una serie di eventi: noterete che lo svuotamento procede dell'alto verso il basso, spingendo quindi verso il basso l'elemento selezionato che produce l'evento. Come risultato, avete più eventi se selezionate un elemento alto della lista, e ne avete di meno se selezionate un elemento basso. 

Una ulteriore complicazione: se invece di collegare il ``wx.TreeCtrl`` al suo evento, collegate la finestra-madre (quindi: ``self.Bind(...)`` invece di ``self.tree.Bind(...)``), il risultato cambia drasticamente. Questa volta, al momento della chiusura, nessun evento sarà intercettato: questo perché l'event handler (ovvero la finestra stessa) si trova in quel momento in una fase abbastanza avanzata della distruzione da non poter più operare. 

Questo, naturalmente, è uno scenario abbastanza inconsueto: dovete essere su Windows; usare un ``wx.TreeCtrl``; avere un albero con più radici; intercettare ``wx.EVT_TREE_SEL_CHANGED``; e infine, beninteso, dovete mettere nel callback del codice "sensibile", che può effettivamente combinare dei guai (scritture sul database, etc.) quando viene eseguito a sproposito. 

Se però siete proprio in questa condizione, niente panico. La soluzione è semplicissima: basta testare ``wx.Window.IsBeingDeleted`` e non eseguire il callback proprio quando la finestra sta per essere distrutta::

    def on_sel_changed(self, evt):
        if not self.IsBeingDeleted():
            print "Selezione cambiata: ", self.tree.GetItemText(evt.GetItem())

Vediamo un altro esempio molto simile, ma dalle conseguenze ancora più drammatiche. ``wx.GenericDirCtrl`` è un pratico widget che visualizza automaticamente il vostro file system. Per fare questo, naturalmente al suo interno utilizza un ``wx.TreeCtrl`` (ops). E naturalmente su Windows il file system può avere più di una radice (ops!)... Avete già capito il problema::

    # anche qui, l'effetto si vede solo in Windows
    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            self.dirctrl = wx.GenericDirCtrl(self)
            self.dirctrl.Path = 'c:'
            # "self.dirctrl.TreeCtrl" e' il wx.TreeCtrl interno
            self.dirctrl.TreeCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
     
        def on_sel_changed(self, evt):
            print self.dirctrl.Path

Se siete su una tipica macchina Windows, probabilmente avrete almeno due unità (``c:`` e ``d:``, in genere) che costituiscono altrettante radici del file system. Durante la fase di chiusura, viene emesso un ``wx.EVT_TREE_SEL_CHANGED`` spurio: il callback relativo cerca di accedere alla proprietà ``wx.GenericDirCtrl.Path``; questo provoca un tentativo di accesso a un elemento del ``wx.TreeCtrl`` interno, che però in quel momento non è accessibile; e questo, a sua volta, provoca un clamoroso crash del programma! 

Notate che non sempre il programma va in crash. Le due radici vengono distrutte in ordine (prima ``c:``, poi ``d:``), e se voi avevate selezionato un elemento dell'albero ``d:`` al momento di chiudere la finestra, tutto fila liscio: quando ``d:`` viene svuotato, non ci sono altri elementi su cui spostare la selezione. In ogni caso, anche questa volta la soluzione è semplicissima::

    def on_sel_changed(self, evt):
        if not self.IsBeingDeleted():
            print self.dirctrl.Path

Ci sono forse altri esempi del genere, nascosti nel gran numero di widget che wxPython mette a disposizione. Per esempio ``wx.Treebook`` emette un suo specifico evento ``wx.EVT_TREEBOOK_PAGE_CHANGED``, che non è soggetto a questo problema... almeno fin quando non avete bisogno di personalizzare il suo comportamento al punto da accedere direttamente al suo ``wx.TreeCtrl`` interno... e allora, naturalmente, sapete che cosa potrebbe aspettarvi. 

L'importante, in ogni caso, è rendersi conto del principio generale: la chiusura dei widget è un processo delicato nel quale sarebbe meglio non intervenire. Se però vi trovate in circostanze eccezionali, nel dubbio ``wx.Window.IsBeingDeleted`` è sempre pronto per voi. 
