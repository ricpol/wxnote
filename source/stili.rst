.. _stili:

.. index::
   single: stili

I flag di stile.
================

I flag di stile sono frequenti in wxPython. Al momento della creazione di un widget qualsiasi, è comune aggiungere un parametro ``style`` al costruttore. Ogni widget ha i suoi flag di stile predefiniti, che si possono combinare per ottenere varie personalizzazioni. 

.. index::
   single: bitmask
   
Che cos'è una bitmask.
----------------------

Prima di tutto, una piccola spiegazione sulle bitmask: non è un argomento specifico di wxPython, ma serve a capire meglio il resto. Se avete familiarità con il concetto, saltate questo paragrafo. 

Ciascuno stile in wxPython è definito da una costante globale. Per esempio::

    >>> import wx
    >>> wx.TE_READONLY # lo stile per i TextCtrl di sola lettura
    16

Quello che alcuni notano a prima vista, è che tutte queste costanti sono scelte per essere potenze di 2. La cosa è utile perché le potenze di 2, in notazione binaria, si possono sommare tra loro in modo che ciascun addendo contribuisca a modificare solo un bit della somma finale. In altre parole, è sempre possibile ricostruire gli addendi a partire dal risultato. 

La comodità è che in questo modo potete combinare gli stili tra di loro, semplicemente sommandoli: dalla somma, wxPython ricava l'elenco di quelli che avete scelto. 

.. note:: Naturalmente un programmatore Python è abituato a usare strutture di più alto livello e maneggevoli, come le liste o le tuple, per questi compiti. Ma in C++ queste cose non sono gratis, e le bitmask sono comode e veloci. 

Per combinare gli stili, usate l'operatore bitwise OR Python::

    wx.TextCtrl(parent, sytle=wx.TE_READONLY|wx.TE_MULTILINE)
    
produce una casella di testo multilinea e per sola lettura. 

Alcuni stili, per comodità, sono già definiti come il risultato della combinazione di altri. Per esempio, il già citato ``wx.DEFAULT_FRAME_STYLE`` è definito come::

    wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|
    wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX 

