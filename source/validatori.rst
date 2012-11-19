.. highlight:: python
   :linenothreshold: 15
   
.. _validatori:

.. index::
   single: validatori

Validatori: prima parte.
========================

La validazione dei dati è un processo delicato. wxPython vi viene incontro con uno strumento apposito, la classe ``wx.PyValidator`` ("validatore" per gli amici), che ha delle funzionalità interessanti, ma che non è facile comprendere bene. 

I validatori in wxPython servono a due cose complementari:

* convalidano i dati;
* trasferiscono i dati dentro e fuori da un dialogo. 

Potete usare i validatori anche solo per una di queste due funzioni, o per entrambe, a vostro gusto. Noi dedichiamo questa sezione a spiegare la funzione di validazione, e :ref:`un'altra pagina <validatoridue>` per il trasferimento dei dati. 

.. note:: se avete un editor con l'autocompletion, a quest'ora avrete probabilmente già scoperto che esiste anche la più "normale" classe ``wx.Validator``. Voi però dovete sempre usare la "versione python" ``wx.PyValidator``. La ragione della presenza di questi doppioni è complessa, e le dedicheremo una pagina separata. Affidatevi sempre a ``wx.PyValidator``, è tutto quello che vi serve sapere per usare bene i validatori.

.. todo:: una pagina sui pycontrols

.. index::
   single: wx; PyValidator()
   single: PyValidator; Clone()
   single: PyValidator: Validate()
   single: validatori; validazione a cascata

Come scrivere un validatore.
----------------------------

Occorre semplicemente sottoclassare ``wx.PyValidator``. Ecco un esempio da manuale: questo è un validatore che si può applicare a una casella di testo, e che garantisce che l'utente non la lasci vuota::

    class NotEmptyValidator(wx.PyValidator):
        def Clone(self): return NotEmptyValidator()
        def TransferToWindow(self): return True
        def TransferFromWindow(self): return True
        
        def Validate(self, ctl):
            win = self.GetWindow()
            val = win.GetValue().strip()
            if val == '':
                return False
            else:
                return True
            
Le righe 2, 3, 4 sono (purtroppo) boilerplate necessario. ``Clone`` deve esserci necessariamente, e deve restituire una istanza dello stesso validatore. I due ``Tranfer*`` servono solo se intendete usare il validatore per trasferire dati: tuttavia dovete comunque sovrascriverli e restituire ``True``, altrimenti wxPython emette un warning. 

La parte interessante è ``Validate``: sovrascrivete questo metodo per fare la vostra validazione. ``Validate`` deve restituire ``True`` se la validazione ha successo, ``False`` altrimenti. Notate anche (riga 7) che all'interno del validatore, potete risalire a un'istanza del widget che state validando, chiamando ``GetWindow``. Forse pensate che il secondo, necessario, parametro di ``Validate`` (``ctl`` nel nostro esempio) abbia già un riferimento al widget validato, ma questo potrebbe non essere vero in caso di validazioni "a cascata", come il nostro esempio dimostrerà tra non molto. Quindi il modo più sicuro è usare  sempre ``GetWindow``. 

Il costruttore di un validatore, di norma, non prende argomenti. Tuttavia niente vi impedisce di passagli degli argomenti extra, se necessario. Per esempio, questo validatore garantisce che il valore immesso non sia in una bad-list di parole proibite::

    class NotInBadListValidator(wx.PyValidator):
        def __init__(self, badlist):
            wx.PyValidator.__init__(self)
            self._badlist=badlist
        
        def Clone(self): return NotInBadListValidator(self._badlist)
        def TransferToWindow(self): return True
        def TransferFromWindow(self): return True
        
        def Validate(self, ctl):
            win = self.GetWindow()
            val = win.GetValue().strip()
            if val in self._badlist:
                return False
            else:
                return True

Chiaramente, in questo caso volete sovrascrivere anche l'``__init__`` per gestire i paramentri aggiuntivi. Non dimenticatevi di riportare gli argomenti correttamente anche in ``Clone`` (riga 6)... anche il boiledplate vuole un minimo di attenzione. 

