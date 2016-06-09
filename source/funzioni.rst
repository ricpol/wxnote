.. _funzioni:

.. index::
   single: funzioni globali

Un tour delle funzioni globali di wxPython.
===========================================

wxPython è un framework anziano, vasto e intricato. Anche solo aprire una shell Python e chiedere ``len(dir(wx))`` vi dà un'idea delle sue dimensioni. In quanto framework a oggetti, wxPython mette a disposizione parecchie centinaia di classi organizzate in una vasta gerarchia. Ma nel namespace ``wx`` vivono anche alcune centinaia di funzioni globali, che rispondono alle più diverse esigenze. Potete rendervi conto facilmente del loro numero::

    >>> import wx, types
    >>> len([i for i in dir(wx) if isinstance(getattr(wx, i), types.FunctionType)])

In questa pagina presentiamo velocemente queste funzioni, raggruppandole per temi. Naturalmente non ci soffermeremo nel dettaglio su ciascuna di esse: per questo basta ricorrere alla documentazione ufficiale. 

.. note:: Per non sovraccaricare l'indice di riferimenti inutili, non vi troverete le funzioni elencate in questa pagina. 


Static method esposti come funzioni globali.
--------------------------------------------

Quasi la metà delle funzioni globali che affollano il namespace ``wx`` sono in realtà degli static method di qualche classe wxPython. E' facile riconoscerli, perché il loro nome segue la convenzione ``[ClassName]_[MethodName]``. Un elenco completo è quindi::

    >>> [i for i in dir(wx) if '_' in i]

Bisogna tener presente che wxPython è in circolazione da prima che Pyhton sviluppasse molte delle feature che noi oggi diamo per scontate. Nei suoi primi anni di vita, wxPython "traduceva" gli occasionali static method delle classi c++ di wxWidgets mettendoli a disposizione appunto come funzioni globali sciolte direttamente nel namespace ``wx``. Successivamente, quando Python ha incorporato il supporto per gli static method, anche wxPython li ha introdotti, seguendo più fedelmente le api di wxWidgets. Di conseguenza, ormai da molti anni queste funzioni globali con l'underscore esistono solo più per retro-compatibilità, e non dovreste usarle. 

La regola di corrispondenza tra funzioni e static method è banale: in pratica, basta sostituire l'underscore con il punto. Per esempio, al posto di chiamare la funzione ``wx.DateTime_Now()``, dovreste usare il metodo ``wx.DateTime.Now()`` (che, essendo appunto uno static method, può essere usato senza bisogno che la classe ``wx.DateTime`` sia precedentemente istanziata).

Altre funzioni in via di dismissione.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

wxPython, come è noto, è un porting in Python del framework c++ wxWidgets. La "traduzione" è fatta in larghissima parte grazie a strumenti automatici, naturalmente: wxPython non esisterebbe senza `SWIG <http://www.swig.org/>`_. Uno dei limiti "storici" della tecnica di traduzione adottata da wxPython, era l'impossibilità di convertire correttamente gli "overloaded methods" di c++. 

wxWidgets fa uso pervasivo, infatti, di metodi costruttori (ma anche molti metodi setter) che possono accettare parametri diversi. Molto spesso in wxPython questi "overloaded methods" sono tradotti con diversi metodi separati, ciascuno con un nome e una "signature" differente. Per esempio, come :ref:`sappiamo<dimensioni>`, in wxPython abbiamo ``wx.Window.SetSize`` e inoltre ``.SetDimensions``, ``.SetRect``, ``.SetSizeWH``. Tutti questi metodi corrispondono all'unico "overloaded method" ``wxWindow::SetSize`` di wxWidgets. 

Questa complicazione sta per essere finalmente superata nella nuova incarnazione di wxPython, il cosiddetto "progetto Phoenix" che è già disponibile in beta e che dovrebbe uscire... in un futuro non ancora determinato. In Phoenix tutti i "metodi doppioni" non saranno più necessari e scompariranno (metodi come ``wx.Window.SetSize``, per esempio, decideranno a runtime quale versione del metodo c++ sottostante invocare, a seconda della signature).

