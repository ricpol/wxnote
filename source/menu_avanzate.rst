.. _menu_avanzate:

.. index::
   single: menu
   
I menu: concetti avanzati.
==========================

Nelle :ref:`due<menu_basi>` :ref:`pagine<menu_basi2>` precedenti che abbiamo dedicato ai menu, abbiamo coperto le basi necessarie per l'uso di tutti i giorni. In questa pagina copriamo invece altre tecniche, non necessariamente più "difficili", ma semplicemente meno consuete. 

.. index::
   single: icone; nei menu
   single: menu; icone
   single: wx.MenuItem; SetBitmap
   single: menu; wx.MenuItem.SetBitmap

Icone nelle voci di menu.
-------------------------

Per cominciare, un tocco gentile: come inserire una piacevole icona nelle vostre voci di menu:: 

  menu = wx.Menu()
  item = wx.MenuItem(menu, -1, 'foo')
  item.SetBitmap(wx.Bitmap('image.jpg'))
  menu.AppendItem(item)

Niente di particolarmente difficile, solo che purtroppo l'icona deve essere attribuita prima di agganciare la voce al menu. Di conseguenza non possiamo usare il solito pattern (``menu.Append(...)``), ma dobbiamo creare la voce di menu separatamente. Per questo usiamo il costruttore ``wx.MenuItem()``; poi aggiungiamo l'icona (``SetBitmap``), e infine agganciamo la voce al menu usando il metodo alternativo ``AppendItem`` al posto del normale ``Append`` (la differenza è che il primo accetta ``MenuItem`` già pronti all'uso, mentre il secondo li crea al volo).

Per quanto riguarda ``wx.Bitmap``, probabilmente dovremo dedicare una pagina separata all'uso delle immagini in wxPython. Per il momento, vi basta sapere che si fa così. 

.. todo:: una pagina sulle immagini

.. index::
   single: menu; contestuali, popup
   single: wx.EVT_CONTEXT_MENU
   single: wx.Frame; PopupMenu
   single: menu; wx.EVT_CONTEXT_MENU
   single: menu; wx.Frame; PopupMenu
   single: eventi; wx.EVT_CONTEXT_MENU

Menu contestuali e popup.
-------------------------

Ecco invece qualcosa di più concreto. Finora abbiamo visto soltanto menu (``wx.Menu``) agganciati a una barra dei menu (``wx.MenuBar``). Tuttavia i menu possono comparire anche in posti del tutto inaspettati: una tecnica consueta è quella del "menu contestuale" (che si apre facendo clic col tasto destro), ma si può far comparire un menu in qualsiasi punto in risposta a un qualsiasi evento, in teoria (in teoria! In pratica, però, è meglio non sorprendere troppo il povero utente).

Di per sé queste tecniche non sono difficilissime, ma per essere usate in modo efficiente richiedono un briciolo di strategia. Procediamo per gradi. 

Una piccola nota terminologica: nel seguito, confondiamo volentieri "menu contestuale" e "menu popup". Di base, sono la stessa cosa (ovvero, menu popup). Un menu contestuale, come vedremo, a rigore è un menu popup che si apre in risposta a un particolare evento ``wx.EVT_CONTEXT_MENU``. Ma è puramente una distinzione di termini.

Fare prima il binding degli eventi.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Occorre tenere conto del fatto che questo genere di menu, per loro natura, appaiono e scompaiono di continuo. In pratica, la strategia migliore è considerarli menu "usa-e-getta" che create e distruggete ogni volta (potete nascondere il menu invece di distruggerlo: ma questo funziona solo se vi serve ogni volta lo stesso menu, e in genere è poco pratico).

Se non ci sono problemi a creare e distruggere anche mille volte un menu, conviene però gestire gli eventi una volta sola, in modo da non dover rifare tutte le volte il collegamento tra le varie voci e i callback. 

Per assurdo che possa sembrare, una buona strategia è fare il binding degli eventi ancora prima di creare le voci dei menu, e quindi i menu stessi. La cosa è perfettamente possibile: basta "prenotare" degli id, e usare gli id per fare il binding. Ebbene sì: i menu contestuali sono uno dei pochi posti di wxPython in cui non è sbagliato usare esplicitamente :ref:`gli id<gli_id>`. Come abbiamo visto, un altro caso potrebbero essere i :ref:`ranged event<ranged_menu_events>`.

Per esempio, va benissimo qualcosa come::

  self.Bind(wx.EVT_MENU, self.my_callback_1, id=100)
  self.Bind(wx.EVT_MENU, self.my_callback_2, id=101)
  self.Bind(wx.EVT_MENU, self.my_callback_3, id=102)
  # etc.

  def my_callback_1(self, evt):  # etc etc
  def my_callback_2(self, evt):  # etc etc
  def my_callback_3(self, evt):  # etc etc

Per prima cosa collegate dei semplici id a dei callback specifici. Poi, quando arriverà il momento di creare le voci del menu contestuale, basterà fare attenzione ad assegnare manualmente gli id giusti. Alla fine, potrete distruggere senza problemi il menu contestuale: gli id resteranno sempre lì, già pronti e collegati ai callback. 

Le cose potrebbero ulteriormente complicarsi, perché spesso nei menu contestuali compaiono delle voci che già esistono anche nel menu principale (salva, copia, incolla...), e che avete già collegato ai callback giusti al momento di creare il menu principale. Anche in questo caso, la soluzione è di attribuire esplicitamente l'id di queste voci, e usare lo stesso id anche nel menu contestuale. Per esempio::

  menu = wx.Menu() # questo e' il menu principale
  menu.Append(100, 'foo') # questa servira' anche nei menu contestuali
  # ...
  self.Bind(wx.EVT_MENU, self.my_callback, id=100)

Creare e mostrare il menu popup.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Un menu contestuale si crea come un qualsiasi altro menu, e può contenere sottomenu, voci spuntabili o blocchi "radio", icone, etc. Potrebbe anche contenere shortcut e acceleratori, anche se raramente possono servire in questi casi. 

Una volta creato, il menu viene mostrato con il metodo ``self.PopupMenu()`` (dove ``self`` è la finestra corrente). Il menu appare nel punto in cui si trova il cursore del mouse: siccome di solito voi mostrate il menu in risposta a un clic dell'utente, il menu apparirà lì dove l'utente se lo aspetta (a meno che il menu appaia in risposta a un evento che non comporta nessun clic, come vedremo: in questo caso sarà meglio specificare dove va fatto apparire il menu).

Non appena il menu appare, resta in attesa del prossimo clic dell'utente, ed eventualmente innesca un evento in corrispondenza della sua scelta (eventualmente: perché l'utente potrebbe anche cliccare fuori dal menu, e in questo caso niente succede). Quando l'evento è stato processato, il flusso del programma torna nelle vostre mani: la prima cosa che dovete fare è ovviamente distruggere il menu, in modo da non lasciarlo in giro (il comportamento di default si limiterebbe a nasconderlo). 

