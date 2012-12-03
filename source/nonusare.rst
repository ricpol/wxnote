.. _non_usare:

Gli strumenti da non usare.
===========================

Avvertenza: questa pagina è "opinionated", come si dice. La includo in questi appunti per mantenere una risposta pronta alla domanda che sento spesso: che cosa ne pensi dei "gui builder"? Posso usarli? Semplificano il lavoro? 

La risposta breve è no, non usateli, punto. Dopo di che, se volete continuare a leggere, tenete presente che comunque questa è solo la mia opinione, e siete liberi di tenervi la vostra.

.. index::
   single: Boa Constructor
   
Boa Constructor.
----------------

Non usate Boa Constructor. Ecco. 

Prima di tutto, è un progetto vecchio e ormai abbandonato: le ultime attività risalgono al 2007, per dire. Nel frattempo wxPython è andato molto avanti, e (cosa ancora più importante) nessuno testa più Boa in modo sistematico da una vita. 

Detto questo, Boa cerca di essere un RAD per wxPython, e in quanto tale ha tutti i difetti tipici di un RAD. Produce codice sporchissimo, sul quale comunque dovrete prima o poi mettere le mani, per qualunque applicazione appena un po' completa, perché ci sono molte cose che Boa non supporta o supporta male. Come in tutti i RAD, è difficilissimo fattorizzare il codice e renderlo modulare e riutilizzabile. 

Detto con franchezza, il motivo per cui viene ancora usato e se ne sente parlare ancora così tanto, è che molti si avvicinano a wxPython con la speranza di trovare una specie di Visual Basic "free", e Boa è la cosa che somiglia di più ai RAD chiavi-in-mano. 

Ora, non è il caso di ripetere la litania dei motivi per cui usare i RAD è **Male**. Chiunque programmi in Python dovrebbe portarsi questa convinzione nel dna. Ma in ogni caso, Boa è poco soddisfacente anche come RAD. 

.. index::
   single: wxGlade
   
wxGlade.
--------

E non usate neppure wxGlade. 

Devo dire che wxGlade mi sta molto più simpatico di Boa. Si propone come semplice "assemblatore di gui", senza avere la pretesa di essere un RAD completo, e questo è senz'altro un bene. Inoltre, di recente sembra aver ripreso un po' di attività, quindi non è abbandonato come Boa. 

wxGlade ha un'api per generare widget "custom", ossia non ancora supportati. Il che è un'ottima cosa, tranne naturalmente che ci si può chiedere se vale la pena di studiarsi le api di wxGlade in aggiunta a wxPython. 

Anche wxGlade genera codice molto sporco e ripetitivo, e anche in questo caso è probabile che prima o poi finirete per doverci mettere le mani comunque. Forse è un po' più facile, rispetto a Boa, generare "porzioni" di interfaccia riutilizzabili, ma comunque una vera fattorizzazione del codice resta un miraggio. 

Forse wxGlade può essere adatto a costruire rapidamente interfacce non troppo complesse. Ma il problema è che, con un po' di esperienza, proprio le interfacce semplici sono quelle che fate prima a realizzare a mano, producendo codice più compatto e pulito. Inoltre, se poi l'interfaccia cresce nel tempo e dovete metterci le mani, vi ritrovate a gestire il solito polpettone di codice illeggibile. 

Forse wxGlade può essere di aiuto all'inizio, se si ha paura di perdersi nel mare delle opzioni, metodi e proprietà di ogni oggetto wxPython. Ma anche in questo caso, probabilmente si fa prima a imparare scrivendo il codice a mano. 

.. index::
   single: XmlResource()

XmlResource.
------------

Molti sostengono che il codice per disegnare le gui sia boilerplate degradante da scrivere. Costoro in genere sostengono che la gui dovrebbe essere definita da una risorsa esterna (tipicamente un file xml) e caricata dinamicamente dentro il programma. 

Gli fai notare che così bisogna sempre lottare per ficcare in uno schema xml tutte le sottigliezze espressive che puoi molto più facilmente ottenere con qualche riga di codice. Loro ribattono che, se una gui è complicata al punto da non poter essere espressa da uno schema xml, vuol dire che è troppo complicata, e andrebbe semplificata. Il che, a mio avviso, è un po' come non rispondere. 

E quando gli fai notare che scrivere un file xml a mano è di gran lunga più degradante che scrivere codice boilerplate, vacillano un po', ma poi ribattono che: basta usare un editor xml! Magari visuale! Insomma, quasi quasi un RAD...

Un altro argomento spesso citato in favore degli schemi xml, è che aiuterebbero a separare la gui dal codice di controllo, favorendo il pattern "model-controller-view", autentico sacro graal della programmazione a oggetti (e su questo non mi permetto di ironizzare, in effetti). Ma questo è un miraggio in wxPython, come in tutti i gui framework. O meglio, come vedremo, si può in effetti applicare MCV a una applicazione con gui, ma è un processo che passa per strade molto distanti dalla banale riduzione della gui a un xml. Nel frattempo, lo schema xml con la sua tragica staticità toglie tutta l'espressività della programmazione dinamica, tutta la flessibilità di poter decidere le cose a runtime. 

.. todo:: una pagina su MVC con collegamento a questa.

Detto questo, wxPython in effetti offre un modo di caricare dinamicamente schemi xml, grazie alla classe ``wx.xrc.XmlResource`` (cercate "xml" nella demo per saperne di più). E se guardate nella directory della demo, trovate anche ``.../wxPython2.8 Docs and Demos/scripts/xrced.pyw``, che è un grazioso editor visuale di schemi xml correttamente formati per essere usati con wxPython. Potete provarlo: ricorda vagamente wxGlade. 

Ora intendiamoci, i sostenitori delle gui xml hanno le loro ragioni. Ma la mia opinione è che, a ben vedere, sono ragioni "eterogenee" alla programmazione di interfacce grafiche. Voglio dire, se sei un sistemista, hai sempre scritto software server-side, e un giorno ti chiedono una gui al volo perché anche i non addetti possano vedere un log di sistema (tu ovviamente lo scorri con gli occhi, stile "Matrix"), allora capisco che uno schema xml ti sembra la soluzione più naturale per sbrigare in fretta l'odioso compito. 

Ma la programmazione di gui, credeteci o meno, è un'arte tanto quanto il resto della programmazione. Si possono fare cose molto raffinate, e l'espressività di Python è di grande aiuto in questo. 

Quindi in conclusione, no, non usate neppure xml. 

Grazie.