Un aspetto rilevante di questo problema è che, allo stato attuale, alcuni di questi "metodi alternativi" sono esposti come funzioni globali nel namespace ``wx``. Di conseguenza, anche queste funzioni sono in procinto di essere deprecate, quando uscirà Phoenix. La situazione non è ancora definitiva (alcune cose resteranno, altre saranno deprecate, altre spariranno proprio), e quindi non avrebbe senso fornire qui un elenco completo. Di seguito elenchiamo comunque tutte le funzioni globali disponibili in wxPython "classico", segnalando quelle che sono destinate a diventare obsolete in Phoenix.


Funzioni ``Pre[WidgetName]`` per la two-step creation.
------------------------------------------------------

Un altro blocco molto numeroso è quello delle funzioni globali che iniziano con ``Pre``. Queste sono funzioni di convenienza che generano un "pre-widget" utilizzato per la cosiddetta "two-step creation". Si tratta di una tecnica un po' convoluta di creazione di un widget, che si usa nei rari casi in cui è necessario :ref:`settare un extra-style<extrastyle>` che non può essere applicato dopo la creazione del widget. 

.. todo:: una pagina sulla two-step creation.

Esiste una funzione globale ``Pre`` per ciascun widget di wxPython: abbiamo quindi ``wx.PreButton``, ``wx.PreFrame``, etc. etc. La loro utilità è già oggi molto vicina a zero, naturalmente. 

In Phoenix la "two-step creation" non sarà più necessaria, e tutte le funzioni ``Pre`` dovrebbero venire soppresse.


Date e orari.
-------------

wxPython mette a disposizione un sotto-sistema per rappresentare date e orari, incardinato sulle classi ``wx.DateTime``, ``wx.DateSpan`` e ``wx.TimeSpan``. In questo ambito si collocano anche alcune scorciatoie esposte come funzioni globali di varia utilità:

* ``DateTimeFromDateTime``, ``DateTimeFromDMY``, ``DateTimeFromHMS``, ``DateTimeFromJDN``, ``DateTimeFromTimeT``, ``GetCurrentTime``, ``GetLocalTime``, ``GetLocalTimeMillis``, ``GetUTCTime``, ``Now`` 

Ancora una volta, l'utilità di questo sotto-sistema è molto diminuita da quando esiste il modulo ``datetime`` nella libreria standard di Python. Ma occorre sempre ricordare che wxPython è in circolazione da molto più tempo...


Logging.
--------

wxPython mette a disposizione un sotto-sistema per gestire il logging, centrato sulla classe ``wx.Log``. Per usare il logging di wxPython con le impostazioni di default, non è necessario tuttavia accedere direttamente a ``wx.Log``: è sufficiente ricorrere a una delle più comode funzioni globali 

* ``LogDebug``, ``LogError``, ``LogFatalError``, ``LogGeneric``, ``LogInfo``, ``LogMessage``, ``LogStatus``, ``LogStatusFrame``, ``LogSysError``, ``LogTrace``, ``LogVerbose``, ``LogWarning``

Il sistema di logging di wxPython è usato ormai di rado, da quando esiste il modulo ``logging`` nella libreria standard di Python. E' vero però che ``wx.Log`` è più integrato nella logica wxWidgets sottostante a wxPython, e potrebbe fornire messaggi di errore più completi per i problemi innescati strettamente all'interno del codice wxWidgets. 


Drag & Drop.
------------

Le operazioni di Drag & Drop (in sostanza, una forma particolare di copia e incolla) in wxPython sono affidate alle classi ``wx.DropSource`` e ``wx.DropTarget`` e ai loro metodi. Alcune funzioni globali integrano delle funzionalità in questo campo: 

* ``CustomDataFormat``, ``DragIcon``, ``DragListItem``, ``DragString``, ``DragTreeItem``, ``IsDragResultOk``

Le prime quattro sono funzioni-factory da usare come scorciatoie, e restituiscono una istanza della classe ``wx.DragImage`` già preparata per trascinare diversi componenti (``wx.DragImage`` è a sua volta una classe di convenienza ottimizzata per il trascinamento delle immagini, utile soprattutto in ambiente Windows). Queste funzioni, come si intuisce, corrispondono a un costruttore "overloaded" nella corrispondente classe c++. In Phoenix non dovrebbero pertanto essere più necessarie. 

Infine, ``IsDragResultOk`` restituisce ``True`` per indicare un trascinamento andato a buon fine. 