Questo esempio chiarisce tutto quello che abbiamo detto fin qui::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          # prima, preparo i binding... 
          self.Bind(wx.EVT_MENU, self.my_callback_1, id=100)
          self.Bind(wx.EVT_MENU, self.my_callback_2, id=101)
          self.Bind(wx.EVT_MENU, self.my_callback_3, id=102)

          p = wx.Panel(self)
          wx.StaticText(p, -1, 'fai clic qui', pos=((50, 50)))
          p.Bind(wx.EVT_LEFT_UP, self.on_clic)

      def on_clic(self, evt): 
          # l'utente ha fatto clic: dobbiamo creare il menu popup...
          menu = wx.Menu()
          menu.Append(100, 'scelta uno') # notare gli id...
          menu.Append(101, 'scelta due')
          menu.Append(102, 'scelta tre')
          # ... e adesso lo mostriamo:
          self.PopupMenu(menu)
          # adesso il menu popup resta a disposizione:
          # quando l'utente ha finito di usarlo, il flusso del programma
          # torna qui: subito distruggiamo il popup
          menu.Destroy()

      def my_callback_1(self, evt): print 'hai scelto la uno'
      def my_callback_2(self, evt): print 'hai scelto la due'
      def my_callback_3(self, evt): print 'hai scelto la tre'

  if __name__ == '__main__':
      app = wx.App(False)
      MyFrame(None).Show()
      app.MainLoop()

