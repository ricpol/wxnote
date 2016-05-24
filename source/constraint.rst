.. index:: 
   single: constraints
   single: constraints; wx.LayoutConstraints
   single: wx.LayoutConstraints
   single: constraints; wx.IndividualLayoutConstraint
   single: wx.IndividualLayoutConstraint
   single: wx.Window; SetConstraints
   single: constraints; wx.Window.SetConstraints
   single: wx.Window; SetAutoLayout
   single: constraints; wx.Window.SetAutoLayout
   single: wx.Window; Layout
   single: constraints; wx.Window.Layout

.. _constraint:

I constraints: un modo alternativo di organizzare il layout.
============================================================

Il modo corretto di organizzare il layout della vostra interfaccia grafica :ref:`è utilizzare i sizer <sizer_basi>` (quello scorretto è naturalmente il posizionamento assoluto, come abbiamo già detto nella stessa pagina).

Prima che venissero introdotti i sizer, tuttavia, il layout delle finestre si organizzava con i constraints. I sizer sono obiettivamente più pratici ed eleganti, e negli anni sono stati sviluppati moltissimo. I constraints invece sono ufficialmente deprecati da oltre 10 anni, e nessuno li usa più. Tuttavia non sono mai stati rimossi completamente da wxWidgets (e anche wxPython continua a supportarli). 

Anche se i constraints sono più macchinosi da usare rispetto ai sizer, ci sono alcuni casi particolari in cui potrebbero ancora tornare utili. In generale dovreste sempre usare i sizer: se un problema di layout vi sembra insormontabile con i sizer, nove su dieci vuol dire che avete ancora difficoltà a padroneggiarli. Tuttavia, occasionalmente potreste davvero trovarvi in una situazione in cui i vecchi constraints hanno ancora qualche carta da giocare. 

In questa pagina ci limiteremo a una breve presentazione dei constraints: se dovessero servirvi, la documentazione di wxWidgets spiega tutti i dettagli. In ogni caso, dovreste usare i contraints solo come ultima risorsa, e solo nel modo più semplice: se vi trovate a passare troppo tempo a studiare gli oscuri dettagli dei constraints, probabilmente state sbagliando approccio e dovreste tornare ai sizer. 


``wx.IndividualLayoutConstraint`` e ``wx.LayoutConstraints``.
-------------------------------------------------------------

Proprio come ``wx.Sizer`` e le sue sottoclassi incapsulano l'algoritmo di calcolo di un sizer, ``wx.IndividualLayoutConstraint`` definisce un constraint da applicare a un widget. 

Un constraint è un vincolo che si impone a una caratteristica geometrica di un widget: si possono imporre fino a otto diversi contraints, relativi a 

- bordo destro,
- bordo sinistro,
- bordo superiore,
- bordo inferiore,
- altezza,
- larghezza,
- coordinata x del centro,
- coordinata y del centro.

I vincoli si specificano in relazione ad altri widget, che possono essere i container genitori (un ``wx.Panel``, per esempio), o i widget "fratelli" nello stesso container. Per esempio è possibile vincolare il bordo destro di un widget a restare a 50 pixel dal bordo sinistro del vicino; si possono specificare anche vincoli come percentuali di altri vincoli, e così via. 

In realtà non c'è quasi mai ragione di istanziare direttamente un singolo constraint e poi applicarlo a un widget: si preferisce usare la più comoda classe ``wx.LayoutConstraints``, che in pratica è un contenitore che permette di specificare fino a 8 vincoli insieme, e poi applicarli tutti contemporaneamente al widget interessato. 

Un'istanza di ``wx.LayoutConstraints`` ha otto proprietà che mappano gli otto tipi di constraint visti sopra: ``wx.LayoutConstraints.top`` impone un vincolo al bordo superiore, e così via (le altre sono ``.bottom``, ``.left``, ``.right``, ``.height``, ``.width``, ``.centreX`` e ``.centreY``).

Un primo esempio chiarirà meglio la tecnica necessaria (iniziate a leggere dal codice della classe ``MainFrame``, per semplicità)::

    def my_constraints(relative_to):
        lc = wx.LayoutConstraints()
        lc.top.Below(relative_to, 20)
        lc.width.PercentOf(relative_to, wx.Width, 50)
        lc.height.AsIs()
        # provate per esempio ad alternare le due righe qui sotto:
        lc.left.SameAs(relative_to, wx.Left)
        # lc.centreX.SameAs(relative_to, wx.CentreX)
        return lc

    class MainFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            p = wx.Panel(self)
            p.SetAutoLayout(True)

            b1 = wx.Button(p, -1, '1')
            lc = wx.LayoutConstraints()
            lc.top.SameAs(p, wx.Top, 20)
            lc.left.SameAs(p, wx.Left, 40)
            lc.width.PercentOf(p, wx.Width, 50)
            lc.height.AsIs()
            b1.SetConstraints(lc)

            b2 = wx.Button(p, -1, '2')
            b2.SetConstraints(my_constraints(relative_to=b1))
            b3 = wx.Button(p, -1, '3')
            b3.SetConstraints(my_constraints(relative_to=b2))
            b4 = wx.Button(p, -1, '4')
            b4.SetConstraints(my_constraints(relative_to=b3))

