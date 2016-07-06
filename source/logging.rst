.. _logging:

.. index:: 
   single: logging; con Python

Logging in wxPython (1a parte).
===============================

Questa è la prima di una serie di pagine che dedichiamo agli argomenti in qualche modo interconnessi del logging e della :ref:`gestione delle eccezioni<eccezioni>`. Non sono problemi specifici della programmazione di interfacce grafiche. In generale si usano le stesse strategie di qualunque programma Python: in queste pagine supponiamo sempre che abbiate una buona familiarità con le tecniche di base, e approfondiamo invece alcuni aspetti più specifici di wxPython. 

Come è noto, il sistema di logging è una componente irrinunciabile di ogni applicazione web, dove è necessario poter rintracciare l'origine di un problema tra migliaia di azioni provenienti da migliaia di connessioni contemporanee. Le applicazioni desktop in genere lavorano in ambienti più piccoli e più protetti, ma non per questo potete permettervi di trascurare il logging. Una volta che il programma ha abbandonato il vostro controllato ambiente di sviluppo per entrare in produzione, solo l'analisi dei log può permettervi di capire che cosa è successo se qualcosa va storto. 

Un'applicazione wxPython ha quindi bisogno di un sistema di logging esattamente come qualsiasi altro programma. Non è questa la sede per un tutorial sull'argomento: ci limitiamo a qualche raccomandazione generale, prima di affrontare alcuni aspetti più specifici relativi a wxPython. 

1) Nel mondo del web, lo scopo del logging è anche aiutarvi a profilare l'efficienza della vostra applicazione man mano che scala verso un numero di connessioni sempre più elevato. Per un'applicazione desktop, raramente questo aspetto ha importanza. Lo scopo del logging è quindi soprattutto di aiutarvi a rintracciare le cause degli errori. 

2) Di conseguenza, non abbiate paura di loggare molto. Nel web scegliere cosa loggare è un'arte, e un log alluvionato da milioni di registrazioni irrilevanti diventa inutile. Nel mondo desktop raramente questo è un problema, e potete permettervi di abbondare con le registrazioni. L'importante però è scegliere livelli diversi di criticità, e/o creare nomi e gerarchie di componenti, flag, o altre indicazioni che vi aiutano a filtrare successivamente il registro. 

3) Ma fate attenzione a non loggare dati sensibili! Questo può essere molto pericoloso, perché in genere i file di log sono più vulnerabili del database dell'applicazione. In molti casi è comodo loggare, per esempio, l'ultima riga inserita in una tabella, per avere idea precisa di che cosa ha innescato un errore. Ma dovreste attribuire a queste registrazioni un livello di criticità più basso ("debug", per esempio) di quello che impostate in produzione. In ogni caso, concordate sempre una policy precisa con il committente/utente del vostro programma: fategli sapere che cosa state loggando, e quali sono i potenziali pericoli.

4) Per lo stesso motivo, fate attenzione che il log non diventi un involontario sistema di tracciamento dell'attività degli utenti. Se avete bisogno di legare ciascuna registrazione a chi l'ha originata, potrebbe essere necessario, per esempio, generare un codice casuale al momento del login, da usare solo ai fini del log e da cambiare a ogni nuova sessione. 

5) Fornite all'utente un modo per cambiare temporaneamente il livello di criticità del logging, senza bisogno di un vostro diretto intervento sui file di configurazione (per esempio, potrebbe essere una regolazione da includere in un dialogo di opzioni del vostro programma). 

6) Preparatevi all'eventualità che tutto possa andar bene! Se non intervenite per parecchio tempo, le dimensioni del file di log cresceranno senza limiti, e questo è un problema. Se usate il modulo ``logging`` della libreria standard di Python, vi conviene loggare su un ``RotatingFileHandler`` o un ``TimedRotatingFileHandler``. Create inoltre una routine automatica per cancellare o archiviare i vecchi log, nel caso. 

