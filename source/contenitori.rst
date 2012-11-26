.. highlight:: python
   :linenothreshold: 5

.. index:: frame, dialoghi, panel

.. _contenitori:

Frame, dialoghi, panel: contenitori wxPython.
=============================================

Tra i widget wxPython, alcuni hanno la funzione principale di contenere altri widget, organizzandoli sia graficamente sia anche logicamente. I tre più importanti sono ``wx.Frame``, ``wx.Dialog`` e ``wx.Panel``. 

Oltre a questi ce ne sono molti altri, per lo più ottenuti per sottoclassamento. Per esempio, ``wx.MiniFrame`` è un normale frame, ma con la barra del titolo più stretta; ``wx.ScrolledPanel`` è un panel con barre di scorrimento incorporate, etc. etc. 
Cercate sulla demo "frame", "panel" e "dialog" per farvi un'idea. 

E' importante però conoscere bene i tre "fondamentali", perché costituiscono l'intelaiatura di ogni applicazione wxPython.

.. index:: 
   single: wx; Frame()
   single: stili; di un frame

``wx.Frame``. 
-------------

I ``wx.Frame`` (frame per gli amici) sono quello che l'utente, guardando, dice "è la finestra". In genere la "finestra principale" della vostra applicazione è un frame, anche se non è necessario (potrebbe essere un dialogo). Molto spesso i frame sono :ref:`finestre "top-level" <finestre_toplevel>`, ma nulla vieta di assegnare anche a loro dei genitori. 

Non succede praticamente mai che si crei direttamente un ``wx.Frame``: la procedura normale è invece definire delle sottoclassi personalizzate, con tutte le caratteristiche volute (e già complete di tutti i widget da inserire nel frame), e poi istanziare la sottoclasse. 

Il costruttore di ``wx.Frame`` prevede naturalmente un parametro ``style``, e ci sono moltissimi :ref:`stili <stili>` disponibili per variare l'aspetto e le funzionalità di un frame (e anche alcuni :ref:`extra-style <extrastyle>`). Potete consultare la documentazione per conoscerli tutti. La raccomandazione in ogni caso è di non variare mai troppo l'aspetto base del frame, soprattutto la finestra principale, per non disorientare (leggi: irritare) l'utente, che si aspetta la normale operatività delle finestre del suo sistema operativo. Se non passate nessun parametro ``style``, verrà applicato il ``wx.DEFAULT_FRAME_STYLE``. 

Oltre alla cornice, nel frame è possibile inserire una ``wx.MenuBar`` (ossia un barra dei menu), una ``wx.ToolBar`` (una barra dei pulsanti, in genere sotto i menu) e una ``wx.StatusBar`` (una barra di stato in basso). 

.. todo:: sicuramente una pagina per i menu

.. todo:: una pagina per la toobar e la statusbar?

Tutto lo spazio che resta, ovviamente, deve essere riempito con altri widget "figli". In genere i widget figli si creano nell'``__init__`` del frame, in modo che quando il frame ha terminato il processo di istanziazione e verrà mostrato, avrà già al suo interno tutti i widget figli che deve contenere. Per esempio::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            a_text = wx.TextCtrl(self, pos=(10, 10))
            a_button = wx.Button(self, -1, 'Hello Word', pos=(10, 50))
            
    app = wx.App(False)
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()  
    
Alla riga 1, definisco una sottoclasse personalizzata di ``wx.Frame``. Alla riga 2, sovrascrivo l'``__init__`` per definire al suo interno i diversi widget "figli" che il frame dovrà contenere. Alla riga 3, mi ricordo di richiamare l'``__init__`` della classe-madre: questo è sempre necessario al momento di sovrascrivere l'``__initi__``, e non solo dei frame, ma di qualsiasi widget. Infatti, nell'``__init__`` avvengono sempre importanti inizializzazioni sul lato C++ del framework, e quindi è importante limitarsi ad estenderlo, senza sostituirlo del tutto. 

