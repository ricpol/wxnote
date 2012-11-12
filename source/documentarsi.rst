Documentazione wxPython.
========================

wxPython è un framework vasto e complesso, e soprattutto all'inizio può disorientare. Questa sezione elenca una serie di risorse che *dovete assolutamente* tenere a portata di mano quando scrivete codice wxPython. 

Il problema con tutti questi materiali, ovviamente, è che sono in inglese. Non esiste nulla in italiano... il che sarebbe poi la ragione dell'esistenza di questi appunti. Tuttavia non potete prescindere da un po' di fatica linguistica, se volete fare qualche progresso con wxPython (e con Python, e con la programmazione in generale). 


La demo.
--------

La demo è il primo posto dove in genere vi conviene guardare. Se non c'è nella demo, le cose si complicano. 

La demo è un pacchetto che si scarica e si installa a parte `sul sito di wxPython <http://www.wxpython.org/download.php#stable>`_ (cercate "wxPython Demo" tra i vari pacchetti). Una volta aperta, presenta un elenco di esempi organizzati in un albero che potete sfogliare. Ciascun esempio mostra anche il suo codice sorgente e delle note utili. Una possibilità molto comoda è che potete fare delle modifiche direttamente nel codice, e vedere subito il risultato. 

L'unico problema della demo è che spesso gli esempi sono eccessivamente complessi: nello sforzo di dimostrare tutte le possibilità dei vari widget, il codice si allunga a dismisura, e non è sempre facile orientarsi. 


Gli altri esempi.
-----------------

Scaricando il pacchetto della demo, installate anche alcune piccole applicazioni di esempio che trovate installate in ``.../wxPython2.8 Docs and Demos/samples``. Alcuni di questi esempi riguardano tecniche complesse ("mainloop", per esempio...), e altri sono applicativi molto estesi ("ide", "PySketch"); però la maggior parte sono interessanti e facili da capire. Forse i tre più semplici per iniziare sono:

* "simple" è un'applicazione basilare, a titolo di esempio;

* "doodle" illustra le basi delle tecniche di disegno ("PySketch" è molto più completo, ma è lungo da analizzare);

* "hangman" è una mini-applicazione ben strutturata;

Molto utili sono anche gli snippet raccolti in ``.../wxPython2.8 Docs and Demos/wxPython/samples/wxPIA_book``. Questi sono esempi tratti dal libro `WxPython in Action <http://www.manning.com/rappin/>`_. L'unico problema di questi esempi è che, essendo tratti dal libro, sono organizzati secondo i capitoli, ed è un po' noioso provarli tutti per vedere cosa fanno.


La documentazione wxPython.
---------------------------

La documentazione delle API di wxPython è solo online. Potete trovare la versione "ufficiale" generata con Epydoc a `questo indirizzo <http://www.wxpython.org/docs/api/>`_, ma vi consiglio di quardare prima quella "alternativa" mantenuta da Andrea Gavana `qui <http://xoomer.virgilio.it/infinity77/wxPython/APIMain.html>`_. Questa seconda documentazione non è ancora completa, ma è generata con Sphinx, ed è molto più chiara e ricca. Dovrebbe diventare la documentazione ufficiale della prossima "reincarnazione" di wxPython, il cosiddetto "progetto Phoenix" di cui si parla ormai da qualche anno.


Ovviamente la documentazione delle API è fondamentale, ma solo se sapete già che cosa state cercando...


La documentazione wxWidget.
---------------------------

Come ormai dovreste sapere, wxPython è il porting per Python del framework C++ wxWidgets. La documentazione delle API di wxWidgets è molto completa e ricca, ed è compresa nel pacchetto della demo, per cui la trovate installata in 
``.../wxPython2.8 Docs and Demos/docs``. In alternativa, potete consultare la versione on line `qui <http://docs.wxwidgets.org/stable/>`_. 

Naturalmente, il problema qui è che tutta la sintassi, gli esempi, le convenzioni tipografiche etc., si riferiscono al mondo C++. Non è troppo difficile, con un po' di allenamento, tradurre al volo nel nostro linguaggio preferito; tuttavia non è neppure proprio facilissimo. 

