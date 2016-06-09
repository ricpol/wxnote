.. _menu_basi2:

.. index::
   single: menu
   
   
I menu: altri concetti di base.
===============================

Questa seconda parte sui menu segue direttamente la :ref:`precedente <menu_basi>`. Dopo la panoramica sui concetti fondamentali, raccogliamo qui "in ordine sparso" alcune altre tecniche che dovreste conoscere per essere pronti a usare i menu nel mondo reale. Dedichiamo invece una :ref:`pagina separata <menu_avanzate>` per le tecniche un po' più avanzate. 

Scorciatoie da tastiera.
------------------------

Nessun vero menu potebbe dirsi completo senza le scorciatoie da tastiera! wxPython vi permette di utilizzare entrambe le tecniche classiche: le scorciatoie e gli "acceleratori". 

.. index::
  single: menu; scorciatoie

Come creare una scorciatoia.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le scorciatoie sono le lettere sottolineate nei menu, a cui si accede attraverso il tasto "alt". Se volete "sottolineare" una lettera in una voce di menu (ossia, creare una scorciatoia per quella lettera), basta premettere una ``&``::

  item1 = menu.Append(-1, 'Inc&olla')

Questo per esempio crea una scorciatoia per la "o" di "Incolla" (che apparirà sottolineata). Naturalmente, se avete bisogno di scrivere una "&" nella vostra voce di menu, dovete fare l'escape e scrivere ``&&``. Se avete bisogno di creare una scorciatoia proprio per la "&" allora... non so, non ci ho mai provato e non dovreste neanche voi. 

Una particolarità importante: se decidete di fornire scorciatoie per le vostre voci di menu, ricordatevi che ogni "nodo" che porta a quella voce deve avere la sua scorciatoia: questo perché la prima pressione di "Alt+lettera" aprirà il menu, poi si aprono gli eventuali sottomenu, fino a trovare la voce esatta. Se non è possibile fare il percorso completo con la tastiera, non sarà possibile attivare la vostra scorciatoia. Quindi::

    menu = wx.Menu()
    item1 = menu.Append(-1, 'Inc&olla')  # se creo questa scorciatoia...
    # ...
    menubar.Append(menu, "&Miomenu")   # ... devo farne una nel nodo precedente!