.. todo:: una pagina sul copia e incolla e drag & drop.


Finding.
--------

Alcune funzioni servono semplicemente per cercare un widget:

* ``FindWindowAtPoint``, ``FindWindowAtPointer``, ``FindWindowById``, ``FindWindowByLabel``, ``FindWindowByName``, ``GenericFindWindowAtPoint``

L'esistenza di queste funzioni è più facilmente spiegabile nell'ambito c++ di wxWidgets. In Python, dove i riferimenti agli oggetti possono essere passati liberamente come argomenti di funzioni, l'utilità di meccanismi del tipo ``FindWindowBy...`` è praticamente nulla (è un discorso simile a quello che :ref:`abbiamo già fatto per gli id<gli_id>`). Occasionalmente potreste invece trovare qualche utilità nelle funzioni del tipo ``FindWindowAtPoint[er]``, per esempio se lavorate direttamente con i canvas in applicazioni che disegnano dinamicamente oggetti sullo schermo. 

Alcune funzioni globali restituiscono invece le :ref:`finestre top-level<finestre_toplevel>`, e la ``wx.App`` come sappiamo:

* ``GetApp``, ``GetTopLevelParent``, ``GetTopLevelWindows``

A queste si può aggiungere infine ``GetActiveWindow``, che restituisce il widget attualmente attivo.


Scorciatoie per vari dialoghi.
------------------------------

Alcune funzioni creano e restituiscono istanze già pronte di varie sotto-classi specializzate di ``wx.Dialog``, oppure usano queste per ottenere input dall'utente e restituiscono direttamente il risultato dopo aver chiuso e distrutto il dialogo:  

* ``AboutBox``, ``DirSelector``, ``FileSelector``, ``GetColourFromUser``, ``GetFontFromUser``, ``GetNumberFromUser``, ``GetPasswordFromUser``, ``GetSingleChoice``, ``GetSingleChoiceIndex``, ``GetTextFromUser``, ``LoadFileSelector``, ``MessageBox``, ``SaveFileSelector``

Sono molto comode da usare nei casi più comuni, anziché istanziare direttamente i vari dialoghi specifici (``wx.FontDialog``, ``wx.DirDialog``, etc.) e poi chiuderli e distruggerli manualmente. 

In questa categoria includiamo anche due funzioni per le ``wx.TipWindow``:

* ``CreateFileTipProvider``, ``ShowTip``

.. todo:: una pagina sulle sottoclassi di wx.Dialog. 


Costruttori di sizer item.
--------------------------

:ref:`Come sappiamo<sizeritem>`, un ``wx.SizerItem`` è un elemento di un sizer. In genere otteniamo una istanza di questa classe come valore di ritorno di ``wx.Sizer.Add``, e nella pratica quotidiana non abbiamo mai bisogno di istanziare direttamente né ``wx.SizerItem`` né ``wx.GBSizerItem`` (la sottoclasse specializzata per i ``wx.GridBagSizer``). 

Ancor meno bisogno, quindi, abbiamo di queste funzioni globali che restituiscono un ``wx.[GB]SizerItem``: 

* ``GBSizerItemSizer``, ``GBSizerItemSpacer``, ``GBSizerItemWindow``, ``SizerItemSizer``, ``SizerItemSpacer``, ``SizerItemWindow``

Inoltre, come è facile intuire, si tratta di funzioni globali che corrispondono a costruttori "overloaded" delle corrispondenti classi c++. In Phoenix niente di tutto questo dovrebbe essere più necessario.


Font.
-----

In wxWidgets e wxPython, la classe ``wx.Font`` serve a conservare informazioni relative a un font. 

Alcune funzioni globali sono delle scorciatoie per creare una istanza di ``wx.Font``. A parte la prima, le altre non dovrebbero più servire in Phoenix:

* ``FFont``, ``FFontFromPixelSize``, ``Font2`` (un alias di ``FFont``), ``FontFromNativeInfo``, ``FontFromNativeInfoString``, ``FontFromPixelSize``

Infine, ``GetNativeFontEncoding`` e ``TestFontEncoding`` sono relitti del vecchio sistema di supporto degli encoding di wxWidgets, che in wxPython è completamente superato. 

