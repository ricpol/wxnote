.. _periodwidget:


Un widget per selezionare periodi di tempo.
===========================================

Ho usato questo widget (che avevo scritto in origine per un progetto "vero") per esemplificare la scrittura di :ref:`eventi personalizzati <eventi_personalizzati>`. 

Il suo funzionamento è semplice: permette di selezionare un periodo (per esempio un trimestre), e restituisce gli estremi del periodo come ``datetime.date``.  

.. literalinclude:: /_static/snippets/recipes/period_widget.py
   :lines: 5-
   :linenos:
   
   