Infine, naturalmente, dovete fare attenzione a rendere le scorciatoie uniche (almeno nell'ambito di un menu). La politica consueta è di "sottolineare" sempre la prima lettera, e passare alla seconda/terza lettera solo in caso di conflitto. 

Una volta era considerato essenziale fornire le scorciatoie da tastiera, se non proprio per tutte le voci di tutti i menu, almeno per quelle più importanti. Oggi non è più così imprescindibile: si è capito che gli utenti alla fine le usano poco, e preferiscono piuttosto memorizzare gli "acceleratori" più comuni. 

.. index::
  single: menu; acceleratori
  single: menu; wx.StripMenuCodes
  single: wx.StripMenuCodes

Come creare un acceleratore.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Gli acceleratori sono quelle combinazioni con due o tre tasti ("ctrl+alt+tasto", e così via) che eseguono direttamente un'azione senza la necessità di aprire un menu. Per esempio, in genere "Ctrl+S" serve per "salvare", "Ctrl+O" serve per "aprire", "Ctrl+C" per "copiare" e "Ctrl+V" per "incollare" (qualsiasi cosa voglia dire nella logica della vostra applicazione!). All'interno dei menu, gli acceleratori sono sempre scritti accanto alla voce corrispondente. 

A dire il vero gli acceleratori sono definiti a livello globale nella vostra applicazione, e potete usarli anche al fuori dei menu (e perfino se non usate nessun menu!). Tuttavia è molto comune usarli in accoppiata con i menu, e in effetti c'è un modo facilissimo per integrare acceleratori e menu in wxPython: basta aggiungere all'etichetta della voce la sequenza ``\tModificatore+Tasto``. Per esempio:: 

  menu = wx.Menu()
  item1 = menu.Append(-1, 'Salva\tCtrl+s')
  item1 = menu.Append(-1, 'Salva con nome\tCtrl+Shift+s')
  item3 = menu.Append(-1, 'Chiudi\tAlt+F4') # ehm... in Windows ;-)

E' perfettamente possibile usare insieme acceleratori e scorciatoie::

  item1 = menu.Append(-1, '&Salva\tCtrl+s')

Occasionalmente potrebbe servirvi la funzione globale ``wx.StripMenuCodes`` per ottenere la voce di menu "depurata" dai vari simboli extra::

  >>> wx.StripMenuCodes('&Salva\tCtrl+s')
  u'Salva'

Ricordatevi che gli acceleratori sono globali in tutta la vostra applicazione, e quindi devono essere unici: non potete definire lo stesso acceleratore per due azioni diverse, anche se si trovano in menu differenti. 

Cercate di fornire acceleratori coerenti con le normali consuetudini: non definite "Ctrl+V" per "Valutare" un film, anche se state scrivendo un software di recensioni cinematografiche. Se la vostra applicazione non ha bisogno di azioni standard come aprire, salvare, copiare, incollare... non cercate comunque di riciclare questi acceleratori per i vostri scopi: gli utenti sono abituati a usare "Ctrl+o" con il significato di "aprire", e non vogliono dover memorizzare una convenzione alternativa valida solo per il vostro programma. 

Viceversa, se la vostra applicazione prevede azioni standard, ricordatevi di fornire gli accelerati standard corrispondenti: gli utenti se lo aspettano. 

Un tocco di classe: fornite gli acceleratori più comuni nelle diverse piattaforme. Per esempio, "chiudere" un programma è "Alt+F4" in Windows, "Cmd+Q" nel Mac. Potete testare a runtime la piattaforma in uso, ricorrendo per esempio a ``wx.Platform`` (o anche, naturalmente, a ``sys.platform`` della libreria standard di Python):: 

  accel = {'__WXMSW__': '\tAlt+F4', 
           '__WXMAC__': '\tCtrl+Q'}[wx.Platform]
  menu.Append(-1, 'Esci'+accel)

Notate che wxPython sul Mac traduce il "Ctrl" automaticamente in "Cmd" quindi non dovete preoccuparvi di questo dettaglio. Con questa agevolazione, di fatto la stragrande maggioranza degli acceleratori sono identici tra le varie piattaforme: potete regolarvi con `questa pagina di Wikipedia <http://en.wikipedia.org/wiki/Table_of_keyboard_shortcuts>`_. Diventa più complesso se volete tener conto delle abitudini nazionali: per esempio, "trova" può diventare "Ctrl+T" in italiano.

.. index::
  single: wx.AcceleratorTable
  single: wx.AcceleratorEntry
  single: menu; wx.AcceleratorTable
  single: menu; wx.AcceleratorEntry

Creare un acceleratore senza legarlo a una voce di menu.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Siccome qui stiamo parlando di menu, questa parte è un po' fuori tema: la inseriamo ugualmente per completezza. 

Come abbiamo già accennato, gli acceleratori possono essere definiti anche indipendentemente dai menu (o addirittura in assenza di menu). La procedura però è un po' più complicata. 

Occorre prima di tutto istanziare una ``wx.AcceleratorTable``, che è semplicemente un contenitore di uno o più ``wx.AcceleratorEntry``. Il codice da scrivere sarebbe quindi qualcosa come:: 

  table = wx.AcceleratorTable([wx.AcceleratorEntry(......), 
                               wx.AcceleratorEntry(......), 
                               wx.AcceleratorEntry(......)])

wxPython tuttavia ci permette di usare una più semplice lista di tuple (la conversione a oggetti ``wx.AcceleratorEntry`` viene fatta in automatico). Possiamo quindi scrivere::

  table = wx.AcceleratorTable([(......),
                               (......), 
                               (......)])

Una volta descritte la tabella, è necessario infine assegnarla usando ``self.SetAcceleratorTable(table)`` (dove ``self`` è la finestra corrente).

Un ``wx.AcceleratorEntry``, a sua volta, deve essere costruito con tre parametri. 

- Il primo è una :ref:`bitmask <cosa_e_bitmask>` che compone i tasti di controllo che devono essere premuti. La scelta è tra: 

 + ``wx.ACCEL_NORMAL`` (nessun modificatore)
 
 + ``wx.ACCEL_ALT`` 

 + ``wx.ACCEL_SHIFT`` 
 
 + ``wx.ACCEL_CTRL`` ("Ctrl", oppure "Cmd" sul Mac)
 
 + ``wx.ACCEL_RAW_CTRL`` ("Ctrl" sempre, anche sul Mac)

- Il secondo è il keycode del tasto da associare (semplicemente ``ord(key)``)

- Il terzo è l'id del widget che emette il ``wx.CommandEvent`` che vogliamo innescare. 

Questo ultimo parametro ci svela finalmente la vera natura degli acceleratori: si tratta semplicemente di un modo rapido per simulare un clic su un widget. Basta che nell'interfaccia sia presente un widget in grado di emettere un ``wx.CommandEvent`` (per esempio un pulsante), e possiamo simularne la pressione per innescare il callback associato. 

In questo esempio, che riassume tutto quello che abbiamo detto fin qui, troviamo due pulsanti collegati ad altrettanti acceleratori:: 

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)
          p = wx.Panel(self)

          a_button = wx.Button(p, -1, 'pulsante a', pos=((10, 10)))
          b_button = wx.Button(p, -1, 'pulsante b', pos=((10, 50)))

          a_button.Bind(wx.EVT_BUTTON, self.on_a_button)
          b_button.Bind(wx.EVT_BUTTON, self.on_b_button)

          table = wx.AcceleratorTable(
                    [(wx.ACCEL_CTRL, ord('t'), a_button.GetId()), 
                    (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('t'), b_button.GetId())]
                   )
          self.SetAcceleratorTable(table)

      def on_a_button(self, evt): print "evento a"
      def on_b_button(self, evt): print "evento b"

  if __name__ == '__main__':
      app = wx.App(False)
      MyFrame(None).Show()
      app.MainLoop()
 
