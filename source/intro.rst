Introduzione.
=============

Benvenuti. Queste note non sono un manuale completo: tuttavia cerco di essere abbastanza sistematico e di andare per gradi, quindi ecco... diciamo che *aspirano* a essere un manuale, se non completo almeno buono, e comunque l'unico in italiano di un certo "spessore" (almeno a mia conoscenza). 

Questa prima pagina contiene le solite note introduttive... se non sapete nulla di wxPython, cominciate di qui. Altrimenti, basta un'occhiata al volo.


Licenza.
--------

Per prima cosa, questi appunti sono distribuiti con licenza `Creative Commons BY-NC-SA 3.0 <http://creativecommons.org/licenses/by-nc-sa/3.0/it/>`_. Detto in breve, siete liberi di tagliare e copiare e incollare e modificare... ma dovete sempre citarmi, e non potete fare uso commerciale di queste cose. 



Che cos'è wxPython?
-------------------

wxPython è un GUI framework: un set organizzato di strumenti per scrivere l'interfaccia grafica delle vostre applicazioni. E' il porting per Python di wxWidget, uno dei più "vecchi" e consolidati gui framework in circolazione, essendo nato nel lontano 1992. wxWidgets è scritto in C++, e oltre che per Python, ne esistono bindings per Perl, Ruby, Java, PHP, C#, Haskell, e molti altri linguaggi/ambienti. 

wxWidgets/wxPython è "abbastanza" multipiattoforma: funziona sotto Windows (32 e 64 bit), MacOS, Linux, Solaris, OS/2, e molti altri. Però manca ancora il supporto per Android e iOS, e quindi è (al momento) ancora ancorato al vecchio mondo desktop. 

wxWidgets non ha un toolkit grafico suo proprio, ma i vari port sono realizzati "appoggiandosi" a diversi toolkit esterni: su Windows si utilizzano le Win API, su Mac Carbon o Cocoa, su Linux si usa GTK, etc. Questo vuol dire che, anche se i widget di base sono multipiattaforma in modo trasparente, ci si imbatte spesso in feature che vengono "tradotte" in modo leggermente diverso sulle diverse piattaforme, o che sono specifiche solo di una di esse. 

L'implementazione più ampia è sicuramente quella per Windows. Questo significa che, se sviluppate in Windows ma vi interessa mantenere la compatibilità sulle altre piattaforme, dovete prestare particolare attenzione a non introdurre elementi "nativi" che non hanno corrispondenza altrove. 

wxPython traduce wxWidget, permettendo di usarlo nelle applicazioni Python. Questo bindig per molti aspetti è perfino "superiore" all'originale, perché introduce gran parte della flessibilità e dell'espressività tipiche di Python rispetto a C++. Tuttavia c'è un punto critico importante da considerare: al momento, non è ancora supportato Python 3. 

In realtà, wxPython è "antico" quasi quanto wxWidget stesso: le prime versioni risalgono alla metà degli anni '90, e, per esempio, giravano ancora con Window 3.1. Questo vuol dire che wxPython è più vecchio di molte parti di Python che noi oggi diamo per scontate (``datetime``, per dire). Nel corso degli anni, molti "wxPython regrets" si sono accumulati, e oggi Robin Dunn è al lavoro per una nuova riscrittura dell'intero framework, che prende il nome di "progetto Phoenix". Il supporto per Python 3 potrebbe arrivare con l'arrivo di Phoenix, oppure potrebbe essere anticipato, se Phoenix dovesse dimostrarsi un lavoro troppo lungo. 

In ogni caso, oggi wxPython è ancora indietro rispetto allo sviluppo di Python. Oltre a questo, occorre tener presente che wxPython è pur sempre una sottile buccia di codice Python sopra un framework C++. Per quanto wxPython faccia un lavoro meraviglioso nell'adattare le cose dietro le quinte, per chi è abituato a scrivere in Python, l'API di wxPython sembra ben poco... pytonica: getter e setter come se piovesse, costanti globali, eccetera eccetera. 

Con questo, sembra che abbia elencato solo i difetti di wxWidgets/wxPython: chiaramente ci sono tutti i pregi, e non sono pochi. Ma se state leggendo queste pagine, do per scontato che siate già consapevoli dei pregi, e convinti a usare wxPython: per cui, sadicamente, smetto qui.


Convenzioni usate in questi appunti.
------------------------------------

Conviene dirlo subito: wxPython non rispetta la PEP8, e di conseguenza neppure io lo farò. Ecco fatto. 

Il motivo è semplice: siccome wxPython traduce un framework C++, ha scelto di mantenere molte delle convenzioni di wxWidgets. In particolare, non solo i nomi delle classi, ma anche **i nomi dei metodi sono CamelCase** in wxPython. 

Per questi appunti, adotterò la strategia che uso di solito nel mio codice: i nomi wxPython restano ovviamente CamelCase, ma **i nomi delle funzioni/metodi aggiunti rispettano la PEP8**, e quindi sono minuscoli_con_underscore. 

Quindi vi capiterà di leggere codice scritto così::

    class MyWidget(wx.Button):   # le classi sono sempre CamelCase
    
        def SetLabel(self, val): # metodo wxPython -> CamelCase
            pass
        
        def on_click(self, evt): # metodo aggiunto da me -> min_con_underscore
            pass
            
Il motivo è che così si vede subito quali nomi fanno parte dell'API di wxPython, e quali invece sono aggiunti. 

Per il resto, non c'è molto da dire. Aggiungo solo che **i nomi degli identificatori sono in inglese** (come dovrebbe sempre essere), ma **i commenti e le docstring sono in italiano** (visto che questa, alla fine, è una guida in italiano). 