Abbiamo collocato un primo pulsante con dei constraint relativi al panel contenitore. Per gli altri pulsanti abbiamo fattorizzato le regole dei constraint in una funzione separata, cosa che ci ha consentito di risparmiare un bel po' di spazio. Chiaramente, nel caso generale, avremmo dovuto specificare dei constraint differenti per ciascun widget, e dopo un po' di questa ginnastica capirete perché i sizer sono più comodi da usare. 

La sintassi di ``wx.LayoutConstraints`` è articolata, ma tutto sommato facile da capire. Ciascuno degli otto constraint può essere specificato in termini di: 

- ``.SameAs``, ovvero lo stesso bordo o dimensione di un riferimento (più un eventuale margine espresso in pixel);
- ``.PercentOf``, ovvero una percentuale di un riferimento;
- ``.AsIs``, ovvero "invariato", oppure "dimensioni di default";
- ``.Above``, ``.Below``, ``.LeftOf``, ``.RightOf``, ovvero sopra, sotto, a destra o a sinistra di un riferimento (più un eventuale margine);
- ``.Absolute``, ovvero il bordo o la dimensione sono espressi in valori assoluti;
- ``.Unconstrained``, ovvero non ci sono vincoli, e il bordo e la dimensione sono calcolati dopo che tutti gli altri vincoli sono stati rispettati (questo è il valore di default).

Il riferimento a cui si fa... riferimento (ehm) è espresso in termini delle costanti ``wx.Right``, ``wx.Left``, ``wx.Top``, ``wx.Bottom``, ``wx.CentreX`` e ``wx.CentreY`` il cui significato è ovvio. 

Per esempio, la riga ``lc.left.SameAs(p, wx.Left, 40)`` significa che il bordo sinistro (``.left``) del widget a cui verranno assegnati questi constraint dovrà avere lo stesso valore (``.SameAs``) del bordo sinistro (``wx.Left``) del widget di riferimento (il panel contenitore ``p``), più un margine di 40 pixel. 

I constraint si applicano al widget voluto invocando il metodo ``wx.Window.SetConstraints``. Il calcolo effettivo di tutti i constraint applicati avviene nel momento in cui wxPython esegue internamente il metodo ``wx.Window.Layout`` del widget (:ref:`ne abbiamo già parlato<fit_layout>`). Questo metodo però non è eseguito automaticamente: per essere sicuri che sia davvero chiamato ogni volta che la finestra viene ri-dimensionata, possiamo fare tre cose:

- la più semplice, è chiamare ``wx.Window.SetAutoLayout`` sul parent dei widget a cui vogliamo assegnare dei constraint: questo è possibile solo se il parent è un :ref:`contenitore<contenitori>` (che peraltro in pratica è la situazione più frequente) ovvero un panel, un dialogo o un frame;
- sovrascrivere il callback ``wx.Window.OnSize`` che viene eseguito di default in risposta a un ``wx.EVT_SIZE``, e chiamare lì direttamente ``wx.Window.Layout``; 
- oppure, in modo equivalente, catturare ``wx.EVT_SIZE`` e chiamare ``wx.Window.Layout`` nel nostro callback. 

Quando i constraints possono tornare utili.
-------------------------------------------

Come avrete capito anche da questo primo semplice esempio, i constraint sono molto verbosi e farraginosi da usare, in confronto ai sizer. In genere non vale la pena. Tuttavia, di tanto in tanto anche i sizer mostrano qualche limite. 