Alle righe 4 e 5, creo due widget "figli" che saranno contenuti nel frame. Definisco il rapporto di parentela passando ``self`` come primo argomento (il "parent"). In questo modo saranno figli della futura istanza di ``MyFrame``, quando verrà creata. Un discorso più ampio sulle catene di relazioni padre-figlio è affrontato :ref:`in una pagina separata <catenaparent>`. 

.. note:: in questi esempi minimali, usiamo il cosiddetto "posizionamento assoluto" dei widget, ovvero specifichiamo la posizione in pixel. Questo è decisamente sconsigliato nel mondo reale. Usate i sizer, invece. 

.. todo:: una pagina sui sizer

Alle righe 7 e 10, avvio la macchina della ``wx.App`` e del suo ``MainLoop``. Di nuovo, potete trovare informazioni più accurate su questo :ref:`in un'altra sezione <wxapp_basi>`. 

Alla riga 8, creo finalmente un'istanza della sottoclasse ``MyFrame`` che ho definito sopra. Con questo, wxPython invocherà tutti i procedimenti necessari per disegnare la mia finestra, compresi tutti i figli che ho creato nell'``__init__``. Finalmente, alla riga 9, sono pronto a mostrare il mio frame, completo di tutti i widget che deve contenere. 

Anche se dentro un frame è possibile mettere qualsiasi widget, in pratica conviene sempre "appoggiare" prima i widget sopra un ``wx.Panel``, e inserire direttamente nel frame soltanto il panel. In effetti il frame non è fatto per contenere direttamente i widget. Un motivo potete già vederlo testando il codice dell'esempio qui sopra (almeno se siete in Windows, è molto evidente). Il frame è "bucato", nel senso che intorno al pulsante non si vede lo sfondo che ci aspetteremmo, ma il brutale sfondo del frame (che è immodificabile). Ovviamente potete sistemare i widget in modo da "tassellare" completamente il contenitore del frame senza lasciare nessun buco, ma questo non è pratico. Sulle piattaforme diverse da Windows, il colore di sfondo del frame è ideantico al colore di sfondo degli altri widget, per cui il buco non si vede (ma c'è sempre). 

Ma non è solo un problema di estetica. Il fatto è che un frame manca di alcune funzionalità che probabilmente vi interessano, e di cui invece dispone il panel. Ci arriviamo subito.

.. index::
   single: wx; Panel()
   single: wx; TAB_TRASVERSAL
   single: panel; tab trasversing
   single: wx.Button; SetDefault()

.. _wxpanel: 

``wx.Panel``.
-------------

Se il frame è pensato per presentare la cornice della finestra, il panel ha la funzione di contenere i widget. Come abbiamo notato qui sopra, anche se il frame può contenere direttamente i widget, in pratica si preferisce sempre assegnarli a un panel, e poi inserire il panel dentro al frame. 

Il panel ha delle funzionalità in più, interessanti. A livello estetico, ha uno sfondo "solido", il cui colore può essere modificato a piacere. Ha anche diverse tipologie di bordo, fissabili per mezzo degli stili. 

Ma la cosa più interessante è che fornisce di default il comportamento ``wx.TAB_TRASVERSAL``, ovvero la possibilità di spostarsi tra i vari widget "figli" con il tasto di tabulazione. 

Inoltre, un panel può avere tra i suoi figli un pulsante "di default" (chiamando su di esso il metodo ``SetDefault()``), che si attiva alla pressione del tasto <invio>. 

Nel caso più semplice, per usare un panel dentro un frame basta creare un'instanza di ``wx.Panel`` nell'``__init__`` del frame, proprio come si farebbe per qualsiasi altro widget figlio. Dopo di che, tutti gli altri widget saranno assegnati come figli del panel, e non del frame. Il nostro esempio di sopra diventa quindi::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            panel = wx.Panel(self)
            a_text = wx.TextCtrl(panel, pos=(10, 10))
            a_button = wx.Button(panel, -1, 'Hello Word', pos=(10, 50))
            
    app = wx.App(False)
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()  

Notate, alla riga 4, che il il panel è figlio del frame (``self``), e gli altri widget sono invece figli del panel. Curiosamente non abbiamo bisogno di specificare una posizione per il panel all'interno del frame. Infatti, quando un contenitore ha un solo figlio, questo occupa naturalmente tutto lo spazio libero. 