In questo caso il menu popup appare in risposta a un clic in un punto qualsiasi del panel (abbiamo dovuto usare ``wx.EVT_LEFT_UP`` perché naturalmente un panel non dispone di eventi specifici come ``wx.EVT_BUTTON``). 

Dopo che l'utente ha finito di usare il menu, lo distruggiamo e siamo pronti a ricrearlo di nuovo alla prossima occasione. Come si vede, il meccanismo di base è piuttosto semplice. 

Ecco invece l'esempio di prima modificato per mostrare come la stessa voce può apparire in un menu "normale" e in un menu popup::


  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          # binding per i menu popup
          self.Bind(wx.EVT_MENU, self.my_callback_1, id=100)
          self.Bind(wx.EVT_MENU, self.my_callback_2, id=101)

          menu = wx.Menu() # menu principale
          menu.Append(-1, 'bla bla')
          menu.Append(102, 'anche popup')  # questo va anche nel popup
          self.Bind(wx.EVT_MENU, self.my_callback_3, id=102)

          menubar = wx.MenuBar()
          menubar.Append(menu, 'Menu')
          self.SetMenuBar(menubar)

          p = wx.Panel(self)
          wx.StaticText(p, -1, 'fai clic qui', pos=((50, 50)))
          p.Bind(wx.EVT_LEFT_UP, self.on_clic)

      def on_clic(self, evt): 
          menu = wx.Menu()
          menu.Append(100, 'scelta uno') 
          menu.Append(101, 'scelta due')
          menu.Append(102, 'anche popup') # c'e' anche nel menu principale
          self.PopupMenu(menu)
          menu.Destroy()

      def my_callback_1(self, evt): print 'hai scelto la uno'
      def my_callback_2(self, evt): print 'hai scelto la due'
      def my_callback_3(self, evt): print 'la voce che sta in entrambi i menu'

  if __name__ == '__main__':
      app = wx.App(False)
      MyFrame(None).Show()
      app.MainLoop()


Un "autentico" menu contestuale.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Un menu contestuale, nell'uso comune del termine, è un menu popup che compare in risposta al clic col pulsante destro del mouse. Nell'esempio di sopra, avremmo tranquillamente potuto scrivere::

  p.Bind(wx.EVT_RIGHT_UP, self.on_clic)

e questo basta per creare un menu contestuale a tutti gli effetti... almeno a prima vista. 

In realtà, tuttavia, se volete creare un menu contestuale "nel modo giusto" dovreste utilizzare l'evento ``wx.EVT_CONTEXT_MENU`` per mostrare il vostro menu popup. 

wxPython vi mette a disposizione questo evento proprio per questo specifico scopo. Che differenza c'è tra questo e un banale ``wx.EVT_RIGHT_UP``? 

Prima di tutto, ``wx.EVT_CONTEXT_MENU`` si innesca anche quando l'utente chiede il menu contestuale con la tastiera (c'è un tasto apposito, anche se non tutte le piattaforme lo usano!), e quindi garantisce l'esperienza nativa più completa. 

In secondo luogo, così ``wx.EVT_RIGHT_UP`` viene lasciato libero: potete usarlo separatamente per processare altre cose, se vi serve. Attenti solo a non pasticciare con :ref:`la catena degli eventi<eventi_avanzati>`: quando l'utente rilascia il pulsante destro del mouse, per prima cosa viene innescato il ``wx.EVT_RIGHT_UP``. Se questo non viene processato, allora si innesca il ``wx.EVT_CONTEXT_MENU``. Quindi, se catturate l'evento del mouse, non dimenticatevi di chiamare ``Skip()``, altrimenti l'evento per il menu contestuale non potrà mai partire. 

Ancora una complicazione sulla posizione.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Se l'utente chiama il menu contestuale, lo vede apparire alla posizione corrente del puntatore. Questo comportamento va benissimo (e non provate a modificarlo, se non volete farvi odiare), se il menu compare in seguito a un clic del mouse.

Ma se il menu contestuale è chiamato con la tastiera, allora il comportamento di default non è più adatto, perché il puntatore del mouse potrebbe trovarsi da tutt'altra parte in quel momento. 

