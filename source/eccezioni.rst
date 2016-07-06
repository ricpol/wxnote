.. _eccezioni:

.. index:: 
   single: eccezioni; eccezioni Python

Gestione delle eccezioni in wxPython (1a parte).
================================================

Questa è la prima di due pagine che affrontano il complesso problema della gestione delle eccezioni in un programma wxPython, strettamente interconnesso con le osservazioni :ref:`che abbiamo già fatto<logging2>` sul logging. Potreste pensare che le eccezioni in wxPython funzionano come in un qualsiasi programma Python, ma come vedremo le cose non stanno proprio così. Un programma wxPython è sempre il risultato dell'interazione di codice Python e codice C++ sottostante, e anche le coppie meglio assortite non sempre vanno d'accordo. 

.. todo:: una pagina su SWIG e l'oop Python/C++.

Nel caso specifico della gestione delle eccezioni, ci sono tre aree problematiche:

1) le eccezioni Python non sono completamente libere di propagarsi in un programma wxPython: ne derivano alcune trappole insidiose che dovete saper evitare; 

2) non esiste un meccanismo di traduzione tra eccezioni C++ ed eccezioni Python...

3) ...ma servirebbe comunque solo fino a un certo punto, perché wxWidgets non usa le eccezioni C++ per segnalare condizioni di errori. wxWidgets fa uso di varie formule di "assert" e/o di allarmi emessi con il suo :ref:`sistema di log interno<logging2>`: esiste un meccanismo di traduzione degli "assert" in eccezioni Python, e si possono escogitare soluzioni per gestire meglio anche le scritture di log. Ma in entrambi i casi ci sono dei limiti. 

In questa prima pagina affrontiamo il problema specifico delle eccezioni Python. Dedichiamo :ref:`una pagina separata<eccezioni2>` all'analisi delle condizioni di errore che possono originarsi dal codice C++ di wxWidgets. 


Il problema delle eccezioni Python non catturate.
-------------------------------------------------

Probabilmente vi siete già accorti che in un programma wxPython le eccezioni si comportano in modo anomalo. Un'eccezione non intercettata, in un normale programma Python, si propaga fino in cima allo stack senza trovare nessun handler disposto a gestirla, finché il gestore di default non termina il programma, inviando il traceback dell'eccezione allo standard error (e quindi, tipicamente, alla shell che ha invocato lo script).

In wxPython d'altra parte, un'eccezione non controllata *non termina il programma*::

   class MyFrame(wx.Frame):
      def __init__(self, *a, **k):
         wx.Frame.__init__(self, *a, **k)
         b = wx.Button(self, -1, 'clic')
         b.Bind(wx.EVT_BUTTON, lambda evt: 1/0) # ops!

In questo esempio, ogni volta che cliccate sul pulsante innescate una ``ZeroDivisionError`` non gestita. Il traceback relativo compare in effetti nello standard error, ma l'applicazione wxPython resta perfettamente funzionante. 

Per capire questo bizzarro comportamento, occorre tenere presente che, durante il ciclo di vita di un'applicazione wxPython, il controllo dell'esecuzione passa di continuo da "strati" di codice Python a "strati" di codice wxWidgets (quindi, codice C++). Quando l'utente fa clic su un pulsante, innesca :ref:`come ben sappiamo<eventibasi>` il complesso meccanismo dell'emissione di un evento e della ricerca di un gestore: questa fase è controllata da wxWidgets (C++). Quando l'handler dell'evento è stato trovato, viene eseguito il callback relativo: questo in genere è codice che avete scritto voi (Python). Quando il callback è stato eseguito, il controllo ritorna al ``wx.App.MainLoop``: questo è di nuovo codice C++. E così via. 

Ora, ecco il problema: una eccezione Python non può propagarsi oltre lo "strato" in cui viene emessa. Non è possibile propagare un'eccezione Python attraverso strati di codice C++. Questo è un problema di cui gli sviluppatori wxPython sono ben consapevoli: in teoria dovrebbe essere possibile tradurre al volo una eccezione Python nella sua controparte C++ e viceversa, in modo da permettere la propagazione libera tra i vari strati. In pratica però, non è affatto banale implementare questo meccanismo: sono stati fatti dei tentativi, ma non si è mai approdati a nulla di definitivo. 

E quindi? Che cosa succede quando l'eccezione Python si propaga fino al "confine" dello strato in cui è stata generata, senza trovare nessun blocco 
``try/except`` disposto a prendersene cura? Succede una cosa brutta ma inevitabile: il codice C++ immediatamente successivo rileva che c'è una condizione di errore, chiama ``PyErr_Print`` per scriverlo nello standard error, e resetta l'errore. Quindi l'eccezione termina lì, e non ha modo di propagarsi fino a raggiungere il punto in cui l'interprete Python farebbe arrestare il programma. Voi potete vedere ugualmente il traceback nella shell (o dovunque abbiate :ref:`re-indirizzato lo standard error<reindirizzare_stdout>`), ma solo perché è stato scritto lì da ``PyErr_Print`` (una delle `API C di Python <https://docs.python.org/2.7/c-api/index.html>`_). 