Tuttavia la documentazione wxWidgets resta in certi casi l'ultima risorsa. Tra l'altro, al suo interno si trovano anche delle note specifiche per wxPython (e wxPerl!), nei punti in cui le API differiscono. 


Events in Style!
----------------

"Events in Style" è un modulo del sempre geniale Andrea Gavana (disponibile `qui <http://xoomer.virgilio.it/infinity77/Zipped/EventsInStyle.py>`_, semplicemente salvate la pagina). E' una piccola gui che punta alla documentazione online (va usato con una connessione internet) e scarica la parte relativa agli eventi e agli stili (da cui il nome!) disponibili per ciascun widget. 

E' uno strumento molto comodo per farsi un'idea veloce di due aspetti (eventi e stili, appunto) che di solito nessuno riesce mai a ricordarsi. 


Libri wxPython.
---------------

Ce ne sono due che valgono la pena:

* `WxPython in Action <http://www.manning.com/rappin/>`_, già menzionato sopra, è scritto in collaborazione con Robin Dunn, l'autore di wxPython. E' un manuale ben fatto, di livello medio-base. Ci trovate i fondamentali ben spiegati, ma niente di particolarmente esotico. 

* `wxPython 2.8 Application Development Cookbook <http://www.packtpub.com/wxpython-2-8-application-development-cookbook/book>`_ di Cody Precord (l'autore dell'IDE Editra, vedi sotto), è un manuale più avanzato, che offre anche esempi di buone pratiche di programmazione. Leggetelo solo se avete già un'idea di base di come funziona wxPython. Altrimenti può essere disorientante. 


Siti wxPython.
--------------

Ce ne sono troppi. 

Il problema qui è che wxPython è un framework *anziano* e *popolare*, il che significa che negli anni si è accumulata in rete una impressionante quantità di materiale, spesso vecchio (vedi alla voce "anziano") e/o di scarsa qualità (vedi alla voce "popolare"). 

.. todo:: Al momento, non riesco a consigliare nessun sito di cui mi fido ciecamente. In futuro, prometto di fare una nuova indagine.

Per dovere di cronaca, devo citare almeno il `wiki ufficiale <http://wiki.wxpython.org/>`_, che però è poco sistematico, e talvolta presenta ancora degli esempi superati. Tuttavia, molte pagine sono invece assolutamente ben scritte e aggiornate. 


Un buon editor.
---------------

Sembra facile, ma se lavorate con un framework complesso come wxPython, scordatevi IDLE. Avete bisogno di un editor che faccia almeno queste cose:

* code folding: il codice wxPython tende ad essere lungo. Senza il code folding, passerete la vita a fare scrolling su e giù. 

* autocompletion: come per tutti i framework complessi, il problema numero uno è orientarsi nella selva delle classi e dei metodi. Il problema numero due, è rircordarsi come si scrivono esattamente. Senza l'autocompletion, siete fritti. 

* calltips: o come volete chiamarli, insomma, la docstring della funzione/metodo che appare automaticamente quando scrivete il nome. Il problema numero tre è ricordarsi l'infinità di named arguments che può avere un metodo (specialmente un costruttore) wxPython. Senza i calltips, siete fritti. 

Ora, tutti gli editor decenti hanno queste feature: scegliete quello che preferite. Tenete solo a mente che non è il caso di ricorrere per forza a elefanti come Eclipse. Non è questa la sede per aprire l'eterna discussione su quale editor utilizzare. Se non avete proprio nessuna idea, potete provare `Editra <http://editra.org/>`_: è un IDE abbastanza completo, scritto da Cody Precord nientemeno che in wxPython. E' diventato un po' l'editor "ufficiale" di wxPython, e quindi è incluso nelle distribuzioni che scaricate, ma vi conviene visitare il sito per avere la versione più aggiornata, scaricare i plugin, etc.


La vecchia buona shell. 
-----------------------

E infine, non dimenticate di tenervi sempre accanto una shell aperta, quando programmate. Quando siete in dubbio, ``dir`` è sempre vostro amico per un primo orientamento. 

Per esempio::

    >>> import wx
    >>> [i for i in dir(wx.TextCtrl) if 'Background' in i]
    
vi rivela tutti i metodi disponibili in ``wx.TextCtrl`` che in qualche modo riguardano lo sfondo. 


