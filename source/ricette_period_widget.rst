.. _periodwidget:

.. index::
   single: wx.lib.newevent; NewCommandEvent
   single: wx.Window; GetEventHandler
   single: wx.PyEvtHandler; ProcessEvent
   single: wx.Event; SetEventObject
   single: eventi; wx.lib.newevent.NewCommandEvent
   single: eventi; wx.Window.GetEventHandler
   single: eventi; wx.PyEvtHandler.ProcessEvent
   single: eventi; wx.Event.SetEventObject
   single: eventi; eventi personalizzati

Un widget per selezionare periodi di tempo.
===========================================

Ho usato questo widget (che avevo scritto in origine per un progetto "vero") per esemplificare la scrittura di :ref:`eventi personalizzati <eventi_personalizzati>`. 

Il suo funzionamento è semplice: permette di selezionare un periodo (per esempio un trimestre), e restituisce gli estremi del periodo come ``datetime.date``.  

.. literalinclude:: /_static/snippets/recipes/period_widget.py
   :lines: 5-
   :linenos:
   
   