Certamente possiamo usare una ``wx.AcceleratorTable`` anche per creare acceleratori legati alle voci di menu, all'occorrenza:: 

  item1 = menu.Append(-1, 'Salva')
  #...
  table = wx.AcceleratorTable(
                [(wx.ACCEL_CTRL, ord('s'), item1.GetId())]
                )
      self.SetAcceleratorTable(table)

Ma oltre a essere più complesso del modo facile visto prima, così non otteniamo automaticamente di inserire lo shortcut dell'acceleratore accanto all'etichetta della voce del menu. 

Infine, naturalmente, niente ci vieta di associare una voce di menu e (per esempio) un pulsante allo stesso callback, e per buona misura usare un acceleratore per entrambi. In questo scenario conviene naturalmente associare l'acceleratore alla voce di menu con il metodo rapido visto prima: quando l'utente digita la combinazione di tasti ottiene comunque l'effetto desiderato, non importa se il clic è simulato sul menu o sul pulsante::

  b = wx.Button(self, -1, 'Salva')
  b.Bind(wx.EVT_BUTTON, self.on_clic)
  # ...
  item1 = menu.Append(-1, '&Salva\tCtrl+s') # acceleratore!
  self.Bind(wx.EVT_MENU, self.on_clic, item1)  # bind allo stesso callback
  #...

  def on_clic(self, evt): print 'stiamo salvando...'

.. index::
  single: menu; abilitare e disabilitare
  single: wx.MenuBar; EnableTop
  single: wx.MenuBar; IsEnabledTop
  single: menu; wx.MenuBar.EnableTop
  single: menu; wx.MenuBar.IsEnabledTop

Disabilitare i menu.
--------------------

Come praticamente tutti i widget di wxPython, anche le voci di menu hanno un metodo ``Enable`` che consente di abilitarli e disabilitarli, e un metodo ``IsEnabled`` per scoprire il loro stato attuale. Naturalmente, per fare questo dovete accedere alle singole voci al di fuori dell'``__init__``, e pertanto dovete conservare un riferimento in una variabile di istanza (con il ``self`` davanti, per capirci). 