Potete scoprire la posizione corrente del puntatore in seguito a un ``wx.EVT_CONTEXT_MENU`` chiamando ``GetPosition`` sull'evento nel callback. Se ``GetPosition`` vi restituisce ``wx.DefaultPosition`` invece di una tupla, vuol dire che l'evento è stato chiamato dalla tastiera. In questo caso, prima di mostrare il menu contestuale, vi conviene decidere una posizione adatta. 

Nell'esempio che segue, vogliamo che una casella di testo abbia un menu contestuale: se l'utente lo richiama con il mouse, tutto bene. Ma se lo chiama con la tastiera, allora dobbiamo fare un po' di calcoli per assicurarci che compaia in corrispondenza della posizione del cursore (e non dove si trova in quel momento il puntatore del mouse)::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          p = wx.Panel(self)
          self.text = wx.TextCtrl(p, -1, 'fai clic qui '*10, 
                                  style=wx.TE_MULTILINE, pos=((50, 50)))
          self.text.Bind(wx.EVT_CONTEXT_MENU, self.on_clic)

      def on_clic(self, evt): 
          menu = wx.Menu()
          menu.Append(-1, 'scelta uno') # i binding di queste voci
          menu.Append(-1, 'scelta due') # sono omessi per brevita'

          if evt.GetPosition() == wx.DefaultPosition:
              ins_point = self.text.GetInsertionPoint()
              correct_position = self.text.PositionToCoords(ins_point)
              self.PopupMenu(menu, pos=correct_position)
          else:
              self.PopupMenu(menu)
          menu.Destroy()

  if __name__ == '__main__':
      app = wx.App(False)
      MyFrame(None).Show()
      app.MainLoop()

.. index::
   single: menu; tecniche di manipolazione

Manipolare dinamicamente i menu. 
--------------------------------

I menu sono strumenti complessi, e wxPython mette a disposizione molti metodi per maneggiarli. Potete all'occorrenza far sparire voci di menu, aggiungerle, spostarle. E potete far sparire o cambiare allo stesso modo interi menu. 

Tuttavia diciamo subito che queste non sono tecniche da adoperare a cuor leggero. Il menu, in tutte le applicazioni, è una cosa sacra: il programmatore spende molte energie a progettarlo bene, l'utente investe molto tempo a orientarvisi; in generale ci si aspetta che ogni possibile funzione del vostro programma corrisponda a una voce di menu, da qualche parte. 

Cambiare la struttura dei menu a runtime è probabilmente sempre una cattiva idea. Per esempio, se l'utente non può accedere a certe voci, la cosa migliore è disabilitarle ma lasciarle visibili. Così l'utente può almeno capire che in seguito a certe azioni (e magari con dei permessi aggiuntivi!) potrebbe accedere a quella sezione del vostro programma. Se invece nascondete completamente la voce nel menu, l'utente potrebbe perdere un sacco di tempo a cercarla, se crede che "da qualche parte ci deve pur essere".

Proprio perché queste manovre non sono quasi mai una buona idea, non le descriveremo nel dettaglio. Potete senz'altro riferirvi alla documentazione per scoprire qualcosa di più. In particolare, la demo (cercate "menu") illustra qualche esempio di voci di menu che appaiono, scompaiono e si spostano in questo modo. 