Naturalmente, con lo stesso metodo possiamo definire un secondo panel nell'``__init__`` del frame, e un altro gruppo di widget da raggruppare. Possiamo inserire quanti panel vogliamo dentro un frame, basta specificare in qualche modo il layout (con il posizionamento assoluto, oppure, molto meglio, con i sizer: vedi la nota sopra). E' frequente anche l'inserimento di un panel dentro un altro panel, per creare strutture più complesse. 

I panel, nella pratica dello sviluppo di applicazioni efficienti, vengono utilizzati molto per organizzare i widget da un punto di vista logico, raggruppando insieme i widget che concorrono a una stessa funzionalità del programma. Per esempio, un panel potrebbe contenere tutti i campi necessari alla scheda anagrafica di una persona (nome, cognome, indirizzo...). Un altro panel raggruppa invece i campi necessari a registrare la sua posizione nell'azienda (salario, data di assunzione...). Il panel "anagrafico" potrebbe essere contenuto in un frame "Dati personali", e il panel "aziendale" in un altro frame "Dati aziendali". Ma entrambi i panel potrebbero essere riutilizzati e inseriti in un terzo frame "Dati completi dell'impiegato". Questa organizzazione favorisce il riutilizzo del codice e la separazione delle varie funzioni (per esempio, ciascun panel potrebbe essere collegato a un diverso codice "di controllo" per il trattamento dei dati immessi). 

Il modo normale per implementare questi "cluster" riutilizzabili di widget consiste semplicemente nel creare sottoclassi personalizzte di ``wx.Panel``. che definiscono nel loro ``__init__`` tutti i widget figli di cui hanno bisogno. Successivamente, il panel personalizzato può essere inserito in un frame come al solito. Per esempio, riscriviamo ancora una volta il nostro codice, separando il panel dal frame::

    class MyPanel(wx.Panel):
        def __init__(self, *a, **k):
            wx.Panel.__init__(self, *a, **k)
            a_text = wx.TextCtrl(self, pos=(10, 10))
            a_button = wx.Button(self, -1, 'Hello Word', pos=(10, 50))
            
    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            panel = MyPanel(self)
            
    app = wx.App(False)
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()   

Si noti che adesso i due widget sono figli di ``self`` (ma ``self`` è il panel, beninteso), e si noti anche l'istanziazione di ``MyPanel`` dentro il frame, alla riga 10. 

Il risultato finale sembra identico, e anzi il codice si è allungato un po'. Ma il vantaggio nascosto è che questa volta ``MyPanel`` è una classe separata, pronta a essere riutilizzata ovunque. 

In conclusione, i panel sono un ottimo strumento per organizzare i widget, sia per il layout sia per la logica. Al contrario di quello che ci si potrebbe aspettare, le applicazioni più estese tendono ad avere poche sottoclassi di ``wx.Frame``, piuttosto "leggere", e molte sottoclassi di ``wx.Panel``, ciascuna specializzata a gestire una funzionalità di base e a esporla all'esterno in un'api coerente. I panel sono i veri e propri mattoni da costruzione di un'applicazione wxPython.

.. index::
   single: wx; Dialog()
   single: wx.Dialog; ShowModal()
   single: wx.Window; Destroy()
   single: validatori; validazione automatica
   single: dialoghi; con pulsanti predefiniti
   single: dialoghi; con validazione automatica
   single: dialoghi; chiusura
   single: chiusura; di un dialogo

.. _wxdialog:

``wx.Dialog``.
--------------

I dialoghi sono delle finestre molto simili ai frame, ma con alcune limitazioni da un lato, e alcune aggiunte dall'altro. E' piuttosto facile confondere il comportamento dei frame con quello dei dialoghi, e (ab)usare di uno invece dell'altro. Bisogna tener presente che la funzione dei dialoghi è di creare interfacce più semplici e "di rapido consumo", per chiedere qualche pezzo di informazione all'utente, e poi essere subito distrutti. 