Una volta scritto, il validatore si applica al widget che intendete validare, al momento della sua creazione, passandolo direttamente come parametro ``validator`` del costruttore. Ovviamente potete usare lo stesso validatore (cioè: diverse istanze dello stesso validatore) per validare più widget, se ne avete bisogno. Ecco un esempio::

    class YourNamePanel(wx.Panel):
        def __init__(self, *a, **k):
            wx.Panel.__init__(self, *a, **k)
            self.first_name = wx.TextCtrl(self, validator=NotEmptyValidator())
            self.family_name = wx.TextCtrl(self, validator=NotEmptyValidator())
            self.year = wx.SpinCtrl(self)
            
            s = wx.FlexGridSizer(3, 2, 5, 5)
            s.AddGrowableCol(1)
            s.Add(wx.StaticText(self, -1, 'nome:'), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.first_name, 1, wx.EXPAND)
            s.Add(wx.StaticText(self, -1, 'cognome:'), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.family_name, 1, wx.EXPAND) 
            s.Add(wx.StaticText(self, -1, "eta':"), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.year, 1, wx.EXPAND) 
            self.SetSizer(s)
            s.Fit(self)

    class MyTopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            self.your_name = YourNamePanel(p)
            validate = wx.Button(p, -1, 'valida')
            validate.Bind(wx.EVT_BUTTON, self.on_validate)
            
            s = wx.BoxSizer(wx.VERTICAL)
            s.Add(self.your_name, 1, wx.EXPAND)
            s.Add(validate, 0, wx.EXPAND|wx.ALL, 5)
            p.SetSizer(s)
            
        def on_validate(self, evt):
            ret = self.your_name.Validate()
            if ret == False:
                wx.MessageBox('Non valido')
            
            
    app = wx.App(False)
    MyTopFrame(None, size=(200, 200)).Show()
    app.MainLoop()

Come si vede (righe 4 e 5) due caselle di testo sono legate al nostro validatore, mentre la terza casella non viene mai validata. Se preferite, potete testare anche l'altro validatore. Cambiate la riga 4 con qualcosa come::

    ugly_names = ('Cunegonda', 'Dagoberto', 'Emerenzio', 'Pancrazia')
    self.first_name = wx.TextCtrl(self, validator=NotInBadListValidator(ugly_names))

Abbiamo incorporato le tre caselle in un panel in parte perché è buona pratica raggruppare le funzionalità della gui in piccoli "mattoni" coerenti da combinare, :ref:`come abbiamo già detto altrove <wxpanel>`. Però in questo caso il panel ci torna utile anche per dimostrare la validazione "a cascata": quando chiamiamo ``Validate`` sul panel (riga 33), in effetti vengono validati tutti i widget figli del panel (purché abbiano un validatore associato, naturalmente). ``Validate`` chiamato sul panel restituisce ``True`` solo se tutti i figli passano la validazione, ``False`` altrimenti. 

.. index::
   single: validatori; validazione a cascata
   
Quando fallisce una validazione a cascata.
------------------------------------------

Nel caso di validazione a cascata, abbiamo però un problema aggiuntivo: il processo di validazione si ferma non appena uno dei test fallisce, ma il valore restituito ``False`` non ci dice nulla su quale widget esattamente non ha superato la validazione. 

Quando è necessario dare all'utente anche questa informazione, occorre far sì che sia il validatore stesso a occuparsene, invece del codice chiamante (perché il codice chiamante si ritrova in mano solo un ``False``, alla fine). Per esempio, possiamo riscrivere il nostro ``NotEmptyValidator`` in questo modo::

    class NotEmptyValidator(wx.PyValidator):
        #Clone, TransferToWindow, TransferFromWindow... bla bla 
        
        def Validate(self, ctl):
            win = self.GetWindow()
            val = win.GetValue().strip()
            if val == '':
                wx.MessageBox('Bisogna inserire del testo')
                return False
            else:
                return True

Questo però non è ancora sufficiente: se più caselle di testo hanno lo stesso validatore, talvolta si vuole sapere esattamente quale non funziona (in questo caso forse è banale per l'utente capire dove non c'è testo, ma pensate al caso generale). Possiamo fare in molti modi, per esempio modificando anche il colore del widget incriminato::

    class NotEmptyValidator(wx.PyValidator):
        #Clone, TransferToWindow, TransferFromWindow... bla bla 
        
        def Validate(self, ctl):
            win = self.GetWindow()
            val = win.GetValue().strip()
            if val == '':
                win.SetBackgroundColour('yellow')
                win.Refresh() # necessario...
                wx.MessageBox('Bisogna inserire del testo')
                return False
            else:
                # resettiamo il colore normale
                win.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
                win.Refresh() 
                return True

