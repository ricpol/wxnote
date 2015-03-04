.. _menu_basi:

.. index::
   single: menu
   
   
I menu: le basi da sapere.
==========================

I menu non sono difficili, almeno per gli aspetti di base. Difficile è organizzarli in modo efficiente, compatto, intuitivo per l'utente... quante volte avete perso tempo a cercare la funzionalità che vi serve tra le decine di voci di menu di una gui? Ci sarebbe molto da parlare sul problema dell'usabilità dei menu... ma non qui, e non oggi! 

In questa pagina ci limiteremo alle informazioni tecniche di base, rimandando a un'altra volta gli argomenti più avanzati. 

.. index::
  single: wx; MenuBar

Come creare una barra dei menu.
-------------------------------

Dei tre :ref:`contenitori <contenitori>` - base (finestre, dialoghi e panel), i menu possono essere usati solo con le finestre, ossia i ``wx.Frame``. In particolare, i dialoghi (``wx.Dialog``) non possono avere menu, e non avrebbe senso: se il vostro dialogo è abbastanza complicato da aver bisogno di menu per orientare l'utente, scrivete un normale frame, invece. 

I menu si creano tipicamente nell'``__init__`` della classe del vostro frame, e si mostrano già completi agli utenti quando si mostra il frame. Aggiungere o modificare i menu in seguito è una pessima idea (piuttosto, potete abilitare e disabilitare singole voci o interi menu). 

I menu "vivono" nella barra dei menu, che come sicuramente sapete è la "striscia" subito sotto la barra del titolo della vostra finestra. La barra dei menu è direttamente figlia del frame che la ospita, e non può essere figlia di niente altro (per esempio, non del panel "principale" che farete per quella finestra). 

Creare una barra dei menu è facilissimo, basta istanziare la classe ``wx.MenuBar`` e assegnarla successivamente al frame usando il metodo ``SetMenuBar``::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menubar = wx.MenuBar()
          # qui creo i vari menu... 
          # e infine:
          self.SetMenuBar(menubar)

  app = wx.App(False)
  MyFrame(None).Show()
  app.MainLoop()

Se provate questo codice, vedrete un normale frame con una barra dei menu pronta, ma ancora vuota. Notate che il nome della barra dei menu (``menubar``) serve solo localmente nell'``__init__`` della classe: per questo motivo non abbiamo bisogno di chiamarla ``self.menubar``. 

.. index::
  single: wx; Menu

Come creare i menu.
-------------------

Ogni menu è una istanza della classe ``wx.Menu``. Dopo la sua creazione, un ``wx.Menu`` può essere popolato con le varie voci che deve contenere. Infine, viene attaccato alla barra dei menu, usando il metodo ``wx.MenuBar.Append`` come vedremo subito. Tuttavia, un menu può essere agganciato anche a un altro menu già esistente, formando in questo modo un sotto-menu. 

Espandiamo un poco l'esempio di sopra::

  # ... come sopra...
  menubar = wx.MenuBar()

  mymenu = wx.Menu()  # creo un menu
  # qui aggiungo le voci del menu, e infine...
  menubar.Append(mymenu, 'PrimoMenu')

  mymenu = wx.Menu()  # creo un altro menu
  # qui aggiungo le voci del menu, e infine...
  menubar.Append(mymenu, 'SecondoMenu')

  self.SetMenuBar(menubar)
  # ... segue come sopra...

Se adesso fate girare l'esempio di prima con quese aggiunte, vedrete che la barra dei menu si è popolata di due menu ("PrimoMenu" e "SecondoMenu"), ancora senza nessun elemento. Noterete anche che il "titolo" dei menu è assegnato solo al momento di agganciarlo alla barra dei menu. 

Osservate poi che anche i nomi dei singoli menu servono solo all'interno dell'``__init__``, quindi non c'è bisogno di nessun ``self`` davanti. Anzi, effettivamente il nome di un menu serve solo fino al momento di aggangiarlo alla barra dei menu; per questo motivo possiamo riciclare senza scrupoli il nome generico ``mymenu`` per tutti quelli che stiamo creando.

Infine, notate che i vari menu compaiono nella barra (da sinistra a destra) nell'ordine in cui li avete agganciati. A dire il vero ``wx.MenuBar``, oltre ad ``Append``, offre anche un metodo ``Insert`` per inserire un menu in una posizione arbitraria: tuttavia la cosa più facile e naturale è collocare i vari menu nell'ordine giusto usando solo ``Append``.

.. _creare_voci_menu:

.. index::
  single: wx; MenuItem
  single: wx.Menu; Append

Come creare le voci di menu.
----------------------------

Una voce di menu è semplicemente il risultato del metodo ``Append`` applicato a un ``wx.Menu``. Per esempio::

  menu = wx.Menu()
  menu.Append(-1, "prima voce")
  menu.Append(-1, "seconda voce")
  menu.Append(-1, "terza voce")

inserisce tre voci di menu in un menu. Ma vediamo un po' più da vicino come funziona questa magia.