E quindi vi risparmia un bel po' di battute di tastiera. Quando lavorate con questi stili composti, talvolta può tornare utile *sottrarre* qualche stile dalla lista, invece di aggiungerlo. Per fare questo, potete usare l'operatore XOR:: 

    wx.Frame(parent, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

produce un frame "normale" ma senza bordi trascinabili, e::

    wx.Frame(parent, style=wx.DEFAULT_FRAME_STYLE^(wx.MAXIMIZE_BOX|
                                                   wx.MINIMIZE_BOX|
                                                   wx.RESIZE_BORDER))

elimina anche la possibilità di espansione e riduzione a icona. 

.. index::
   single: EventsinStyle
   
Conoscere i flag di stile di un widget.
---------------------------------------

Ogni widget può avere un set di stili personalizzati tra cui scegliere, e non esiste un modo per sapere a runtime quali sono. Inoltre, siccome gli stili sono solo delle costanti numeriche, non esistono docstring che spiegano rapidamente che cosa fanno. 

Tra l'altro, il nome stesso di "stile" è ingannevole. Alcuni stili effettivamente cambiano solo il look del widget a cui si applicano, ma molti si riferiscono a caratteristiche strutturali più profonde: ``wx.LI_VIRTUAL`` cambia completamente l'utilizzo di un ``wx.ListCtrl``. 

L'unica è affidarsi alla :ref:`documentazione <documentarsi>`: per i widget più comuni, la documentazione wxWidget è la più completa. Per i widget implementati solo in Python, sperimentali, etc., occorre anche provare la demo, o la documentazione interna del widget (per esempio la docstring della classe o del modulo di solito sono molto chiare). L'utility esterna :ref:`EventsinStyle <EventsinStyle>` può essere molto comoda da usare, almeno per i widget che supporta. 

Spesso è questione di pratica. Per esempio, tutti gli stili di un ``wx.TextCtrl`` iniziano con ``wx.TE_*``, e tutti quelli di un ``wx.ComboBox`` iniziano con ``wx.CB_*``. Un buon editor con l'autocompletion in questi casi fa miracoli.


Sapere quali stili sono stati applicati a un widget.
----------------------------------------------------

Così come non è possibile sapere a runtime quali sono gli stili disponibili per un widget, non è neppure possibile sapere quali stili avete applicato al widget una volta che è stato creato. Tuttavia molti widget implementano dei metodi ausiliari con una funziona analoga. 

Per esempio, ``wx.TextCtrl.IsMultiline()`` restituisce ``True`` se avete settato lo stile ``wx.TE_MULTILINE``. 

Ma non dovete farci troppo affidamento. Per esempio, in corrispondenza dello stile ``wx.TE_READONLY`` non esiste nessun metodo ``IsReadOnly``. 

Conoscere quali sono questi metodi è ovviamente una questione di sfogliare con pazienza la documentazione, caso per caso. Ovviamente, un po' di mestiere aiuta... per esempio, prima di guardare alla cieca, iniziate a sfogliare i metodi che iniziano con ``Is*`` e poi quelli con ``Get*``. 


.. index::
   single: wx.Window; SetWindowStyleFlag()
   
Settare gli stili dopo che il widget è stato creato. 
----------------------------------------------------

Per questo, potete usare il metodo ``SetWindowStyleFlag``, che riceve come argomento una normale bitmask di stili. 

Tuttavia non è un'operazione da fare a cuor leggero. A seconda dei widget e degli stili che volete cambiare, potreste causare incongruenze gravi. Certe operazioni potrebbero semplicemente fallire. Dovete fare esperimenti caso per caso, ma in generale non è una pratica consigliabile. 

In ogni caso, è molto probabile che dobbiate chiamare ``Refresh()`` sul widget, per vedere gli effetti delle modifiche. 

.. _extrastyle:

.. index:: 
   single: stili; extra-style

Che cosa sono gli extra-style. 
------------------------------

Definire gli stili come costanti numeriche che si possono combinare con le bitmask è comodo all'inizio, ma prima o poi si arriva a un limite: non ci sono tante potenze di 2 in circolazione. 

Se il widget ha bisogno di pochi stili, tutto va bene. Tuttavia, man mano che occorrono sempre più stili per le più svariate necessità di un widget, ci si scontra con i limiti del tipo numerico (``long``) che C++ riserva per le costanti degli stili. 

Ed ecco che arrivano in soccorso gli "extended style" (o extra style). In pratica si tratta di stili aggiuntivi che non possono stare nello spazio delle normali bitmask, e vanno quindi aggiunti a parte, con il metodo ``SetExtraStyle``. Questo metodo va chiamato ovviamente dopo che il widget è stato creato, ma prima di mostrarlo (chiamando ``Show()`` sul widget stesso o sul suo parent contenitore). 

Di nuovo, la documentazione è l'unico posto dove potete sapere se un certo widget prevede anche degli extra-style. In ogni caso, è utile sapere che ``wx.Window`` ha alcuni extra-style definiti, e siccome ``wx.Window`` è la classe progenitrice di tutti i widget, questi vengono ereditati da tutta la gerarchia (anche se naturalmente per la stragrande maggioranza dei widget non hanno alcun significato). Inoltre, anche ``wx.Frame`` e ``wx.Dialog`` (e quindi le loro sottoclassi dirette) ne aggiungono alcuni. 

* gli extra-style di ``wx.Window`` iniziano tutti con ``wx.WS_EX_*``
* gli extra-style di ``wx.Frame`` iniziano con ``wx.FRAME_EX_*``
* gli extra-style di ``wx.Dialog`` iniziano con ``wx.DIALOG_EX_*``

Questo dovrebbe aiutare un pochino. 

Gli extra-style in genere hanno scopi abbastanza esotici, e servono di rado. Alcuni sono platform-specific, per esempio ``wx.FRAME_EX_METAL`` ha effetto solo sul MacOS. Tuttavia ce ne sono alcuni che dovete tener presente:

* ``wx.WS_EX_VALIDATE_RECURSIVELY`` dice alla finestra di validare non solo tutti i suoi figli diretti (comportamento di default), ma anche i figli dei figli, etc. Utile quando si usano i :ref:`validatori <validatori>`, e la finestra contiene per esempio dei panel con dentro degli altri panel. 

* ``wx.WS_EX_BLOCK_EVENTS`` dice alla finestra di bloccare la propagazione degli eventi che partono dai suoi figli. Gli eventi arrivano fin qui, ma poi non si propagano oltre. Notare che i ``wx.Dialog``, :ref:`a differenza dei frame <wxdialog>`, hanno questo flag impostato per default. 

* ``wx.WS_EX_CONTEXTHELP``, ``wx.DIALOG_EX_CONTEXTHELP``, ``wx.FRAME_EX_CONTEXTHELP`` aggiungono il pulsante della guida rapida alla barra del titolo della finestra. 

Infine, c'è un ultimo problema. Gli extra-style, come abbiamo detto, si possono aggiungere con ``SetExtraStyle`` dopo aver creato il widget. Tuttavia ci sono casi in cui non è possibile aggiungere lo stile in un secondo momento, perché la creazioe del widget determina la sua struttura in modo tale da non poter essere più modificato. E' il caso di ``*_EX_CONTEXTHELP`` (devo dire di non sapere se ci sono altri casi. Nel dubbio, la documetazione ovviamente riporta il problema). 

In questi casi, occorre intraprendere una strada ancora più complicata, nota come "two-step creation", in cui si istanzia per esempio un ``wx.PreFrame``, gli si attribuiscono gli extra-style voluti, e poi lo si trasforma in ``wx.Frame`` aggiungendo gli stili normali. La "two-step creation" è un procedimento non difficile ma comunque avanzato, e può servire in casi differenti (non solo per settare gli extra-style). Per questo motivo gli dedichiamo una pagina separata. 

.. todo:: una pagina sulla two-step creation.

.. note:: Tutta questa complicazione degli extra-style a causa della limitazione delle bitmask, non denuncia forse un problema di design? Risposta breve: sicuramente sì. Detto questo, non è per difendere wxWidgets, ma praticamente qualsiasi grande framework con molta storia alle spalle accumula "regrets" dovuti a scarsa lungimiranza iniziale. Quando wxWidgets è nato, le finestre non avevano pulsanti "context help". Infine, va detto che gli extra-style sono rari: la stragrande maggioranza dei widget ha 3-4 stili definiti, e le bitmask sono più che sufficienti, lasciando spazio anche per aggiunte future. 