In questo caso però ci fidiamo che il nostro widget abbia un'interfaccia ``SetBackgroundColour``, cosa che per un ``wx.TextCtrl`` è senz'altro vera, ma di nuovo, dovete pensare al caso generale. 

Un'altra soluzione potrebbe essere per esempio recuperare il ``name`` del widget::

    class NotEmptyValidator(wx.PyValidator):
        #Clone, TransferToWindow, TransferFromWindow... bla bla 
        
        def Validate(self, ctl):
            win = self.GetWindow()
            val = win.GetValue().strip()
            if val == '':
                msg = '%s: manca del testo!' % win.GetName()
                wx.MessageBox(msg)
                return False
            else:
                return True

Anche questo sistema si basa sulla fiducia: confida nel fatto che noi abbiamo assegnato un parametro ``name`` significativo a ogni widget a cui attribuiamo il validatore. Nel nostro esempio sarebbe::

    self.first_name = wx.TextCtrl(self, name='Nome', validator=NotEmptyValidator())
    self.family_name = wx.TextCtrl(self, name='Cognome', validator=NotEmptyValidator())

Il paramentro ``name`` del costruttore non è di solito molto utile. In Python si passano gli oggetti stessi come parametri, e questo rende superfluo contrassegnare ciascun widget con un identificativo statico da passare in giro tra le varie funzioni (abbiamo fatto lo stesso discorso :ref:`a proposito degli id <gli_id>`). Tuttavia, in casi del genere, è un modo veloce di aggiungere un "nickname" piacevole al widget, da presentare all'utente in caso di necessità. 

Il paramentro ``name`` (e quindi l'interfaccia ``GetName``) è sicuramente presente ovunque. Quindi, quale dei due sistemi sulla fiducia è il meno rischioso? Affidarsi a un'interfaccia che potrebbe non esistere (``SetBackgroundColour``) o a una che sicuramente esiste ma dipende da noi renderla significativa? La risposta sta al vostro stile, e alla dimensione del vostro progetto. Nelle situazioni più semplici, non dovete preoccuparvi in nessun caso. Se però iniziate a scrivere validatori "general purpose" e non sapete in anticipo a quali widget potrebbero essere assegnati, dovete muovervi con più cautela.           

.. index:: 
   single: validatori; validazione ricorsiva
   single: wx; WX_EX_VALIDATE_RECURSIVELY
   single: wx.Window; SetExtraStyle
   single: stili; extra-style
   
La validazione ricorsiva.
-------------------------

La validazione a cascata si limita in genere ai soli figli diretti, ma è possibile fare in modo che venga applicata ricorsivamente anche ai figli dei figli, e così via. Per fare questo occorre settare lo stile ``wx.WX_EX_VALIDATE_RECURSIVELY``. Questo :ref:`è un extra-style <extrastyle>`, e quindi va settato dopo la creazione, usando il metodo ``SetExtraStyle``. 

Facciamo degli esperimenti con il codice che abbiamo già scritto: per prima cosa, invece di validare il panel, proviamo a validare direttamente il frame. Alla riga 33, sostituite così::

    ret = self.Validate()  # era: ret = self.your_name.Validate()

Come previsto, la validazione non avviene. La :ref:`catena dei parent <catenaparent>` in effetti è molto lunga: dopo il frame c'è il panel contenitore (quello che istanziamo alla riga 22 e chiamiamo semplicemente ``p``), quindi l'istanza di ``YourNamePanel``, e finalmente le caselle di testo che vogliamo validare. 

Tuttavia, proviamo adesso ad aggiungere all'inizio dell'``__init__`` l'extra-style::

    # nell'__init__ di MyTopFrame, subito all'inizio:
    wx.Frame.__init__(self, *a, **k)
    self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)

Ed ecco che la validazione avviene di nuovo. 