Anche se è possibile creare dialoghi molto complessi, è opportuno tenere a mente che ``wx.Dialog`` è progettato per rispondere meglio a certe esigenze. E' inutile "tirare la corda" e cercare di usare un dialogo per cose per cui sarebbe più adatto un frame. Per esempio, un ``wx.Dialog`` non può avere una toolbar. E' certamente possibile inserire una fila orizzontale di piccoli pulsanti quadrati in alto, e mimare una toolbar... Ma a questo punto, perché non usare un frame, piuttosto?

Rispetto ai frame, ecco un elenco delle cose più importanti che dialoghi e frame hanno in comune:

* possono essere :ref:`finestre "top-level" <finestre_toplevel>`; tuttavia è più frequente che i dialoghi vengano generati da un frame genitore, da cui sono gestiti (e soprattutto distrutti quando non servono più). 

* condividono gli stili necessari per determinare i pulsanti della barra del titolo: in particolare, è possibile mostrare o nascondere i pulsanti di riduzione a icona, chiusura, etc. E' anche possibile determinare se sono ridimensionabili.

* possono naturalmente contenere un numero qualunque di altri widget, tra cui panel. 

Ecco invece che cosa i dialoghi hanno in meno, rispetto ai frame:

* non possono avere barre dei menu, toolbar e barre di stato;

* non hanno alcuni stili specifici dei frame, per esempio ``wx.FRAME_TOOL_WINDOW``

Ecco le funzionalità che i dialoghi hanno in più rispetto ai frame:

* hanno già le funzionalità dei panel. In pratica, potete pensare ai dialoghi come se avessero già un panel inserito dentro. Quindi, quando create un widget "figlio" di un dialogo, è come inserire prima il widget dentro un panel, e poi mettere il panel dentro il dialogo. I widget del dialogo quindi hanno già il "tab-trasversing", e il default widget. 

* hanno un metodo ``ShowModal()`` in aggiunta al metodo ``Show()``, per mostrare il dialogo in forma "modale" (ossia, nessun'altra azione può essere compiuta se prima non si chiude il dialogo). 

* possono fare uso di pulsanti con :ref:`id predefiniti <idpredefiniti>` per chiudersi automaticamente e restituire un codice corrispondente al pulsante premuto. 

* se usano pulsanti predefiniti, guadagnano la :ref:`validazione automatica <validazione_automatica>` se il codice restituito è ``wx.ID_OK``.

* ci sono molte sottoclassi predefinite e specializzate per facilitare casi d'uso tipici (chiedere brevi stringhe di testo, password, selezionare file, colori, etc.: cercate "dialog" nella demo per farvi un'idea). 

Ed ecco infine le cose che, semplicemente, sono diverse:

* hanno :ref:`l'extra-sytle <extrastyle>` ``wx.WS_BLOCK_EVENTS`` settato per default. Il che significa che gli eventi generati dai widget interni :ref:`non possono propagarsi <eventi_avanzati>` al di fuori del dialogo stesso. Questo è in linea con il principio che i dialoghi dovrebbero sempre "sbrigarsi da soli le proprie faccende", e limitarsi a restituire al mondo esterno un codice di uscita. 


* :ref:`rispondono diversamente <chiusura>` al metodo ``Close()``: un frame chiama automaticamente ``Destroy()``, mentre un dialogo non si distrugge subito, ma si limita a nascondersi restando ancora in vita. Questo perché è frequente voler conservare il dialogo, dopo che l'utente lo ha "chiuso", per raccogliere i suoi dati. Questo significa però che dovete sempre preoccuparvi di chiamare voi stessi ``Destroy()`` quando il dialogo davvero non vi serve più. 

La procedura comune per quanto riguarda l'utilizzo di dialoghi personalizzati per raccogliere e gestire dati, è più o meno questa: si definisce una sottoclasse di ``wx.Dialog``, con tutti i widget necessari (per esempio, caselle di testo, etc.). Per evitare di dover accedere direttamente ai widget "figli", conviene dotarla di una interfaccia ``GetValue`` che raccoglie i dati e li presenta in una struttura-dati conveniente (per esempio, un dizionario). Infine, si inseriscono nel dialogo pulsanti di conferma o annulla, preferibilmente :ref:`con id predefiniti <idpredefiniti>` in modo da ottenere facilmente il comportamento standard di chiusura ed eventuale validazione automatica, se lo si desidera. Quando l'utente chiude il dialogo, prima di distruggerlo si accede alla interfaccia ``GetValue`` per raccogliere i dati inseriti. 