Disabilitare un intero menu è più faticoso, perché ``wx.Menu`` non dispone di un metodo ``Enable``. Occorre passare per ``wx.MenuBar.EnableTop``. Questo metodo accetta due parametri: 

- la posizione del menu che voglaimo (a partire da 0 per il primo);

- un boolean per dire se il menu deve essere abilitato o disabilitato. 

Purtroppo quindi ci tocca conoscere la posizione del menu che ci interessa nella barra dei menu. Possiamo conservarla in una variabile al momento della creazione, oppure scoprirla in seguito con ``wx.MenuBar.FindMenu`` che accetta il nome del menu e restituisce il suo indice. 

La controparte di ``wx.MenuBar.EnableTop`` per scoprire se un menu è attualmente abilitato, è ``wx.MenuBar.IsEnabledTop``, con un costruttore analogo. 

Ecco un esempio pratico che mette insieme tutto questo:: 

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menu_A = wx.Menu()
          # teniamo un riferimento per questa voce di menu
          self.voce_salva = menu_A.Append(-1, 'Salva') 
          menu_A.Append(-1, 'Apri')
          menu_A.Append(-1, 'Chiudi')

          menu_B = wx.Menu()
          menu_B.Append(-1, 'Qui')
          menu_B.Append(-1, 'Quo')
          menu_B.Append(-1, 'Qua')
          
          menubar = wx.MenuBar()
          menubar.Append(menu_A, 'File')
          menubar.Append(menu_B, 'Paperi')
          self.SetMenuBar(menubar)

          # conserviamo un riferimento alla menubar:
          self.menubar = menubar

          # ricordiamo l'indice della posizione del menu_B nella menubar, 
          # se non preferiamo scoprirlo in seguito:
          self.menu_B_position = 1

          p = wx.Panel(self)

          a_button = wx.Button(p, -1, '(dis)abilita Salva', pos=((10, 10)))
          b_button = wx.Button(p, -1, '(dis)abilita menu Paperi', pos=((10, 50)))

          a_button.Bind(wx.EVT_BUTTON, self.on_a_button)
          b_button.Bind(wx.EVT_BUTTON, self.on_b_button)

      def on_a_button(self, evt): 
          # dis/abilito la voce "salva" a seconda del suo stato corrente
          self.voce_salva.Enable(not self.voce_salva.IsEnabled())

      def on_b_button(self, evt):
          # siccome abbiamo conservato l'indice della posizione del menu_B, 
          # possiamo usare direttamente quello. 
          # In alternativa, possiamo scoprirlo in questo modo:
          # self.menu_B_position = self.menubar.FindMenu("Paperi")
          is_enabled = self.menubar.IsEnabledTop(self.menu_B_position)
          self.menubar.EnableTop(self.menu_B_position, not is_enabled)
        
  if __name__ == '__main__':
      app = wx.App(False)
      MyFrame(None).Show()
      app.MainLoop()

.. index::
  single: menu; spuntabili e selezionabili
  single: wx.ITEM_* (nei menu)
  single: wx.MenuItem; IsChecked
  single: wx.MenuItem; Check
  single: menu; wx.MenuItem.IsChecked
  single: menu; wx.MenuItem.Check
  single: menu; wx.ITEM_*

Voci di menu spuntabili o selezionabili.
----------------------------------------

Ecco un'altra necessità piuttosto comune: i menu servono anche per fare delle scelte tra diverse opzioni, e per questo ci sono tradizionalmente due possibilità: 

- le voci di menu con la "spunta", per possono essere de/selezionate individualmente;

- le voci di menu di tipo "radio", presentate in gruppi all'interno dei quali è possibile selezionarne solo una alla volta. 

wxPython supporta entrambe le possibilità. Le voci "spuntabili" si ottengono aggiungendo il flag ``wx.ITEM_CHECK`` al normale metodo ``Append``. Le voci "radio" si ottengono aggiungendo il flag ``wx.ITEM_RADIO``. Più voci "radio" in successione si considerano parte di un gruppo. Un gruppo finisce quando si inserisce una voce non-radio (o un separatore). 