.. index::
   single: wx; SetValidator()
   
``SetValidator``: cambiare il validatore assegnato.
---------------------------------------------------

Anche dopo che il widget è stato creato, potete assegnarli un validatore, chiamando su di esso ``SetValidator`` (attenzione: alcuni widget non dispongono di questo metodo). Se chiamate ``SetValidator`` su un widget che ha già un validatore, ogni volta l'ultimo sostituisce il precedente. 

.. index::
   single: validatori; validazione automatica
   single: dialoghi; con validazione automatica
   singe: wx; ID_OK
   
La validazione automatica dei dialoghi.
---------------------------------------

Fin qui ci siamo limitati a chiamare ``Validate`` manualmente, per effettuare la validazione. L'unico automatismo possibile è che, chiamandolo su un panel, si possono validare a cascata tutti i figli diretti (eventualmente anche i nipoti etc., usando la validazione ricorsiva). 

I :ref:`dialoghi <wxdialog>`, tuttavia, hanno una marcia in più. E' possible validare automaticamente un dialogo, se lo si fornisce di un apposito pulsante con id predefinito ``wx.ID_OK``. In questo caso, quando l'utente fa clic sul pulsante ``wx.ID_OK``, il dialogo chiama automaticamente ``Validate`` su se stesso, prima di chiudersi. Se i widget contenuti nel dialogo hanno dei validatori assegnati, entreranno in funzione. 

Abbiamo già parlato di questa feature dei dialoghi quando ci siamo occupati :ref:`degli Id in wxPython <validazione_automatica>`: la sezione relativa contiene degli esempi che vi invitiamo a rileggere.

Per quanto riguarda invece l'esempio che abbiamo seguito finora, ecco come diventerebbe se lo trasportassimo in un dialogo con validazione automatica::
    
    class NotEmptyValidator(wx.PyValidator):
        def Clone(self): return NotEmptyValidator()
        def TransferToWindow(self): return True
        def TransferFromWindow(self): return True
        
        def Validate(self, ctl):
            win = self.GetWindow()
            val = win.GetValue().strip()
            if val == '':
                msg = '%s: manca del testo!' % win.GetName()
                wx.MessageBox(msg)
                return False
            else:
                return True

    class NotInBadListValidator(wx.PyValidator):
        def __init__(self, badlist):
            wx.PyValidator.__init__(self)
            self._badlist=badlist
        
        def Clone(self): return NotInBadListValidator(self._badlist)
        def TransferToWindow(self): return True
        def TransferFromWindow(self): return True
        
        def Validate(self, ctl):
            win = self.GetWindow()
            val = win.GetValue().strip()
            if val in self._badlist:
                msg = '%s: non valido!' % win.GetName()
                wx.MessageBox(msg)
                return False
            else:
                return True
        
    class NameDialog(wx.Dialog):
        def __init__(self, *a, **k):
            wx.Dialog.__init__(self, *a, **k)
            ugly_names = ('Cunegonda', 'Dagoberto', 'Emerenzio', 'Pancrazia')
            self.first_name = wx.TextCtrl(self, name='Nome', 
                                          validator=NotInBadListValidator(ugly_names))
            self.family_name = wx.TextCtrl(self, name='Cognome',
                                           validator=NotEmptyValidator())
            self.year = wx.SpinCtrl(self)
            validate = wx.Button(self, wx.ID_OK, 'valida')
            cancel = wx.Button(self, wx.ID_CANCEL, 'annulla')
                               
            s = wx.FlexGridSizer(3, 2, 5, 5)
            s.AddGrowableCol(1)
            s.Add(wx.StaticText(self, -1, 'nome:'), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.first_name, 1, wx.EXPAND)
            s.Add(wx.StaticText(self, -1, 'cognome:'), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.family_name, 1, wx.EXPAND) 
            s.Add(wx.StaticText(self, -1, "eta':"), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.year, 1, wx.EXPAND) 

            s1 = wx.BoxSizer()
            s1.Add(validate, 1, wx.EXPAND|wx.ALL, 5)
            s1.Add(cancel, 1, wx.EXPAND|wx.ALL, 5)
            
            s2 = wx.BoxSizer(wx.VERTICAL)
            s2.Add(s, 1, wx.EXPAND|wx.ALL, 5)
            s2.Add(s1, 0, wx.EXPAND)
            self.SetSizer(s2)
            s2.Fit(self)

    class MyTopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            b = wx.Button(self, -1, 'mostra dialogo')
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            
        def on_clic(self, evt):
            dlg = NameDialog(self)
            ret = dlg.ShowModal()
            if ret == wx.ID_OK:
                print 'confermato'
            else:
                print 'annullato'
            dlg.Destroy()
            

    app = wx.App(False)
    MyTopFrame(None, size=(200, 200)).Show()
    app.MainLoop()

