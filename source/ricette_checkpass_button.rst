.. _ricette_checkpass_button:

Un pulsante che controlla le credenziali prima di procedere.
============================================================

Questo pulsante può essere usato al posto di un normale ``wx.Button``, ed è uguale in tutto e per tutto. La sola differenza è che, in risposta a un ``EVT_BUTTON`` (un normale clic), chiede all'utente di inserire una password, e solo in caso positivo passa a eseguire il callback associato.

.. literalinclude:: /_static/snippets/recipes/permission_button.py
   :lines: 5-
   :linenos:

Ecco come si può manipolare la catena degli eventi per ottenere effetti un po' più concreti degli esempi presentati nei :ref:`capitoli precedenti <eventi_avanzati>`. 
Nel mondo reale, chiaramente, la funzione ``check_psw`` potrebbe essere sostituita da un controllo su nome utente e password (confrontando con un database), o con un più avanzato sistema di permessi. 

E' utile ripeterlo: non è necessario intervenire sulla propagazione degli eventi per ottenere un effetto del genere. Per esempio, si potrebbe facilmente scrivere un decoratore da applicare ai singoli callback che necessitano di un controllo sulle credenziali (a-la-Django, per intenderci). E questo potrebbe essere un metodo più "corretto" da usare, perché non ricorre a una specificità della gui per la logica di business dell'applicazione. 

Tuttavia è utile anche sapere che queste cose, quando serve, si possono fare restando all'interno della logica di wxPython.