Infine, tenete conto che esiste un caso interessante in cui questo comportamento non si applica. Se l'eccezione Python non controllata avviene prima di aver chiamato ``wx.App.MainLoop``, allora effettivamente il programma si interromperà "come al solito": questo perché, prima di entrare nel main loop, Python ha ancora il controllo dell'applicazione. In pratica, ci sono due posti in cui un'eccezione Python può verificarsi prima di entrare nel main loop: in ``wx.App.OnInit`` e nell'``__init__`` del frame principale dell'applicazione.


``try/except`` in wxPython non funziona sempre come vi aspettate.
-----------------------------------------------------------------

Se non siete ben consapevoli di questo comportamento, potreste trovarvi di fronte a situazioni paradossali. In Python "puro", potete intercettare un'eccezione anche molto lontano dal punto in cui si è generata::

   >>> def disastro():
   ...     return 1/0  # ops!
   ...
   >>> def produci_un_disastro():
   ...     return disastro()
   ...
   >>> def prepara_un_disastro():
   ...     return produci_un_disastro()
   ...
   >>> def salva_la_giornata():
   ...     try:
   ...         return prepara_un_disastro()
   ...     except ZeroDivisionError:
   ...         return "salvo per miracolo!"
   ...
   >>> salva_la_giornata()
   'salvo per miracolo!'
   >>>