Alcune considerazioni preliminari. Ho scelto la tecnica di assegnare un ``name`` a ciascun widget (righe 39 e 41), e di usare l'interfaccia ``GetName`` nei validatori per distinguerli (righe 10, 29). Il panel ``YourNamePanel`` è andato via, a invece i widget da validare sono stati inseriti direttamente nel dialogo ``NameDialog``. Questo perché un dialogo :ref:`ha già un suo panel predisposto <wxdialog>` e quindi appoggiargli sopra un altro frame avrebbe rischiesto l'uso di ``wx.WX_EX_VALIDATE_RECURSIVELY`` per garantire la validazione automatica (che, ricordiamo, avviene chiamando ``Validate`` *sul dialogo stesso*). Infine, ho aggiunto un frame top-level ``MyTopFrame`` solo per esemplificare il modo di chiamare il dialogo e poi distruggerlo. 

Detto questo, passiamo alle cose più interessanti. Come abbiamo già visto :ref:`parlando degli Id <idpredefiniti>`, i due pulsanti "valida" e "annulla" (righe 44-45) sanno già che cosa fare, senza bisogno di collegarli a un evento. Entrambi tentano di chiudere il dialogo, ma quello contrassegnato con ``wx.ID_OK``, prima, esegue la validazione automatica. Tutti i widget nel dialogo vengono validati, proprio come se avessimo chiamato ``Validate`` sul dialogo. 