Per rimuovere una voce di menu, chiamate ``menu.Remove(id)``, dove ``menu`` è il menu che contiene la voce, e ``id`` è l'id della voce. Allo stesso modo potete rimuovere un intero menu dalla barra del menu chiamando ``menubar.Remove(pos)``, dove ``pos`` è la posizione del menu nella barra. Notate che ``Remove`` non distrugge l'oggetto ``MenuItem`` c++ sottostante. Questo è utile se volete re-inserire la voce di menu in un secondo tempo (``Remove`` restituisce un riferimento all'oggetto rimosso: basta conservarlo in una variabile, e poi riusarlo).

Per inserire una voce in mezzo ad altre esistenti, usate ``menu.InsertItem(pos, item)``, dove ``pos`` è la posizione dell'elemento precedente a quello che volete inserire. Allo stesso modo potete inserire un menu nella barra dei menu con ``menubar.Insert(pos, menu, title)``. 

Se manipolate dinamicamente i menu, potrebbero servirvi anche le funzioni per cercare le varie voci o i vari menu. Ce ne sono diversi: ``menu.FindItem(string)`` cerca una voce di menu per la sua etichetta; ma esistono anche ``menu.FindItemById(id)`` e ``menu.FindItemByPos(position)``, con significato ovvio. Anziché rivolgersi a un menu singolo, è possibile chiedere alla barra dei menu di cercare una determinata voce, ovunque sia: per questo basta usare ``menubar.FindItemById(id)``.

Ma ci sono anche altre possibilità, che potete scoprire da soli guardando la documentazione. 

Infine, anche sul fronte degli eventi, si può andare oltre il consueto ``wx.EVT_MENU``. Esistono anche ``wx.EVT_MENU_CLOSE`` (innescato dalla chiusura di un menu), ``wx.EVT_MENU_OPEN`` (quando si apre un menu), ``wx.EVT_MENU_HIGHLIGHT`` (quando si passa col mouse sopra una voce di menu: il comportamento di default è mostrare l'"help text" del ``wx.MenuItem``), e infine ``xw.EVT_MENU_HIGHLIGHT_ALL`` (come sopra, ma innescato quando si passa col mouse sopra una voce qualsiasi: utile quando non vi interessa sapere quale voce in particolare sta scorrendo l'utente).

.. index::
   single: menu; tecniche di fattorizzazione

Come "fattorizzare" la creazione dei menu.
------------------------------------------

La creazione dei menu comporta sempre la scrittura di codice prolisso e ripetitivo (un sacco di ``menu.Append`` e così via). E' naturale cercare modi di compattare un po' queste procedure. 

Prima di tutto, un avvertimento. Si tratta di tecniche non indispensabili, e anzi, a dirla tutta poco raccomandabili. Compattare la creazione di un menu non è una vera "fattorizzazione", perché dopo tutto il codice per creare i menu serve una volta sola. Potete senz'altro dare una sforbiciata alle righe del vostro programma, se vi fa piacere. Ma non ne guadagnate in ri-usabilità (che sarebbe il vero scopo della fattorizzazione), e probabilmente ci perdete in leggibilità. 

Detto questo, chiaramente non è sbagliato trarre vantaggio dalla strumentazione standard di python. Per esempio, dopo aver scritto dieci volte di seguito ``menu.Append``, anche un programmatore python alle prime armi troverebbe naturale usare un ciclo ``for``::

  for label in ('Topolino, 'Paperino', Qui', 'Quo', 'Qua'):
      menu.Append(-1, label)

E siccome abbiamo visto che gli id possono essere importanti, meglio ancora::

  for n, lab in enumerate(('Topolino, 'Paperino', Qui', 'Quo', 'Qua')):
      menu.Append(100+n, lab) # assegno id dal 100 in poi...

E perché fermarci qui? Se vogliamo offrire il servizio completo possiamo anche integrare il binding degli eventi::

  labels = ('Qui', 'Quo', 'Qua')
  events = (self.on_qui, self.on_quo, self.on_qua)
  for lab, evt in zip(labels, events):
      item = menu.Append(-1, lab)
      self.Bind(wx.EVT_MENU, evt, item)

E potete andare avanti a personalizzare e rendere più smaliziato il vostro codice in mille modi diversi. Per esempio, vi verrà in mente che invece della tupla di etichette potete anche scrivere::

  labels = 'Topolino Paperino Qui Quo Qua'.split()

risparmiando qualche battuta e sentendovi in questo modo dei veri hacker. E così via. 

Il gradino successivo è pensare di scrivere una funzione separata che riceva come argomento un po' di etichette, e sputi fuori un ``wx.Menu`` già bello pronto per essere attaccato alla sua ``wx.MenuBar``. Se vi piace la terminologia dei design pattern, questa si chiamerebbe una "funzione factory". Ovviamente i menu possono contenere dei sotto-menu, e così via: di conseguenza, progettare una factory di creazione dei menu può essere un piacevole esercizio per imparare le funzioni ricorsive. 

Ciascuno può divertirsi a scrivere la sua variante personalizzata. Ecco una traccia da cui partire::

  def make_menu(items):
      menu = wx.Menu()
      for item in items:
          if isinstance(item, list):  # questo e' un sotto-menu
              menu.AppendMenu(-1, item[0], make_menu(item[1:]))
          elif item == '':
              menu.AppendSeparator()
          else:
              menu.Append(-1, item)
      return menu

Questa funzione prende come parametro una lista di elementi. Per ciascuno, se si tratta di una stringa aggiunge una voce al menu; se si tratta invece di un'altra lista, aggiunge un sotto-menu con il nome del primo elemento, e procede a chiamare se stessa ricorsivamente con gli altri elementi. Ecco un esempio di utilizzo:: 

  menuitems = ['Voce 1', 'Voce 2', '', 'Voce 3', 
               ['Sub-menu', 'Sub-voce 1', 'Sub-voce 2'], 'Voce 4']
  menu = make_menu(menuitems)
  menubar.Append(menu)

Naturalmente questa funzione, così com'è, non serve a molto: restituisce un menu pieno di voci di cui non conosciamo l'id, e non abbiamo altri modi per collegare gli eventi. 

Non è difficilissimo modificare questa prima versione per tener conto anche degli eventi: la funzione potrebbe ricevere anche degli id, o addirittura già i nomi dei callback da collegare; oppure potrebbe assegnare gli id secondo un pattern ricostruibile a posteriori. 

Poi però la funzione sarebbe ancora molto limitata: non tiene conto di scorciatoie e acceleratori. Andrebbe arricchita.

E poi la funzione non tiene anche conto che alcune voci potrebbero essere inizialmente disabilitate. Bisognerebbe modificarla. 

E le voci spuntabili e i blocchi "radio"? Ehm, vanno calcolati anche loro.

Dopo un po', è facile perdere il filo. Tanto più cercate di generalizzare il problema, tanto più vi trovate a dover scrivere un'intera libreria (con i suoi problemi di architettura, i bachi, i test...). E nel frattempo, il vostro programma iniziale è sempre lì che aspetta di essere scritto. Inoltre, come abbiamo già detto, la fase di creazione dei menu avviene in genere una volta sola nel vostro programma. Fino a che punto vale la pena di fattorizzare questo codice?

Ciascuno è libero di spingere questo esercizio fin dove crede. Se volete un esempio più completo di "fattorizzazioni" eleganti ma di discutibile utilità pratica, potete guardare negli esempi tratti dal libro "wxPython in Action" (che trovate nella documentazione: ``.../wxPython2.8 Docs and Demos/wxPython/samples/wxPIA_book``). Nella directory del Capitolo 5 trovate due file ``badExample.py`` e ``goodExample.py`` che mostrano la stessa interfaccia prima e dopo la fattorizzazione (dei menu e non solo). 

Alla fine della giornata, comunque, vi renderete conto che i veri problemi con i menu non vengono fuori al momento della loro creazione, ma in seguito, durante il ciclo di vita della vostra applicazione. I menu crescono facilmente fino a diventare sistemi complessi, e mantenere sempre aggiornato e coerente il loro stato è difficile. A seconda dei casi, le varie voci vanno abilitate e disabilitate, spuntate, resettate... Spesso finite per costruire una rete intricata di ``Enable(True)`` e ``Enable(False)`` nei vari callback, che diventa rapidamente ingestibile. 

La vera sfida di "fattorizzazione" dei menu, quindi, è di trovare una forma pratica per separare la logica di business e la logica di presentazione del vostro sistema di menu. Spesso la cosa migliore è costruire un "model" dei vostri menu (una classe separata che incorpora una struttura ad albero, per esempio) capace di tener traccia dello status di ciascuna voce, di calcolare gli aggiornamenti a seconda degli eventi che riceve, e di comunicare a sua volta questi cambiamenti alla gui. 

Anche in questo caso, tuttavia, non è il caso di perdere troppo tempo nello sforzo di generalizzare e prevedere tutte le possibilità in anticipo. Partite da una soluzione rudimentale che si adatta alla vostra situazione, e poi apportate miglioramenti man mano che vi servono. 

.. todo:: una pagina su mvc.