Ricordatevi che il flag ``wx.ITEM_*`` è il quarto argomento del metodo ``Append``, :ref:`come abbiamo già visto<creare_voci_menu>`: il terzo è la stringa di "help text" che spesso si lascia vuota). 

Ecco un esempio per chiarire le cose dette fin qui::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menu = wx.Menu()
          menu.Append(-1, 'una voce normale')
          menu.Append(-1, 'spunta uno', '', wx.ITEM_CHECK)
          menu.Append(-1, 'spunta due', '', wx.ITEM_CHECK)
          menu.Append(-1, 'spunta tre', '', wx.ITEM_CHECK)
          # qui inizia un radio-group
          menu.Append(-1, 'radio uno', '', wx.ITEM_RADIO)
          menu.Append(-1, 'radio due', '', wx.ITEM_RADIO)
          menu.Append(-1, 'radio tre', '', wx.ITEM_RADIO)
          menu.AppendSeparator()
          # qui inizia un nuovo radio-gruppo
          menu.Append(-1, 'altro radio uno', '', wx.ITEM_RADIO)
          menu.Append(-1, 'altro radio due', '', wx.ITEM_RADIO)

          menubar = wx.MenuBar()
          menubar.Append(menu, 'Menu')
          self.SetMenuBar(menubar)

  if __name__ == '__main__':
      app = wx.App(False)
      MyFrame(None).Show()
      app.MainLoop()

Naturalmente potete collegare queste voci di menu "speciali" agli eventi come fareste di solito. Il ``wx.CommandEvent`` propagato da una voce di menu porta con sé un metodo ``IsChecked`` che potete interrogare per sapere se l'utente ha appena spuntato la voce su cui ha fatto clic (questo in teoria funziona anche con le voci "radio", ma in pratica non serve a niente: se l'utente fa clic su una voce "radio", questo vuol già dire che l'ha selezionata).

In alternativa, potete sapere in qualunque momento lo stato di una di queste voci interroganto il metodo ``IsChecked`` del ``MenuItem``. E naturalmente potete anche manipolare voi stessi lo stato di questi elementi, usando ``Check``. 

Ecco l'esempio di prima modificato per mostrare anche queste possibilità::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menu = wx.Menu()
          self.spunta_uno = menu.Append(-1, 'spunta uno', '', wx.ITEM_CHECK)
          self.spunta_due = menu.Append(-1, 'spunta due', '', wx.ITEM_CHECK)
          self.spunta_tre = menu.Append(-1, 'spunta tre', '', wx.ITEM_CHECK)
          self.radio_uno = menu.Append(-1, 'radio uno', '', wx.ITEM_RADIO)
          self.radio_due = menu.Append(-1, 'radio due', '', wx.ITEM_RADIO)
          self.radio_tre = menu.Append(-1, 'radio tre', '', wx.ITEM_RADIO)

          self.Bind(wx.EVT_MENU, self.on_spunta_due, self.spunta_due)

          menubar = wx.MenuBar()
          menubar.Append(menu, 'Menu')
          self.SetMenuBar(menubar)

          p = wx.Panel(self)
          a_button = wx.Button(p, -1, 'manipola spunta', pos=((10, 10)))
          b_button = wx.Button(p, -1, 'manipola radio', pos=((10, 50)))

          a_button.Bind(wx.EVT_BUTTON, self.on_a_button)
          b_button.Bind(wx.EVT_BUTTON, self.on_b_button)

      def on_a_button(self, evt): 
          print "spunta_uno adesso e' spuntato:", self.spunta_uno.IsChecked()
          self.spunta_due.Check(not self.spunta_due.IsChecked())
          print 'invertita la spunta di spunta_due'

      def on_b_button(self, evt):
          print "radio_uno adesso e' selezionato:", self.radio_uno.IsChecked()
          self.radio_tre.Check(True)
          print 'ho selezionato radio_tre'

      def on_spunta_due(self, evt):
          # Dimostra l'uso di evt.IsChecked. 
          # Qui avremmo potuto anche usare self.spunta_due.IsChecked()
          print "adesso spunta_due e' spuntato:", evt.IsChecked()

  if __name__ == '__main__':
      app = wx.App(False)
      MyFrame(None).Show()
      app.MainLoop()