.. todo:: una pagina sui font


Primitive per il disegno.
-------------------------

Queste funzioni possono essere usate per ricavare informazioni sulla geometria del display (lo schermo o l'area di lavoro):

* ``ClientDisplayRect``, ``ColourDisplay``, ``DisplayDepth``, ``DisplaySize``, ``DisplaySizeMM``, ``GetClientDisplayRect``, ``GetDisplayDepth``, ``GetDisplayPPI``, ``GetDisplaySize``, ``GetDisplaySizeMM``, ``GetXDisplay``

Altre funzioni riguardano differenti primitive per il disegno. Tre di esse permettono di istanziare un ``wx.Rect`` (e probabilmente saranno soppresse in Phoenix per le consuete ragioni):

* ``RectPP``, ``RectPS``, ``RectS``

Inoltre, ``IntersectRect`` calcola il rettangolo intersezione di altri due rettangoli. 

Due funzioni creano un ``wx.Point2D`` (un ``wx.Point`` con coordinate float):

* ``Point2DCopy``, ``Point2DFromPoint``

Tre funzioni creano una ``wx.Region``:

* ``RegionFromBitmap``, ``RegionFromBitmapColour``, ``RegionFromPoints``

Due funzioni manipolano un ``wx.Cursor``:

* ``SetCursor``, ``StockCursor``

Infine, in questa categoria includiamo anche due funzioni che creano un qualche tipo di DC: 

* ``AutoBufferedPaintDCFactory``, ``MemoryDCFromDC``


.. todo:: una pagina su come disegnare


Immagini e colori.
------------------

Molte funzioni globali lavorano con le immagini. Per iniziare, molte sono funzioni di conversione, e hanno la forma ``[someClass]From[someClass]``. In Phoenix dovrebbero essere tutte soppresse o quasi: in molti casi basterà usare il costruttore "overloaded" (per esempio, ``wx.BitmapFromImage(image)`` sarà deprecata in favore di ``wx.Bitmap(image)``); in altri casi, verranno introdotti degli static methods corrispondenti (per esempio, ``wx.BitmapFromBuffer()`` diventerà ``wx.Bitmap.FromBuffer()``): 

* ``BitmapFromBits``, ``BitmapFromBuffer``, ``BitmapFromBufferRGBA``, ``BitmapFromIcon``, ``BitmapFromImage``, ``BitmapFromXPMData``, ``BrushFromBitmap``, ``CursorFromImage``, ``IconBundleFromFile``, ``IconBundleFromIcon``, ``IconBundleFromStream``, ``IconFromBitmap``, ``IconFromLocation``, ``IconFromXPMData``, ``ImageFromBitmap``, ``ImageFromBuffer``, ``ImageFromData``, ``ImageFromDataWithAlpha``, ``ImageFromMime``, ``ImageFromStream``, ``ImageFromStreamMime``

Alcune funzioni restituiscono una classe "vuota" (anche queste dovrebbero sparire in Phoenix):

* ``EmptyBitmap``, ``EmptyBitmapRGBA``, ``EmptyIcon``, ``EmptyImage``

Tre funzioni costruiscono un ``wx.Colour`` (e non saranno più necessarie in Phoenix):

* ``ColourRGB``, ``MacThemeColour``, ``NamedColour``

Infine, ``InitAllImageHandlers`` era usata per inizializzare gli handler dei tipi di immagini disponibili per ``wx.Image`` (ormai da tempo questa funzione è una NOP lasciata per retro-compatibilità: l'inizializzazione avviene di default quando si crea la ``wx.App``).

.. todo:: una pagina sulle immagini: wx.Image, wx.Bitmap... 


Eventi, thread di esecuzione.
-----------------------------

Abbiamo :ref:`dedicato<eventibasi>` :ref:`ormai<eventi_avanzati>` :ref:`molte<eventitecniche>` :ref:`pagine<eventitecniche2>` :ref:`agli<eventloop>` :ref:`eventi<integrazione_event_loop>`, e non c'è quindi più bisogno di spendere parole a proposito di queste funzioni globali: 

* ``CallAfter``, ``NewEventType``, ``PostEvent``, ``SafeYield``, ``Yield``, ``YieldIfNeeded``, ``WakeUpIdle``

Alcune funzioni gestiscono processi esterni:

* ``Execute``, ``GetProcessId``, ``Kill``, ``LaunchDefaultApplication``, ``LaunchDefaultBrowser``, ``Shell``, ``SysErrorCode``, ``SysErrorMsg``

Una sola funzione globale ha a che fare direttamente con i thread:

* ``WakeUpMainThread``

Così come wxPython non adotta il supporto per i thread di wxWidgets, preferendo affidarsi alla libreria standard di Python, anche ``wxMutex`` di wxWidgets è assente in wxPython. Queste due funzioni globali sono ancora in giro per retro-compatibilità:

* ``MutexGuiEnter``, ``MutexGuiLeave``

Infine, alcune funzioni per "dormire":

* ``MicroSleep``, ``MilliSleep``, ``Sleep``, ``Usleep`` 

.. todo:: una pagina sui thread


Informazioni sul sistema.
-------------------------

wxPython è dotato di alcuni strumenti per ottenere informazioni sull'ambiente in cui deve operare: per esempio la classe ``wx.PlatformInfo``, ma anche alcune funzioni globali che elenchiamo qui di seguito. Spesso si tratta di strumenti che possono essere sostituiti con successo da moduli come ``sys`` e ``os`` nella libreria standard di Python. Ma alcune funzioni più specifiche possono tornare utili. 

Poche funzioni raccolgono informazioni sull'hardware:

* ``GetBatteryState``, ``GetPowerType``

Altre funzioni riguardano il sistema operativo:

* ``ExpandEnvVars``, ``GetFreeMemory``, ``GetFullHostName``, ``GetHostName``, ``GetLocale``, ``GetOsDescription``, ``GetOsVersion``, ``IsPlatform64Bit``, ``IsPlatformLittleEndian``, ``Shutdown``

Alcune ci fanno sapere qualcosa sull'utente loggato:

* ``GetEmailAddress``, ``GetHomeDir``, ``GetUserHome``, ``GetUserId``, ``GetUserName`` 

Infine, due funzioni ci aiutano in particolare con il supporto Unicode di Python 2: 

* ``GetDefaultPyEncoding``, ``SetDefaultPyEncoding``


Varie.
------

Raccogliamo qui alcune funzioni che non rientrano in nessuna delle categorie precendenti. 

Due funzioni possono essere utilizzate per gestire la :ref:`chiusura di emergenza<wxexit>` della ``wx.App``:

* ``Exit``, ``SafeShowMessage``

``Trap`` solleva una eccezione nel debugger, ovvero il flusso di controllo passa al debugger (se avete un debugger associato al processo Python in corso, naturalmente: se no il programma si limita a terminare in modo anomalo). 

Alcune funzioni interrogano lo stato di mouse e tastiera, e impostano la "clessidra" del cursore: 

* ``BeginBusyCursor``, ``EndBusyCursor``, ``GetKeyState``, ``GetMousePosition``, ``GetMouseState``, ``IsBusy``

Tre funzioni manipolano :ref:`gli id<gli_id>`, come sappiamo: 

* ``GetCurrentId``, ``NewId``, ``RegisterId``

Alcune funzioni riguardano gli :ref:`stock buttons<stockbuttons>`:  

* ``GetStockHelpString``, ``GetStockLabel``, ``IsStockID``, ``IsStockLabel``

Di ``StripMenuCodes`` :ref:`abbiamo parlato<menu_basi2>` a proposito dei menu; anche ``GetAccelFromString`` rientra nello stesso ambito, ma sarà deprecata in Phoenix e peraltro non è mai stata particolarmente utile. 

``EnableTopLevelWindows`` può essere usata come valvola di sicurezza per congelare temporaneamente tutta la gui. Per esempio, è usata internamente da ``wx.SafeYeld``. 

``GetTranslation`` riguarda il supporto per il testo multilingue. 

``FileTypeInfoSequence`` e ``NullFileTypeInfo`` creano un ``wx.FileTypeInfo`` (c'entra il supporto MIME di wxPython).

``Bell`` suona il system bell (!), ``deprecated`` può essere usato per emettere una deprecation warning personalizzata, ``SoundFromData`` costruisce un ``wx.Sound``, ``version`` restituisce la versione in uso di wxPython. 