7) Siate pronti ad analizzare i vostri log rapidamente. Potete usare dei tool, e/o scrivere delle routine ad-hoc: in ogni caso, fate delle prove e testate in anticipo. 


Logging con Python.
-------------------

Il modulo ``logging`` della libreria standard di Python è un ottimo framework: se non avete esigenze particolari, vi conviene senz'altro affidarvi a questo. Se non conoscete ``logging``, la `documentazione ufficiale <https://docs.python.org/2.7/library/logging.html>`_ è un modello di chiarezza: in particolare, potete cominciare dal `tutorial <https://docs.python.org/2.7/howto/logging.html#logging-basic-tutorial>`_ che è davvero semplice da capire. 

Se siete già pratici dell'uso di ``logging``, non dovreste avere problemi: le strategie da usare in un'applicazione wxPython sono del tutto analoghe a quelle di un qualsiasi altro programma Python. 

Di solito, un buon momento per inizializzare un logger "principale" è in ``wx.App.OnInit``::

   import logging, logging.config

   class MyApp(wx.App):
      def OnInit(self):
         self.logger = logging.getLogger(__name__)
         logging.config.fileConfig('logging.ini')
         return True

In questo modo, tutte le finestre della vostra applicazione potranno ottenere un riferimento allo stesso logger semplicemente con::

   self.logger = wx.GetApp().logger

oppure, naturalmente, crearsi un proprio logger chiamando di nuovo ``self.logger = logging.getLogger(__name__)``. Le strategie per dare un nome ai logger dipendono come di consueto dall'organizzazione del vostro codice, dalle necessità e dai gusti personali. Se riuscite a mantenere funzionalità separate in moduli separati, un semplice ``__name__`` andrà bene. Altrimenti, ciascuna classe potrebbe dare al logger il proprio nome, per esempio. 

Molto spesso le registrazioni avvengono dall'interno di un callback collegato a un evento. In wxPython, ricordate, certi eventi possono capitare molto frequentemente. Se registrate un log in risposta a eventi come ``wx.EVT_IDLE``, ``wx.EVT_SIZE``, ``wx.EVT_MOVE``, ``wx.EVT_PAINT`` e molti altri, la fluidità della vostra gui finirà per risentirne (e vi ritroverete con un log sterminato). Se proprio vi serve loggare questi eventi, potete aiutarvi con :ref:`strumenti<yield_etc>` come ``wx.Yield``. 


Re-indirizzare il log verso la gui.
-----------------------------------

Specialmente in fase di sviluppo, può capitare di voler vedere il log "in tempo reale" sullo schermo. La cosa più facile, e probabilmente anche la migliore, è dirigere l'output del log verso la shell (eventualmente duplicandolo su un file). Potete usare le consuete strategie per differenziare l'ambiente di sviluppo da quello di produzione (per esempio, usare file di configurazione diversi).

