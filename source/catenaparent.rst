.. _catenaparent:

.. index:: widget parent, widget figli
   
La catena dei "parent".
=======================

In wxPython, praticamente ogni widget che create deve stare in una relazione padre-figlio con altri widget. Come nella vita reale, un widget può avere molti figli, ma un solo padre. Questa organizzazione, che è onnipresente, rispecchia naturalmente lo stato delle cose in una normale interfaccia grafica. Per esempio, un ``wx.Frame`` (la finestra che fa da cornice al resto) potrebbe contenere al suo interno un ``wx.Panel`` (lo "sfondo") in cui potrebbero a loro volta essere organizzati diversi ``wx.TextCtrl`` (caselle di testo), ``wx.Button`` (pulsanti), e così via. 

Ma non è solo questo. Per esempio, se una finesta apre un ``wx.Dialog`` (una finestra di dialogo) per chiedere qualcosa all'utente, è normale che questo dialogo sia "figlio" della finestra-madre. A loro volta, tutt i widget dentro il dialogo saranno "figli" di questo, e così via. 

Queste catene di padri-figli possono essere anche molto lunghe. Il rapporto padre-figlio non è solo una questione di organizzazione astratta, ma comporta anche delle conseguenze pratiche vistose. 

Per esempio, se chiudete una finestra, tutti i suoi "figli" verranno distrutti automaticamente con essa. Questo è il comportamento che volete, perché altrimenti i vari widget della finestra resterebbero in vita con conseguenze bizzarre. Ma se la vostra finestra aveva aperto una seconda finestra "figlia", al momento di chiudere la prima si chiuderà anche quest'ultima. Anche questo è logico: il principio è che nessun "padre" dovrebbe lasciare in giro figli "orfani". Se però non è il comportamento che desiderate, nessun problema: avete sempre il controllo delle relazioni padre-figlio, quindi potete agganciare la seconda finestra a un nuovo padre, o anche dichiararla "top-level" come vedremo. 

Ma gli effetti delle relazioni padre-figlio si manifestano anche in altre occasioni. Alcuni widget possono trasmettere automaticamente certe proprietà ai figli. Per esempio, se settate un particolare font per un ``wx.Panel``, questo verrà automaticamente trasmesso a tutti i figli. Se chiamate ``Validate()`` su un ``wx.Dialog``, tutti i suoi figli verranno automaticamente "validati" (posto che abbiano un ``wx.Validator`` appropriato). E gli esempi potrebbero continuare a lungo. 

Forse però l'esempio più clamoroso che si deve citare è la propagazione degli eventi. Ce ne occupiamo in modo specifico :ref:`in una pagina separata <eventi_avanzati>`, ma per il momento basta dire che un ``wx.CommandEvent`` si propaga dal widget che lo ha originato al suo genitore, e poi al genitore del genitore, e così via fino all'ultimo genitore "top-level" e poi ancora da questo alla ``wx.App``. Così, per esempio, se avete un frame con dentro un panel con dentro un pulsante, e ci cliccate sopra, il ``wx.EVT_BUTTON`` si trasmette all'indietro dal pulsante al panel, al frame, e finalmente alla ``wx.App``, permettendovi di intercettarlo a ogni "fermata".

La catena dei rapporti padre-figlio è quindi un concentto importante. In questa pagina cerchiamo di analizzare il problema a fondo.

.. index::
   single: wx.Window; SetParent()
   
Dichiarare il "parent".
-----------------------

Ci sono sostanzialmente due modi per dichiarare che un widget è "genitore" di un altro. 

Il primo, di gran lunga il più comune, è al momento della creazione. Tutti i widget di wxPython, al momento della loro creazione (cioè quando istanziate la loro classe) vi chiedono di specificare il loro genitore. Il primo argomento (obbligatorio) che dovete passare al costruttore è sempre il "parent". Per esempio::

    my_button = wx.Button(my_panel, -1, 'clic me!')
    
In questo esempio, ``my_panel`` (un panel già creato, supponiamo) sarà il "parent" di ``my_button``. Per esempio, un approccio tipico quando si definisce la classe di un frame, di un dialogo o di un panel, è di creare tutti i widget che contiene in questo modo::

    class MyFrame(wx.Frame):
        def __init__(self, *a, **k):
            wx.Frame.__init__(self, *a, **k)
            
            a_button = wx.Button(self, -1, 'I am a button')
            another_button = wx.Button(self, -1, '...me too...')
            a_text = wx.TextCtrl(self, -1, 'I am a text box')
            # etc. etc.
            
Notate quei ``self`` passati come primo argomento ai costruttori di ciascun widget: indicano che il "parent" del widget dovrà essere lo stesso ``MyFrame`` (o meglio la sua istanza, appena sarà effettivamente creato). 