Il secondo argomento di ``Append``, come avrete capito, è l'etichetta che l'utente vedrà effettivamente nel menu. Il primo argomento, invece, è un id univoco: abbiamo già visto :ref:`che cosa sono gli id <gli_id>`, e che passare ``-1`` vuol dire lasciare che wxPython gestisca da solo la creazione di un nuovo id.

``Append`` ha altri due argomenti opzionali: il terzo è una stringa che, se inserita, appare come "help text" (di solito come un tooltip, ma può dipendere dalle piattaforme). Il quarto è un flag che indica il tipo di voce di menu che stiamo inserendo (il valore di default è ``wx.ITEM_NORMAL``, ma ne parleremo :ref:`un'altra volta<menu_basi2>`).

Il metodo ``Append`` restituisce un oggetto che rappresenta la voce di menu appena inserita nel menu. In genere dobbiamo conservare questo riferimento in una variabile, se vogliamo poi collegare questa voce di menu a un evento (ossia, vogliamo fare qualcosa quando l'utente fa clic su di essa). Riscriviamo quindi il nostro esempio iniziale, fino a popolare i nostri menu con qualche voce:: 

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menubar = wx.MenuBar()

          mymenu = wx.Menu()  # creo un menu, e lo popolo:
          item1 = mymenu.Append(-1, 'voce uno')
          item2 = mymenu.Append(-1, 'voce due')
          menubar.Append(mymenu, 'PrimoMenu')

          mymenu = wx.Menu()  # creo un altro menu...
          item3 = mymenu.Append(-1, 'voce tre')
          item4 = mymenu.Append(-1, 'voce quattro')
          item5 = mymenu.Append(-1, 'voce cinque')
          menubar.Append(mymenu, 'SecondoMenu')

          self.SetMenuBar(menubar)

          # adesso non dobbiamo scordarci di collegare le voci di menu
          # item1, item2, etc., a degli eventi! 


  app = wx.App(False)
  MyFrame(None).Show()
  app.MainLoop()

Se provate questo esempio, osserverete che i nostri menu si sono popolati con qualche voce. Ancora una volta, ``item1``, ``item2`` etc. sono nomi che ci servono solo localmente, quindi non è il caso di farli precedere da un ``self``. 

Naturalmente le voci di menu sono ancora inerti: se ci fate clic sopra, non succede nulla. Manca ancora il collegamento con gli eventi. Ci arriviamo subito: prima però, abbiamo ancora un paio di punti in sospeso. 

.. index::
  single: wx.Menu; AppendSeparator

Come creare un separatore.
--------------------------

Questo è davvero facile: basta usare ``AppendSeparator`` invece di ``Append``. Per esempio::

          mymenu = wx.Menu()  
          item3 = mymenu.Append(-1, 'voce tre')
          item4 = mymenu.Append(-1, 'voce quattro')
          mymenu.AppendSeparator()  # un separatore
          item5 = mymenu.Append(-1, 'voce cinque')
          menubar.Append(mymenu, 'SecondoMenu')

.. index::
  single: menu; sottomenu
  single: wx.Menu; AppendMenu

Come creare un sotto-menu.
--------------------------

Come abbiamo già accennato, un sotto-menu non è altro che un normale ``wx.Menu`` agganciato a un altro menu, invece che alla barra dei menu. ``wx.Menu`` dispone infatti di un metodo ``AppendMenu`` che fa proprio questo lavoro. 

Lavoriamo ancora sul nostro esempio, e questa volta aggiungiamo un sotto-menu che inseriamo tra gli elementi del secondo menu::


  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menubar = wx.MenuBar()

          mymenu = wx.Menu()  # creo un menu, e lo popolo:
          item1 = mymenu.Append(-1, 'voce uno')
          item2 = mymenu.Append(-1, 'voce due')
          menubar.Append(mymenu, 'PrimoMenu')

          submenu = wx.Menu() # ecco il sotto-menu!
          item10 = submenu.Append(-1, 'voce uno del submenu')
          item11 = submenu.Append(-1, 'voce due del submenu')

          mymenu = wx.Menu()  # adesso creo il secondo menu...
          item3 = mymenu.Append(-1, 'voce tre')
          item4 = mymenu.Append(-1, 'voce quattro')
          # ... e aggancio qui il sotto-menu:
          mymenu.AppendMenu(-1, "ecco un sotto-menu", submenu)
          # quindi proseguo con le altre voci del menu
          item5 = mymenu.Append(-1, 'voce cinque')
          menubar.Append(mymenu, 'SecondoMenu')

          self.SetMenuBar(menubar)

Adesso il secondo menu integra anche il nostro sotto-menu tra i suoi elementi. Notate che ``AppendMenu`` vuole (naturalmente!) un argomento in più, rispetto al normale ``Append``. 

Notate anche che non abbiamo conservato in una variabile il riferimento al nodo di inserimento. Non abbiamo cioè scritto, per esempio::

  item6 = mymenu.AppendMenu(-1, "ecco un sotto-menu", submenu)

Questo è ciò che si fa in genere: non ci serve dargli un nome, perché non abbiamo bisogno di collegare questo nodo a un evento. Quando l'utente fa clic qui, ci basta il comportamento di default gestito da wxPython (ovvero, aprire le voci del sotto-menu). Tuttavia, se volessimo far succedere qualcosa di diverso, potremmo collegare anche questo nodo a un evento, come qualsiasi altro elemento. 

.. index::
  single: wx; EVT_MENU

Collegare le voci di menu a eventi.
-----------------------------------

Ed eccoci al punto finale: dopo aver creato i vostri menu, bisogna fargli fare qualcosa!

.. note:: Quanto segue presuppone che sappiate già che cosa sono gli eventi, e come utilizzarli. In caso contrario, date prima :ref:`un'occhiata qui<eventibasi>`, e poi proseguite :ref:`con questo<eventi_avanzati>`.

Quando l'utente fa clic su una voce di menu, genera un ``wx.EVT_MENU``, che è un ``CommandEvent`` intercettabile nel frame "parent" (quello dove definite il menu, per intenderci).

La tecnica è quella solita che useremmo, per esempio, con un pulsante::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menubar = wx.MenuBar()

          mymenu = wx.Menu()
          item1 = mymenu.Append(-1, 'voce uno')
          item2 = mymenu.Append(-1, 'voce due')
          menubar.Append(mymenu, 'PrimoMenu')

          submenu = wx.Menu()
          item10 = submenu.Append(-1, 'voce uno del submenu')
          item11 = submenu.Append(-1, 'voce due del submenu')

          mymenu = wx.Menu()
          item3 = mymenu.Append(-1, 'voce tre')
          item4 = mymenu.Append(-1, 'voce quattro')
          mymenu.AppendMenu(-1, "ecco un sotto-menu", submenu)
          item5 = mymenu.Append(-1, 'voce cinque')
          menubar.Append(mymenu, 'SecondoMenu')

          self.SetMenuBar(menubar)

          # collego ogni singola voce a un callback
          self.Bind(wx.EVT_MENU, self.on_clic_item1, item1)
          self.Bind(wx.EVT_MENU, self.on_clic_item2, item2)
          self.Bind(wx.EVT_MENU, self.on_clic_item3, item3)
          self.Bind(wx.EVT_MENU, self.on_clic_item4, item4)
          self.Bind(wx.EVT_MENU, self.on_clic_item5, item5)
          self.Bind(wx.EVT_MENU, self.on_clic_item10, item10)
          self.Bind(wx.EVT_MENU, self.on_clic_item11, item11)

      # e scrivo i relativi callback
      def on_clic_item1(self, evt): print 'clic su voce uno'
      def on_clic_item2(self, evt): print 'clic su voce due'
      def on_clic_item3(self, evt): print 'clic su voce tre'
      def on_clic_item4(self, evt): print 'clic su voce quattro'
      def on_clic_item5(self, evt): print 'clic su voce cinque'
      def on_clic_item10(self, evt): print 'clic su voce uno del submenu'
      def on_clic_item11(self, evt): print 'clic su voce due del submenu'

E' solo ordinaria amministrazione, se sapete come si gestiscono gli eventi. L'unica cosa interessante da notare, è che abbiamo adottato il "secondo" stile di binding (dei tre che :ref:`avevamo identificato<tre_stili_di_bind>`). Non possiamo infatti scrivere::

  item1.Bind(wx.EVT_MENU, self.on_clic_item1) # etc. etc.

perché in effetti una voce di menu non è un event handler di per sé, e quindi non ha un metodo ``Bind``. Siamo quindi obbligati a collegare il frame stesso (``self.Bind``), e specificare poi la voce di menu che desideriamo collagare passandola come argomento di ``Bind``. 

Come già accennato, questo è l'unico momento in cui effettivamente utilizziamo i nomi che abbiamo assegnato alle voci di menu (ossia le variabili ``item1``, ``item2``, etc.). Per tenere insieme il momento di creazione della voce di menu e il suo collegamento a un callback, spesso è più comodo scrivere::

  mymenu = wx.Menu()
  item1 = mymenu.Append(-1, 'voce uno')
  self.Bind(wx.EVT_MENU, self.on_clic_item1, item1)
  item2 = mymenu.Append(-1, 'voce due')
  self.Bind(wx.EVT_MENU, self.on_clic_item2, item2)
  # etc etc

e questo ci porta a un passo dal compattare ulteriormente::

  mymenu = wx.Menu()
  self.Bind(wx.EVT_MENU, self.on_clic_item1, mymenu.Append(-1, 'voce uno'))
  self.Bind(wx.EVT_MENU, self.on_clic_item2, mymenu.Append(-1, 'voce due'))
  # etc etc

E in questo modo eliminiamo completamente la necessità di mantenere i riferimenti a ``item1``, ``item2`` etc. 

Conclusione.
------------

Con queste informazioni dovreste essere in grado di creare e gestire almeno i casi più comuni. Ci sono tuttavia molte altre cose da dire sui menu: :ref:`continuate a leggere!<menu_basi2>`

