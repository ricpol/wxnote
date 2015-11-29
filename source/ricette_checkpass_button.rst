.. _ricette_checkpass_button:

Un pulsante che controlla le credenziali prima di procedere.
============================================================

Questo pulsante può essere usato al posto di un normale ``wx.Button``, ed è uguale in tutto e per tutto. La sola differenza è che, in risposta a un ``EVT_BUTTON`` (un normale clic), chiede all'utente di inserire una password, e solo in caso positivo passa a eseguire il callback associato.

La prima versione.
------------------

.. literalinclude:: /_static/snippets/recipes/permission_button.py
   :lines: 5-50
   :linenos:

Ecco come si può manipolare la catena degli eventi per ottenere effetti un po' più concreti degli esempi presentati nei :ref:`capitoli dedicati agli eventi <eventi_avanzati>`. 
Nel mondo reale, chiaramente, la funzione ``check_psw`` potrebbe essere sostituita da un controllo su nome utente e password (confrontando con un database), o con un più avanzato sistema di permessi. 

E' utile ripeterlo: non è necessario intervenire sulla propagazione degli eventi per ottenere un effetto del genere. Per esempio, si potrebbe facilmente scrivere un decoratore da applicare ai singoli callback che necessitano di un controllo sulle credenziali (a-la-Django, per intenderci). E questo potrebbe essere un metodo più "corretto" da usare, perché non ricorre a una specificità della gui per la logica di business dell'applicazione. 

Tuttavia è utile anche sapere che queste cose, quando serve, si possono fare restando all'interno della logica di wxPython.

Approfondiamo il problema.
--------------------------

Ciò detto, questa ricetta richiede qualche parola in più per spiegare lo strano giro che abbiamo dovuto fare, per ricevere un primo evento ed emetterne subito dopo un secondo. 

Il problema generale, qui, è che è molto difficile organizzare una catena "ordinata" di callback in wxPython. Come regola generale, se avete bisogno di inserire più di un callback in risposta a un evento, è meglio scrivere il codice in modo tale che non sia importante l'ordine in cui i callback sono eseguiti. 

Se però l'ordine di esecuzione è importante (ed è il nostro caso: vogliamo che il controllo della password avvenga prima del resto), allora siate pronti a fare salti mortali. 

Questo esempio minimo riproduce il problema che incontriamo nel nostro caso::

  class MyButton(wx.Button):
      def __init__(self, *a, **k):
          wx.Button.__init__(self, *a, **k)
          self.Bind(wx.EVT_BUTTON, self.check_psw)

      def check_psw(self, evt):
          print 'controllo della password!'
          evt.Skip()

  class Test(wx.Frame):
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)
          b = MyButton(p, -1, 'clic', pos=((50, 50)))

          b.Bind(wx.EVT_BUTTON, self.on_clic)
          # self.Bind(wx.EVT_BUTTON, self.on_clic, b)

      def on_clic(self, evt):
          print 'qualche operazione con permessi privilegiati'
          evt.Skip()

  app = wx.App(False)
  Test(None).Show()
  app.MainLoop()

Se adesso fate girare questo esempio, vi accorgete che l'ordine dei callback è tragicamente invertito: prima viene eseguita l'operazione critica, e poi si chiede la password all'utente!

Questo avviene perché il callback collegato dinamicamente con ``Bind`` ha la precedenza su quello definito nella classe madre. Una soluzione sarebbe intercettare l'evento non direttamente nel pulsante che lo genera, ma nel suo parent, utilizzando il "secodo stile" di binding :ref:`che abbiamo visto<tre_stili_di_bind>`. Provate a far girare il codice sostituendo ``b.Bind...`` con ``self.Bind...``, e vedrete che adesso "funziona". Infatti l'evento, prima di arrivare all'handler del panel (che provoca l'esecuzione del codice privilegiato) ha il tempo di passare per l'handler della classe madre, che innesca il controllo della password. 

Tuttavia questa soluzione non è molto sicura: ci fidiamo del fatto che il codice cliente utilizzi lo stile "giusto" di binding per collegare il suo evento, in modo da metterlo educatamente in coda dietro al nostro. In molti casi possiamo conviverci serenamente: basta documentare bene come il nostro pulsante deve essere usato. 

Ma se non vogliamo correre questo rischio, dobbiamo fare un po' fatica. Nella versione iniziale di questa ricetta, abbiamo sfruttato il fatto che un ``wx.Button``, come abbiamo visto, emette prima un ``wx.EVT_LEFT_DOWN`` e un ``wx.EVT_LEFT_UP``, e solo allora il ``wx.EVT_BUTTON`` che in genere viene usato dal codice cliente. Di conseguenza, nella nostra classe madre, abbiamo intercettato il ``wx.EVT_LEFT_UP`` che sicuramente viene innescato prima, e ne abbiamo approfittato per fare il nostro controllo di sicurezza. 

Purtroppo però, una volta intercettato, quell'evento è "consumato". Possiamo chiamare ``Skip``, ma anche questo si riferisce solo al ``wx.EVT_LEFT_UP``: non c'è modo di "far tornare al via" il successivo ``wx.EVT_BUTTON``, per farlo intercettare dal pulsante nel codice cliente. Ormai quell'handler è stato oltrepassato. 

Ecco perché :ref:`abbiamo dovuto diramare<eventi_personalizzati>` un ``wx.EVT_BUTTON`` fresco, pronto a essere usato dal pulsante. 

Se questa soluzione vi sembra troppo macchinosa... c'è un aspetto anche peggiore! Il nostro accrocchio funziona come dovrebbe solo fintanto che il codice cliente si limita a intercettare ``wx.EVT_BUTTON``. Ma se per qualche ragione volesse intercettare anche lui ``wx.EVT_LEFT_UP`` (o peggio ancora, ``wx.EVT_LEFT_DOWN``), saremmo di nuovo al problema della "gara degli handler" che abbiamo visto prima. 

E non solo: se vogliamo dirla tutta, il nostro approccio funziona solo perché stiamo parlando un ``wx.Button``, che fortunatamente ha la caratteristica di emettere tre eventi in successione. Ma se volessimo generalizzare il problema con un altro widget, che emette un solo evento per volta, saremmo punto e a capo. 

La seconda versione.
--------------------

Se questo trucco vi sembra un po' troppo sporco, in effetti esiste una soluzione più definitiva: basta scrivere un :ref:`handler personalizzato<handler_personalizzati>`, e spingerlo in cima allo stack degli handler. Nel nostro handler gestiremo l'evento con l'operazione prioritaria che ci sta a cuore. 

Un esempio vale più di mille parole, come sempre:

.. literalinclude:: /_static/snippets/recipes/permission_button.py
   :lines: 55-
   :linenos:

Abbiamo semplicemente spostato la logica del controllo della password da ``MyButton`` a ``MyEvtHandler``. La vera magia è, naturalmente, chiamare ``PushEventHandler`` per portare il nostro handler in cima alla lista degli handler del pulsante. Una volta che ci siamo assicurati che il nostro codice sarà eseguito per primo, il resto è un gioco da ragazzi: se la password è corretta chiamiamo ``Skip`` e lasciamo propagare l'evento. Se no, tutto si ferma lì. Notate anche che adesso il codice fa quello che vogliamo indipendentemente dallo "stile" di binding preferito dal codice sorgente. 