Ecco un esempio minimo di un dialogo che chiede di inserire nome e cognome::

    class YourNameDialog(wx.Dialog):
        def __init__(self, *a, **k):
            wx.Dialog.__init__(self, *a, **k)
            self.first_name = wx.TextCtrl(self)
            self.family_name = wx.TextCtrl(self)
            
            s = wx.FlexGridSizer(2, 2, 5, 5)
            s.AddGrowableCol(1)
            s.Add(wx.StaticText(self, -1, 'nome:'), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.first_name, 1, wx.EXPAND)
            s.Add(wx.StaticText(self, -1, 'cognome:'), 0, wx.ALIGN_CENTER_VERTICAL)
            s.Add(self.family_name, 1, wx.EXPAND) 
            
            s1 = wx.BoxSizer()
            s1.Add(wx.Button(self, wx.ID_OK, 'ok'), 1, wx.EXPAND|wx.ALL, 5)
            s1.Add(wx.Button(self, wx.ID_CANCEL, 'cancella'), 1, wx.EXPAND|wx.ALL, 5)
            
            s2 = wx.BoxSizer(wx.VERTICAL)
            s2.Add(s, 1, wx.EXPAND|wx.ALL, 5)
            s2.Add(s1, 0, wx.EXPAND|wx.ALL, 5)
            self.SetSizer(s2)
            s2.Fit(self)
        
        def GetValue(self): 
            return {'nome'    : self.first_name.GetValue(), 
                    'cognome' : self.family_name.GetValue()}
            
            
    class MyTopFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            b = wx.Button(self, -1, 'inserisci il tuo nome')
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            
        def on_clic(self, evt):
            dlg = YourNameDialog(self, title='Nome e cognome, prego')
            retcode = dlg.ShowModal()
            if retcode == wx.ID_OK:
                data = dlg.GetValue()
            else:
                data = {}
            # print data
            dlg.Destroy()
            
                            
    app = wx.App(False)
    MyTopFrame(None, size=(150, 150)).Show()
    app.MainLoop()

Le righe significative sono le 4-5, dove definiamo le caselle di testo in cui andranno inseriti i dati; le 15-16, dove inseriamo i pulsanti con gli id predefiniti; le 24-26, dove definiamo l'interfaccia ``GetValue`` che raccoglie di dati e li presenta in una struttura conveniente.

Con queste premesse, il procedimento di creazione del dialogo e raccolta dei dati è molto lineare. Alla riga 36 creiamo il dialogo, e alla riga 37 lo mostriamo. Non c'è stato bisogno di collegare esplicitamente i due pulsanti a degli eventi: siccome hanno id predefiniti, wxPython sa già cosa fare. In entrambi i casi, il dialogo si chiude e  ``ShowModal`` restituisce l'id del pulsante premuto, ``wx.ID_OK`` oppure ``wx.ID_CANCEL``. Nel primo caso, raccogliamo i dati chiamando ``GetValue()``: non c'è  bisogno di accedere direttamente agli elementi interni del dialogo, dal momento che abbiamo definito un'interfaccia conveniente che si occupa di nascondere i dettagli e presentarci solo i dati che vogliamo. Infine, distruggiamo esplicitamente il dialogo che ormai non serve più, alla riga 43.

Se l'utente fa clic sul pulsante contrassegnato da ``wx.ID_OK``, avviene anche la validazione automatica, che in questo caso passa sempre senza conseguenze, perché non abbiamo definito nessun validatore. 

I :ref:`validatori <validatori>` possono inoltre essere una valida alternativa per trasferire i dati dal dialogo alla finestra madre, alla chiusura (e in senso contrario all'apertura). Parliamo di questo nella sezione apposita.

Rimando infine anche agli esempi della sezione dedicata :ref:`alla chiusura delle finestre <chiusura>` e di quella :ref:`sui dialoghi con pulsanti predefiniti <idpredefiniti>`. 