Unicamente i ``wx.Frame`` e i ``wx.Dialog`` (insieme a qualche altro contenitore di minore importanza) possono essere chiamati con ``parent=None``. In questo caso non hanno genitori e sono considerati finestre "top-level", come vedremo tra poco. Chiaramente tutte le vostre applicazioni wxPython devono per forza avere almeno una finestra "top-level", ossia quella che create per prima:: 

    app = wx.App(False)
    my_first_frame = MyFrame(None, -1, title='Hello Word!') # parent=None !
    my_first_frame.Show()
    app.MainLoop()
    
Siete costretti, perché non esiste nessun possibile genitore già creato. 

Il secondo modo di dichiare il "parent" di un widget è chiamare ``SetParent`` dopo che è stato creato::

    my_button.SetParent(some_other_widget)
    
Questo può essere fatto su qualunque widget (posto che naturalmente non potete impostare ``SetParent(None)`` per qualcosa che non sia un frame o un dialogo). Tuttavia è molto raro nella pratica, ed è sempre sorgente di confusione ri-aggiustare la catena dei "parent" a runtime. Un caso in cui può essere giustificato è quando volete agganciare una finestra figlia a un nuovo genitore (o renderla top-level) prima che il suo attuale "parent" venga distrutto. 

.. index::
   single: wx.Window; GetGrandParent()
   single: wx.Window; GetTopLevelParent()
   single: wx.Window; GetChildren()
   
Orientarsi nell'albero dei "parent". 
------------------------------------

Le catene dei "parent" possono essere lunghe e complicate. wxPython mette a disposizione qualche strumento utile per navigare in questo mare tempestoso.

* il più comune è ``GetParent`` (da usare così: ``my_button.GetParent()``) che restituisce il genitore diretto di un widget qualsiasi (oppure ``None``, se lo chiamate su una finestra top-level).

* ``GetGrandParent`` (esiste davvero!) è del tutto analogo, ma restituisce... beh, il nonno. 

* ``GetTopLevelParent`` è molto più utile, salta tutta la gerarchia e punta dritto al progenitore "top level".

* ``GetChildren``, chiamato su un genitore, restituisce l'elenco di tutti i suoi figli (solo i figli diretti: ma potete chiamare ricorsivamente ``GetChildren`` per ricostruire tutta la discendenza di un widget, per esempio). 

.. _finestre_toplevel:

.. index::
   single: top-level, finestre
   single: wx; GetTopLevelWindows()
   single: wx.App; GetTopWindow()
   single: wx.App; SetTopWindow()
   
Le finestre top-level.
----------------------

Come abbiamo detto, i ``wx.Frame`` e i ``wx.Dialog`` (e naturalmente tutte le loro sottoclassi) possono ammettere ``parent=None``. In questo caso sono dette "finestre top-level", perché non hanno genitori. 

In una applicazione possono esserci più finestre top-level contemporaneamente. Sicuramente deve essercene almeno una, però. Quando l'ultima finestra top-level viene chiusa, questo è il segnale per wxPython di terminare la ``wx.App`` e chiudere il programma, come analizziamo più approfonditamente :ref:`altrove <chiusuraapp>`. 

Proprio perché le finestre "top-level" possono essere diverse, wxPython permette anche di definire, tra queste, una "finestra regina", detta "top-window" (da non confondere con "top-level" window). Può esserci sono una "top-window" aperta in ogni momento, e naturalmente deve trattarsi di una finestra "top-level". 

Di fatto, non c'è nessuna differenza particolare tra la "top-window" e le sue sorelle "top-level". Per esempio, non è vero che chiudendo la "top-window" si chiude automaticamente l'applicazione (perché questo avvenga, è necessario che tutte le "top-level" siano chiuse). Si tratta semplicemente di una convenzione che permette, in presenza di più "top-level" aperte, di puntare in fretta a una particolarmente importante. 

wxPython considera automaticamente "top-window" il primo frame che create. Dopo di che, le varie finestre "top-level" possono essere gestite con questi metodi e funzioni globali:

* ``wx.GetTopLevelWindows`` restituisce una lista delle finestre "top-level" aperte;

* ``wx.App.GetTopWindow`` restituisce la "top-window";

* ``wx.App.SetTopWindow`` attribuisce a una "top-level" il ruolo di "top-window" (destituendo automaticamente l'attuale "top-window");

* infine, per promuovere a "top-level" una finestra normale basta chiamare su questa ``SetParent(None)``, come abbiamo visto.

Detto questo, bisogna comunque specificare che, nel mondo reale, di rado c'è bisogno di tutto questo. La maggior parte delle applicazioni wxPython hanno una sola "top-level", che è il primo frame che create e mostrate, e che quindi coincide con la "top-window". Occasionalmente, potrebbero comparire per breve tempo altri dialoghi "top-level" (una finestra di login, per esempio), ma si tratta di eccezioni temporanee. Nelle applicazioni di tutti i giorni, è buona norma limitarsi a una sola "top-level", anche per semplificare il :ref:`processo di chiusura <chiusuraapp>` della ``wx.App.``.