Se preferite, tuttavia, potete indirizzare il log verso la vostra gui. Questo potrebbe essere desiderabile in fase di sviluppo, se per esempio avete timore che il buffer della vostra shell sia troppo piccolo, e/o volete un display più maneggevole (in casi estremi, potreste scrivere una classe personalizzata per visualizzare il log all'interno di qualche widget super-specializzato come ``RichTextCtrl``, basato su Scintilla). In fase di produzione, d'altra parte, questo non dovrebbe essere necessario: dopo tutto, mostrare un log all'utente finale dovrebbe andare contro l'intera idea di "programma con interfaccia grafica".

La soluzione più facile, ancora una volta, è indirizzare il log verso lo standard output e poi utilizzare una delle :ref:`note tecniche<reindirizzare_stdout>` per visualizzare l'output nella gui. In questo modo, tuttavia, lo stream del log si mescolerebbe agli standard output/error (che però in una applicazione grafica non dovrebbero comunque essere mai troppo impegnati). Se questo per voi è inaccettabile, e volete comunque mantenere il flusso del log ben separato, magari dedicandogli uno spazio ad-hoc nella vostra interfaccia, anche questo non è difficile. 

Quello che dovete fare è crearvi un ``logging.Handler`` personalizzato. Ecco un approccio minimalistico al problema::

   class MyLoggingHandler(logging.Handler):
       def __init__(self, ctrl):
           logging.Handler.__init__(self)
           self.ctrl = ctrl

       def emit(self, record):
           record = self.format(record) + '\n'
           self.ctrl.write(record)


   class MyTextCtrl(wx.TextCtrl):
       # un TextCtrl che espone l'api "write" richiesta da MyLoggingHandler.emit
       write = wx.TextCtrl.AppendText


   class MainFrame(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           p = wx.Panel(self)
           self.log_record = MyTextCtrl(p, style=wx.TE_MULTILINE|wx.TE_READONLY)
           do_log = wx.Button(p, -1, 'emetti un log')
           do_std = wx.Button(p, -1, 'emetti stdout/err')
           do_log.Bind(wx.EVT_BUTTON, self.on_do_log)
           do_std.Bind(wx.EVT_BUTTON, self.on_do_std)

           s = wx.BoxSizer(wx.VERTICAL)
           s.Add(self.log_record, 1, wx.EXPAND|wx.ALL, 5)
           s1 = wx.BoxSizer(wx.HORIZONTAL)
           s1.Add(do_log, 1, wx.EXPAND|wx.ALL, 5)
           s1.Add(do_std, 1, wx.EXPAND|wx.ALL, 5)
           s.Add(s1, 0, wx.EXPAND)
           p.SetSizer(s)

       def on_do_log(self, evt):
           wx.GetApp().logger.log(logging.WARNING, "questo e' un log")

       def on_do_std(self, evt):
           print "questo e' uno stdout; segue uno stderr:"
           print 1/0


   class MyApp(wx.App):
       def OnInit(self):
           self.logger = logging.getLogger(__name__)
           # potete eventualmente aggiungere altri handler al logger
           # self.logger.addHandler(logging.StreamHandler())
           # self.logger.addHandler(logging.FileHandler(filename='log.txt'))
           main_frame = MainFrame(None)
           handler = MyLoggingHandler(main_frame.log_record)
           handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
           self.logger.addHandler(handler)
           main_frame.Show()
           return True

   if __name__ == '__main__':
       app = MyApp(False)
       app.MainLoop()

Come si vede, è piuttosto semplice. Per prima cosa creiamo un handler personalizzato ``MyLoggingHandler``, che si potrà poi abbinare a qualunque widget wxPython: l'unica richiesta, naturalmente, è che il widget implementi una interfaccia per le scritture (qui l'abbiamo chiamata ``write``). 

Il guaio però è che non possiamo collegare l'handler finché il widget (e quindi tutta la finestra che gli sta intorno) non è stato creato. Nel nostro esempio abbiamo organizzato il codice necessario in ``wx.App.OnInit``, in modo da essere sicuri di rispettare l'ordine giusto. Finché il widget che deve contenere il log è nella finestra principale dell'applicazione, questa soluzione dovrebbe bastare. Ma se il log deve apparire in una finestra secondaria, che può essere chiusa e magari riaperta dall'utente... allora siete nei guai: se il log viene scritto in un momento in cui il widget non esiste, otterrete un ``wx.PyDeadObjectError`` o qualche eccezione analoga. 

Se volete far vedere il log in una finestra diversa da quella principale, potete adottare diverse strategie per accertarvi che il widget esista sempre per tutto il ciclo di vita della vostra applicazione. Per esempio potreste nascondere la finestra, invece di chiuderla::

   class MyLoggingHandler(logging.Handler):
       def __init__(self, ctrl):
           logging.Handler.__init__(self)
           self.ctrl = ctrl

       def emit(self, record):
           record = self.format(record) + '\n'
           self.ctrl.write(record)


   class LogWindow(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           self.log_record  = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
           self.Bind(wx.EVT_CLOSE, self.OnClose)

       def OnClose(self, evt):
           self.Hide()

       def write(self, record):
           # implementiamo l'api richiesta da MyLoggingHandler
           self.log_record.AppendText(record)


   class MainFrame(wx.Frame):
       def __init__(self, *a, **k):
           wx.Frame.__init__(self, *a, **k)
           p = wx.Panel(self)
           do_log = wx.Button(p, -1, 'emetti un log', pos=(20, 20))
           do_std = wx.Button(p, -1, 'emetti stdout/err', pos=(20, 60))
           show_log = wx.Button(p, -1, 'mostra log', pos=(20, 100))
           do_log.Bind(wx.EVT_BUTTON, self.on_do_log)
           do_std.Bind(wx.EVT_BUTTON, self.on_do_std)
           show_log.Bind(wx.EVT_BUTTON, self.on_show_log)
           self.Bind(wx.EVT_CLOSE, self.on_close)

       def on_do_log(self, evt):
           wx.GetApp().logger.log(logging.WARNING, "questo e' un log")

       def on_do_std(self, evt):
           print "questo e' uno stdout; segue uno stderr:"
           print 1/0

       def on_show_log(self, evt):
           wx.GetApp().log_window.Show()

       def on_close(self, evt):
           wx.GetApp().log_window.Destroy()
           evt.Skip()


   class MyApp(wx.App):
       def OnInit(self):
           self.logger = logging.getLogger(__name__)
           main_frame = MainFrame(None)
           self.log_window = LogWindow(None, title='LOG')
           handler = MyLoggingHandler(self.log_window)
           self.logger.addHandler(handler)
           main_frame.Show()
           self.log_window.Show()
           return True

   if __name__ == '__main__':
       app = MyApp(False)
       app.MainLoop()

In questo esempio, la finestra che mostra il log viene creata all'inizio (in ``wx.App.OnInit``) e distrutta solo al momento di chiudere la finestra principale (in risposta al ``wx.EVT_CLOSE``). Per tutto il ciclo di vita dell'applicazione, l'utente apre e chiude a piacere la finestra, ma in realtà non fa altro che mostrarla e nasconderla. 


Loggare da thread differenti.
-----------------------------

``logging`` è thread-safe, quindi non dovreste poter tranquillamente loggare da thread differenti, come per qualsiasi altro programma Python. 

Il problema naturalmente si verifica quando, oltre a voler loggare da thread diversi, avete anche fatto qualcosa di esotico come re-indirizzare l'output del log verso qualche widget della gui. Questo è vietato dalla prima regola aurea dei thread in wxPython: mai modificare lo stato della gui da un thread secondario. Niente paura, però: la seconda regola aurea dei thread in wxPython viene in soccorso: basta includere la chiamata pericolosa in ``wx.CallAfter`` e tutto torna a funzionare come per magia. 

Riprendendo l'esempio qui sopra, se volete usare usare l'handler personalizzato ``MyLoggingHandler`` in una situazione in cui è possibile che il log sia scritto anche da thread secondari, basterà modificarlo come segue::

   class MyLoggingHandler(logging.Handler):
       def __init__(self, ctrl):
           logging.Handler.__init__(self)
           self.ctrl = ctrl

       def emit(self, record):
           record = self.format(record) + '\n'
           if wx.Thread_IsMain():
               self.ctrl.write(record)
           else:
               wx.CallAfter(self.ctrl.write, record) # thread-safe!

.. todo:: una pagina sui thread.


In conclusione...
-----------------

Quasi certamente l'impalcatura del vostro log si affiderà al modulo ``logging`` della libreria standard Python. Tuttavia, anche wxPython mette a disposizione un suo framework di logging interno: difficilmente lo troverete più utile di ``logging``, e tuttavia dovete ugualmente sapere come funziona. Infatti wxPython lo utilizza anche senza il vostro consenso, per alcune importanti funzioni: ne parliamo più in dettaglio :ref:`nella prossima pagina<logging2>` che dedichiamo a questi argomenti. 
