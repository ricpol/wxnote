.. highlight:: python
   :linenothreshold: 15
   
.. _catturaeventi:

Catturare tutti gli eventi di un widget.
========================================

Come abbiamo visto :ref:`parlando degli eventi <eventibasi>`, non è facile in generale sapere quali eventi può emettere un determinato widget. 

Questa ricetta cerca di scoprirlo con un approccio naif: semplicemente collega a un widget *tutti i binder disponibili* nel namespace ``wx``. Chiaramente la maggior parte non sarà mai davvero emessa, ma poco importa. 

Potete inserire il widget che desiderate testare, alla riga 9. 

I due widget "riempitivi" servono per esempio a testare il passaggio del focus. 

Ho eliminato gli eventi "collettivi" come ``wx.EVT_MOUSE_EVENTS`` (riga 37). Inoltre alcuni eventi sono innescati di continuo, e pertanto producono "rumore di fondo": vi conviene eliminarli. Alle righe 23-27 ne ho eliminati alcuni che trovo particolarmente fastidiosi, ma naturalmente potete ri-aggiungerli e toglierne altri, come preferite. 

In ogni caso, per aiutare a rendere l'output più pulito, se l'evento è ripetuto viene stampato solo un punto (righe 43-47).


.. literalinclude:: /_static/snippets/recipes/all_events_catcher.py
   :lines: 5-
   :linenos:
   
   
   