.. index::
   single: wx.EVT_MENU_RANGE
   single: menu; wx.EVT_MENU_RANGE
   single: eventi; wx.EVT_MENU_RANGE

.. _ranged_menu_events:

Ranged events per i menu.
-------------------------

Quando abbiamo parlado degli id, ci siamo soffermati un po' anche :ref:`sul caso dei menu <gli_id_nei_menu>`. E' il caso di tornare a leggere quel paragrafo, prima di procedere con la lettura qui. 

Fatto? In quelle note si parlava di tecniche che qui finora non abbiamo mai incontrato, in particolare l'uso degli id come scorciatoia per identificare la provenienza di un evento (grazie all'uso di ``evt.GetId()`` nel callback). Non ripetiamo qui le cose già dette. Riassumendo:

- finché collegate ciascuna voce di menu a un callback separato, nessun problema;

- se volete collegare più voci a un singolo callback, potete farlo. Ma nel callback vi servirà rintracciare la voce da cui è partito l'evento, e potete farlo con gli id;

- in particolare, se più voci hanno eventi consecutivi, potete collegarle in un colpo solo a un unico callback usando ``wx.EVT_MENU_RANGE`` invece di ``wx.EVT_MENU``.

Un classico esempio in cui di solito si fa in questo modo è proprio quando usate blocchi di voci "radio" (o anche, sebbene più raramente, blocchi di voci spuntabili). In questi casi, in genere si preferisce raccogliere tutti gli eventi in un solo callback, e smistare di qui la logica di decisione successiva. 

Per esempio, sicuramente potreste anche fare così::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menu = wx.Menu()
          radio_uno = menu.Append(-1, 'radio uno', '', wx.ITEM_RADIO)
          radio_due = menu.Append(-1, 'radio due', '', wx.ITEM_RADIO)
          radio_tre = menu.Append(-1, 'radio tre', '', wx.ITEM_RADIO)

          self.Bind(wx.EVT_MENU, self.on_radio_uno, radio_uno)
          self.Bind(wx.EVT_MENU, self.on_radio_due, radio_due)
          self.Bind(wx.EVT_MENU, self.on_radio_tre, radio_tre)

          menubar = wx.MenuBar()
          menubar.Append(menu, 'Menu')
          self.SetMenuBar(menubar)

      def on_radio_uno(self, evt): print 'hai selezionato radio_uno'
      def on_radio_due(self, evt): print 'hai selezionato radio_due'
      def on_radio_tre(self, evt): print 'hai selezionato radio_tre'

Ma così è molto prolisso. Una forma più compatta (notate l'uso degli id) sarebbe invece::

  class MyFrame(wx.Frame): 
      def __init__(self, *a, **k):
          wx.Frame.__init__(self, *a, **k)

          menu = wx.Menu()
          radio_uno = menu.Append(100, 'radio uno', '', wx.ITEM_RADIO)
          radio_due = menu.Append(101, 'radio due', '', wx.ITEM_RADIO)
          radio_tre = menu.Append(102, 'radio tre', '', wx.ITEM_RADIO)

          self.Bind(wx.EVT_MENU_RANGE, self.on_radio, id=100, id2=102)

          menubar = wx.MenuBar()
          menubar.Append(menu, 'Menu')
          self.SetMenuBar(menubar)

      def on_radio(self, evt): 
          caller = evt.GetId()
          if caller == 100:
              print 'hai selezionato radio_uno'
          elif caller == 101:
              print 'hai selezionato radio_due'
          elif caller == 102:
              print 'hai selezionato radio_tre'
          # etc. etc., o un qualsiasi metodo di dispatch che vi sembra opportuno

Conclusione.
------------

Questa pagina e :ref:`la precedente <menu_basi>` completano il panorama di ciò che vi serve sapere per usare i menu nella vita di tutti i giorni. Ci sono tecniche più esotiche, di cui parleremo :ref:`un'altra volta <menu_avanzate>`.