Questa non è una buona pratica di programmazione: ma potete comunque farlo. In wxPython, invece, intercettare un'eccezione lontano dal punto di origine potrebbe non riuscire bene come immaginate::

   class MyFrame(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           b = wx.Button(self)
           b.Bind(wx.EVT_BUTTON, self.on_clic)
           self.Bind(wx.EVT_SIZE, self.on_size)

       def on_clic(self, evt):
           try:
               self.SendSizeEvent() # genera manualmente un wx.EVT_SIZE
           except ZeroDivisionError:
               print 'presa al volo!'

       def on_size(self, evt):
           evt.Skip()
           1/0 # ops!

Prendetevi qualche minuto per immaginare come potrebbe funzionare questo esempio, prima di proseguire. Abbiamo collegato ``wx.EVT_SIZE`` a un callback che produce una eccezione Python non gestita. Possiamo aspettarci, tutte le volte che ridimensioniamo la finestra, di veder comparire il traceback nella shell (la finestra però si ridimensiona correttamente. A wxWidgets non interessa il nostro codice problematico nel callback: fintanto che chiamiamo ``Skip``, l'handler di default dell'evento farà il suo mestiere). Per la precisione, un primo ``wx.EVT_SIZE`` viene emesso automaticamente già al momento di creare la finestra: quindi dovremmo vedere un traceback nella shell proprio come prima cosa. 

Quando però facciamo clic sul pulsante, ci aspettiamo una cosa diversa. Nel callback del pulsante noi generiamo manualmente un ``wx.EVT_SIZE``: quindi il callback difettoso verrà di nuovo eseguito, eccezione compresa. Questa volta però ci siamo premuniti, e abbiamo incluso la chiamata che genera il ``wx.EVT_SIZE`` in un blocco ``try/except``. Dunque, ciò che vedremo questa volta sarà il messaggio "presa al volo!" nella shell, giusto?

Sbagliato, purtroppo. Il problema è che, tra lo strato di codice Python pronto a intercettare l'eccezione, e lo strato di codice Python che innesca l'eccezione, c'è di mezzo un consistente strato di codice C++ (che si occupa del dispatch del ``wx.EVT_SIZE``). E attraverso questo strato la nostra eccezione non passa. Il risultato è che, anche quando il ``wx.EVT_SIZE`` si genera in seguito al clic sul pulsante, noi vedremo comunque il traceback nella shell, perché il ramo ``except`` che abbiamo predisposto non sarà mai raggiunto dall'eccezione. 

Non esiste una soluzione generale di questo problema. La cosa migliore è attenersi al noto principio di buon senso: le eccezioni dovrebbero essere intercettate più vicino possibile al punto di emissione. In Python è una buona pratica di programmazione, ma in wxPython è un principio guida da seguire con il massimo scrupolo. 


Che cosa fare delle eccezioni Python non gestite.
-------------------------------------------------

Abbiamo ormai capito che le eccezioni Python possono essere più difficili da intercettare in un programma wxPython, e abbiamo visto che le eccezioni non gestite non terminano prematuramente il programma. Questo però ci lascia con una domanda: come dovremmo comportarci con queste eccezioni non intercettate?


Il problema.
^^^^^^^^^^^^

Prima di tutto, non dovrebbe esserci bisogno di dirlo, ma insomma: in un programma con interfaccia grafica, pensato per l'utente finale, le eccezioni non gestite sono bachi puri e semplici. Non dovrebbero esserci. Se vi capitano in fase di sviluppo, poco male: tenete d'occhio il flusso dello standard error, osservate lo stacktrace, vi rimproverate perché l'eccezione si è verificata "in vivo" passando tra le maglie della vostra suite di test, debuggate, scrivete altri test, li eseguite, problema risolto. 

Tuttavia, sappiamo che i bachi vengono fuori anche (no, soprattutto!) quando ormai il programma è in produzione. E' a questo punto che wxPython vi fa rischiare grosso. In un normale programma Python, un baco in produzione significa che l'eccezione non gestita ferma il programma. Certo, l'utente non sarà felice. Forse l'uscita anomala lascerà qualche risorsa esterna non chiusa a dovere. Ma oltre a questo, il danno non ha modo di propagarsi. 

In un programma wxPython, d'altra parte, l'utente finale non vede lo standard error e non ha modo di accorgersi di nulla. Ecco uno scenario fin troppo comune (in pseudo-codice)::

   class Anagrafica(wx.Frame):
      def __init__(...):
         ...
         ok.Bind(wx.EVT_BUTTON, self.salva_dati)

      def salva_dati(self, evt):
         dati = self._raccogli_dati()
         try:
            db.orm.persisti(dati)
         except db.QualcosaNonVa:
            wx.MsgBox('Qualcosa non va')
            return
         wx.MsgBox('Dati salvati, tutto a posto')
         self.Close()

Quando l'utente fa clic sul pulsante "Salva", noi invochiamo una routine per salvare i dati nel database ("db.orm.persisti()" potrebbe far riferimento a un ORM, o comunque a un layer separato in una logica MVC). La nostra routine innesca un'eccezione custom "QualcosaNonVa" in caso di problemi, e noi correttamente la intercettiamo nel callback. Dunque, se qualcosa non va, l'utente vede un messaggio allarmante. Se invece tutto va bene, l'utente viene rassicurato e la finestra si chiude. Questo pattern in sé non ha niente di sbagliato. Ma se c'è un baco nel layer di gestione del database, "db.orm.persisti" innesca un'eccezione che non abbiamo previsto: siccome non la intercettiamo, tutto sembra andare per il verso giusto (ricordate, wxPython non ferma il programma). Ma in realtà i dati non sono stati salvati. Prima che l'utente abbia modo di accorgersi del problema, l'errore potrebbe ripetersi più volte; i dati sbagliati saranno usati per ulteriori elaborazioni; e il baco originario potrebbe essere molto difficile da individuare. 

Ora, in Python un approccio come questo viene giustamente considerato una cattiva pratica::

   try:
      main()
   except:  # un "bare except" per ogni possibile imprevisto
      # ...

Tuttavia possiamo chiederci se in wxPython non sia l'unico modo per risolvere il problema delle "eccezioni invisibili". Ci piacerebbe poter scrivere qualcosa come::

   if __name__ == '__main__':
       # questo non funziona davvero!
       try:
           app = wx.App(False)
           MainFrame(None).Show()
           app.MainLoop()
       except:
           wx.MessageBox('Qualcosa non va!!')
           wx.Exit()

Purtroppo, come avrete già intuito, questo non funziona. A partire da quando invocate ``wx.App.MainLoop``, ci sono troppi strati di codice C++ perché una eccezione Python imprevista possa finire nella rete del "bare except" che abbiamo messo al livello più alto dello stack. 


.. index:: 
   single: eccezioni; sys.excepthook

Una soluzione accettabile.
^^^^^^^^^^^^^^^^^^^^^^^^^^

Una soluzione accettabile è invece usare ``sys.excepthook`` dalla `libreria standard di Python <https://docs.python.org/2.7/library/sys.html#sys.excepthook>`_::

   def my_excepthook (extype, value, tback):
       wx.MessageBox('Questo non va proprio bene!', 'errore')
       # non dimenticate di loggare... qualcosa come:
       # logger.error('disastro fatale', exc_info=(extype, value, tback))
       wx.Exit()

   class MyFrame(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           b = wx.Button(self)
           b.Bind(wx.EVT_BUTTON, lambda evt: 1/0) # ops!

   if __name__ == '__main__':
       sys.excepthook = my_excepthook
       app = wx.App(False)
       MyFrame(None).Show()
       app.MainLoop()

Nel nostro "except hook" personalizzato possiamo inserire una logica arbitrariamente complessa. Per esempio, sarebbe perfettamente sicuro interagire con l'interfaccia grafica (aprire e chiudere finestre, postare eventi nella coda, etc.): la nostra eccezione Python non impedisce al framework C++ sottostante di continuare a funzionare, come sappiamo. Tuttavia, proprio perché stiamo affrontando un'eccezione imprevista (leggi: un baco) e non possiamo sapere che cosa sta succedendo, conviene limitarsi al minimo indispensabile: avvertire l'utente che il programma sta per chiudersi; fare il rollback di eventuali transazioni in corso; loggare il traceback dell'eccezione che altrimenti andrebbe perduto; infine, :ref:`chiudere l'applicazione<chiusuraapp>` nel modo che riteniamo migliore. 

E' possibile inserire il nostro except hook direttamente nel blocco ``if __name__=="__main__"``, come nel nostro esempio. In alternativa, un buon momento è come sempre ``wx.App.OnInit``. 