Notate che *se la validazione fallisce il dialogo non si chiude*. Questo vuol dire che, finché la validazione non ha successo (o l'utente non preme "annulla", ovviamente), il codice chiamante resta bloccato alla riga 74. E' evidente che non c'è proprio alcun modo di affidare al codice chiamante il compito di informare l'utente sul risultato della validazione: è proprio necessario che siano i validatori stessi a pensarci. 

Il codice chiamante prosegue la sua corsa quando la validazione ha successo, il dialogo si chiude e ``ShowModal`` restituisce il codice corrispondente al pulsante premuto. Se adesso il codice è ``wx.ID_OK``, si può stare sicuri che i dati sono validi. Attenzione però: in caso di codice ``wx.ID_CANCEL``, la validazione non è avvenuta e i dati non sono sicuri. 
                                                                                        
Questo è importante: la validazione avviene solo in caso di ``wx.ID_OK``. Se si desidera che i widget siano validati sempre, qualunque pulsante sia stato premuto, allora bisogna tornare alla validazione manuale: collegare i pulsanti a un evento, e chiamare ``Validate`` nel callback relativo. 

.. todo:: una pagina sulla validazione "in tempo reale" (avanzata? un'aggiunta a questa?)


Consigli sulla validazione.
---------------------------

Composizione di validatori.
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A una prima impressione, i validatori sembrano oggetti limitati: per esempio, non possono essere combinati tra loro per eseguire diversi test su un unico widget. Non è possibile chiamare diversi validatori uno dopo l'altro sullo stesso widget. Così, ogni validatore deve avere, nel suo metodo ``Validate``, tutti i test che servono per un dato widget in una data circostanza. Questo limita il loro utilizzo a un validatore per widget, o al massimo a un validatore per un limitato insieme di widget che si trovano per caso nelle medesime condizioni. 

Tuttavia questa "limitazione" dipende spesso da un utilizzo errato dei validatori. Non dovete pensare che i validatori siano il posto in cui scrivere davvero i test di validazione. Dovrebbero essere invece solo il punto di raccordo finale tra la vostra suite di test di validazione e il widget che dovete validare. Il codice effettivamente contenuto in ``Validate`` dovrebbe essere breve, e avere solo quanto basta a gestire i dati in partenza e le risposte in arrivo. 

Per esempio, io mi trovo spesso a scrivere cose come::

    def Validate(self, win):
        val = self.GetWindow().GetValue()
        if all((test1(val), test2(val), test3(val))):
            return True
        else:
            # informo l'utente che la validazione e' fallita
            return False
            
Così posso scrivere separatamente i vari ``test1``, ``test2``, etc. in modo "atomico" e generale, e poi combinarli tra loro a seconda dei casi (anche l'ordine di esecuzione si può naturalmente controllare). Così si può arrivare, nella peggiore delle ipotesi a dover scrivere un breve validatore per ciascun widget da validare: ogni validatore rappresenta una catena di test da eseguire. 

Ma volendo si può fare di meglio, e scrivere un validatore "general purpose" con un numero variabile di test passati come parametri::

    class GroupTestValidator(wx.PyValidator):
        def __init__(self, *tests):
            wx.PyValidator.__init__(self)
            self._tests = tests
        #Clone, TransferToWindow, TransferFromWindow... bla bla 
        
        def Validate(self, win):
            val = self.GetWindow().GetValue()
            if all([test(val) for test in self._tests]):
                return True
            else:
                return False
            
che poi può essere assegnato a diversi widget con diversi parametri::

    text_1 = wx.TextCtrl(..., validator=GroupTestValidator(test1, test2))
    text_2 = wx.TextCtrl(..., validator=GroupTestValidator(test1, test3, test4))
    
Chiaro che poi non bisogna esagerare: non è che un singolo validatore "dinamico" può bastare per tutte le esigenze della vostra applicazione.


Validazione a cascata.
^^^^^^^^^^^^^^^^^^^^^^

Sulla validazione a cascata, bisogna dire che è una grande comodità, tuttavia introduce dei limiti. Prima di tutto, la validazione si ferma al primo widget che non va bene, ma questo impedisce all'utente di sapere se ci sono altri errori, dopo. E' frustrante corregere un errore, premere di nuovo "invio", e scoprire che c'era un errore anche nel campo successivo. Se volete che tutti i widget siano validati comunque, non c'è niente da fare, dovete rinunciare alla validazione a cascata (e a maggior ragione a quella ricorsiva, e a quella automatica), e validare a mano tutti i widget. Fortunatamente in Python tutto diventa più semplice::

    failed = []
    for widget in (self.nome, self.cognome):
        if not widget.Validate():
            failed.append(widget)
    # poi presento la lista degli errori, etc. etc.

Basta un'occhiata a questo banale ciclo ``for``, e ci si chiede perchè perdere tempo con le validazioni a cascata, etc. Ancora una volta, questo è merito della grande flessibilità di Python. Tuttavia i meccanismi di wxPython possono tornare comodi per gestire i casi più consueti (e sicuramente saranno la maggioranza nelle varie applicazioni). 


Validazione a seconda di un contesto.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Un altro limite dei validatori è che sono concepiti per validare un widget "di per sé stesso", senza tenere conto del contesto (per esempio, del valore di altri widget). Ora, naturalmente il "contesto" può essere calcolato e passato "a mano" al validatore come argomento aggiuntivo::

    class ContextValidator(wx.PyValidator):
        #Clone, TransferToWindow, TransferFromWindow... bla bla 
        
        def Validate(self, win, context):
            val = self.GetWindow().GetValue()
            if all((test1(val, context), test2(val, context), ...)):
                ...
                
    # e quindi, nel codice chiamante:
    context = some_calculations() # per esempio, il valore di un altro widget
    retcode = widget.Validate(context)

Questo ovviamente rende impossibile ogni tipo di validazione automatica, ma abbiamo visto che con Python in genere non è un problema. 

Ma c'è di più: sempre grazie alla flessibilità di Python, possiamo anche far calcolare il contesto dinamicamente al validatore stesso. Fino a cose un po' temerarie come questo esempio, dove un validatore ammette che una casella di testo sia vuota solo se un'altra è piena::

    class AlternateEmptyValidator(wx.PyValidator):
        def __init__(self, context):
            wx.PyValidator.__init__(self)
            self.context = context
        #Clone, TransferToWindow, TransferFromWindow... bla bla 
        
        def Validate(self, win):
            val = self.GetWindow().GetValue()
            context_val = self.context()
            if context_val == '' and val == '': return False
            if context_val != '' and val != '': return False
            return True

E *non si deve usare così* naturalmente::

        text1 = wx.TextCtrl(..., validator=AlternateEmptyValidator(text2.GetValue))
        text2 = wx.TextCtrl(..., validator=AlternateEmptyValidator(text1.GetValue))

perché al momento di assegnare il validatore a ``text1``, ``text2`` non esiste ancora! Tuttavia, può essere usato senza problemi in questo modo::

    text1 = wx.TextCtrl(...)
    text2 = wx.TextCtrl(...)
    text1.SetValidator(AlternateEmptyValidator(text2.GetValue))
    text2.SetValidator(AlternateEmptyValidator(text1.GetValue))

La cosa importante è che, grazie a Python, passiamo direttamente un "callable" come argomento del validatore, lasciando a lui il compito di... chiamarlo, appunto, quando necessario. 


Problemi con i masked controls.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In ogni caso, altri problemi potrebbero spuntar fuori con i validatori. Per esempio, non giocano bene con i "masked controls" (cercateli sulla demo), una famiglia di widget che hanno un sistema di validazione interno, separato. Quando un masked control non è valido, produce un suo comportamento di default (per esempio si colora di giallo): ma siccome non ha un validatore vero e proprio attaccato, è difficile integrare questo suo comportamento in un processo di validazione a cascata, per esempio. 

Naturalmente si può argomentare che questo è colpa dei masked controls, e non dei validatori (che sono arrivati ben prima). In ogni caso i masked controls sono utili da usare, ed è spiacevole dover prevedere due flussi di validazione separati. 


Validazione ricorsiva.
^^^^^^^^^^^^^^^^^^^^^^

Ancora qualche parola sulla validazione ricorsiva. In linea di principio, meglio non esagerare, specialmente se applicata alle finestre top-level che raggruppano (in vari panel) diverse macro-aree della vostra applicazione. Quando chiamate ``Validate`` sul frame perché volete validare un certo settore, contemporaneamente validate anche tutti gli altri. Nella migliore delle ipotesi è una perdita di tempo; nella peggiore un bel guaio, se in quel momento gli altri settori sono in uno stato provvisoriamente inconsistente. 

La cosa migliore è affidarsi al principio "ogni area, un panel" e validare i singoli panel, facendo affidamento sul fatto che i loro figli diretti saranno i widget che davvero vi serve validare. Occasionalmente, quando uno di questi panel-area ha una gerarchia più complessa (contiene altri panel, che contengono i widget), allora potete settare ``wx.WX_EX_VALIDATE_RECURSIVELY`` solo per loro. 


In conclusione: code smell?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In conclusione, i validatori sono strumenti utili, ma può essere difficile farli funzionare in modo armonico. Da un lato, la loro praticità risalta soprattutto quando sono accoppiati ai dialoghi, con il meccanismo della validazione a cascata, e automatica. Basta fare clic su ``wx.ID_OK``, e ottieni gratis la validazione di tutto quanto. D'altra parte però con un ciclo ``for`` in Python, anche la validazione manuale è molto agevole, e consente inoltre di personalizzare più accuratamente che cosa e quando validare. Inoltre, sempre grazie a Python, è possibile scrivere validatori più generali e dinamici. 

Dopo aver imparato a usare bene i validatori, resta comunque sempre un vago "code smell". C'è poco da fare: i validatori entrano in gioco in un segmento difficile del flusso di gestione dell'applicazione, ovvero quando i dati "sporchi" della gui si devono mescolare ai dati "puri" del modello sottostante. Vedremo anzi, :ref:`nella seconda parte di questa analisi <validatoridue>`, che il disagio può aumentare quando si usano i validatori anche per trasferire dati dal modello alla gui.  

Alla fine, i validatori sono uno strumento. Vanno senz'altro bene per i casi più semplici, e possono essere usati con successo anche in scenari più difficili: ma se non riuscite ad armonizzarli nel vostro framework di validazione complessivo, potete tranquillamente rinunciarvi.