Considerate per esempio il caso in cui volete assegnare dei bordi asimmetrici a un widget. Vediamo prima un layout con i constraints::

    class Test(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            panel_base = wx.Panel(self)
            panel_red = wx.Panel(panel_base)
            panel_red.SetBackgroundColour(wx.RED) # per distinguerlo...
            panel_base.SetAutoLayout(True)

            lc = wx.LayoutConstraints()
            lc.top.SameAs(panel_base, wx.Top, 20)
            lc.left.SameAs(panel_base, wx.Left, 40)
            lc.bottom.SameAs(panel_base, wx.Bottom, 60)
            lc.right.SameAs(panel_base, wx.Right, 80)
            panel_red.SetConstraints(lc)

            b = wx.Button(panel_red, -1, 'clic', pos=(20, 20))
            b.Bind(wx.EVT_BUTTON, self.on_clic)
            self.panel_base = panel_base
            self.panel_red = panel_red

        def on_clic(self, evt):
            # dimostriamo come cambiare i margini di panel_red
            lc = wx.LayoutConstraints()
            lc.top.SameAs(self.panel_base, wx.Top, 70)
            lc.left.SameAs(self.panel_base, wx.Left, 50)
            lc.bottom.SameAs(self.panel_base, wx.Bottom, 30)
            lc.right.SameAs(self.panel_base, wx.Right, 10)
            self.panel_red.SetConstraints(lc)

            self.panel_base.SendSizeEvent()

Come si vede, la logica dei constraint è facile da seguire, e non abbiamo nessuna difficoltà a impostare quattro margini differenti per il nostro panel rosso. Anche modificare i margini successivamente è banale, come dimostriamo nel callback del pulsante: basta ricreare e ri-assegnare un ``wx.LayoutConstraints`` (qui non ci siamo preoccupati troppo di duplicare parecchie linee di codice. In un progetto reale, un po' di fattorizzazione sarebbe consigliabile!). L'unico accorgimento necessario, dal momento che la finestra non ha cambiato dimensioni, è ricordarsi di chiamare ``wx.Window.SendSizeEvent`` per innescare il ricalcolo del layout. 

I sizer d'altra parte hanno più difficoltà a gestire margini differenti. Se i margini fossero tutti uguali, non ci sarebbero problemi a fare qualcosa come::

    s = wx.BoxSizer()
    s.Add(panel_red, 1, wx.EXPAND|wx.ALL, 20)
    panel_base.SetSizer(s)

In caso di margini diversi, però, il layout si complica e bisogna ricorre ad artifici come gli :ref:`spazi vuoti<sizer_spazio_vuoto>`. Un equivalente potrebbe essere questo::

    class Test(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            panel_base = wx.Panel(self)
            panel_red = wx.Panel(panel_base)
            panel_red.SetBackgroundColour(wx.RED)

            s = wx.FlexGridSizer(3, 3) # una griglia 3x3
            s.AddGrowableCol(1)
            s.AddGrowableRow(1)
            s.Add((40, 20)) # gli spacer d'angolo impongono i margini
            s.Add((-1, -1))
            s.Add((-1, -1))
            s.Add((-1, -1))
            s.Add(panel_red, 1, wx.EXPAND) # al centro, il panel rosso
            s.Add((-1, -1))
            s.Add((-1, -1))
            s.Add((-1, -1))
            s.Add((80, 60)) # gli spacer d'angolo impongono i margini
            panel_base.SetSizer(s)

Qui per fortuna ci siamo fatti aiutare da un ``wx.FlexGridSizer`` con le sue proprietà ``AddGrowableCol`` e ``AddGrowableRow``, perché lo stesso layout realizzato esclusivamente con i ``wx.BoxSizer`` sarebbe stato più complicato (anche se invece un ``wx.GridBagSizer``, a dire il vero, ci avrebbe risparmiato un po' di linee di codice: ma lo strumento migliore varia da progetto a progetto). Si nota comunque una buona dose di artificiosità per realizzare un layout tutto sommato molto semplice. 

Anche cambiare i margini a runtime, con i sizer è più complicato, e questo perfino nell'ipotesi che tutti i margini siano uguali. Infatti i margini sono determinati da costanti e flag del metodo ``wx.Sizer.Add``, in costrutti del tipo ``s.Add(widget, 1, wx.BOTTOM|wx.TOP, 5)`` (che vuol dire, un margine di 5 pixel sopra e sotto). L'unica soluzione per cambiare questi parametri in seguito, è conservare un riferimento al ``wx.SizerItem`` restituito dalla chiamata a ``wx.Sizer.Add``, e poi usare metodi come ``wx.SizerItem.SetFlag`` o ``wx.SizerItem.SetProportion`` per cambiare le cose, :ref:`come abbiamo visto<sizeritem>`. Oppure, si potrebbe in modo più radicale staccare l'elemento dal sizer senza distruggerlo (con ``wx.Sizer.Detach``) e poi re-inserirlo nello stesso posto con parametri diversi. 

Questo sono comunque scenari piuttosto rari nella pratica di tutti i giorni. Di solito non capita di dover modificare margini già assegnati; in effetti, è raro anche voler assegnare margini asimmetrici. Non dovrebbe capitarvi spesso, quindi, una situazione in cui vi viene voglia di usare i constraint invece dei sizer. 

Se però decidete di usare i constraint per qualche motivo, ricordate infine che potete farli lavorare insieme ai sizer senza particolari problemi. Nell'esempio qui sopra, per brevità abbiamo inserito un pulsante all'interno del panel rosso con il posizionamento assoluto (anche se sappiamo bene che :ref:`non bisognerebbe mai farlo<sizer_basi>`). Avremmo invece potuto creare un sizer assegnato al panel rosso, e usarlo come di consueto per disporre il pulsante e altri widget. 
