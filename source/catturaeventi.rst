.. highlight:: python
   :linenothreshold: 15
   
.. _catturaeventi:

Catturare tutti gli eventi di un widget.
========================================

Come abbiamo visto :ref:`parlando degli eventi <eventibasi>`, non è facile in generale sapere quali eventi può emettere un determinato widget. 

Questa ricetta cerca di scoprirlo con un approccio naif: semplicemente collega a un widget *tutti i binder disponibili* nel namespace ``wx``. Chiaramente la maggior parte non sarà mai davvero emessa, ma poco importa. 

Potete inserire il widget che desiderate testare, alla riga 8. 

Ho eliminato gli eventi "collettivi" come ``wx.EVT_MOUSE_EVENTS`` (riga 31). Inoltre alcuni eventi sono innescati di continuo, e pertanto producono "rumore di fondo": vi conviene eliminarli. Alle righe 23-25 ne ho eliminati alcuni che trovo particolarmente fastidiosi, ma naturalmente potete ri-aggiungerli e toglierne altri, come preferite. 

In ogni caso, per aiutare a rendere l'output più pulito, se l'evento è ripetuto viene stampato solo un trattino (righe 41-45).

.. literalinclude:: /_static/snippets/recipes/all_events_catcher.py
   :lines: 5-
   :linenos:
   
Questa ricetta è uno script che mi ero scritto per capire meglio come vengono generati il eventi. In seguito mi sono accorto che nella libreria di wxPython è già compresa una versione molto più "professionale" e completa della stessa idea, nel modulo ``wx.lib.eventwatcher.py``. Se lo eseguite, avvia una demo che mostra gli eventi di un frame di prova. Ma potete usarlo per monitorare gli eventi di qualsiasi frame scritto da voi stessi. Il suo uso è semplicissimo::

    from wx.lib.eventwatcher import EventWatcher
    
    my_frame = MyFrame(...)
    my_frame.Show()
    
    ewf = EventWatcher(my_frame) 
    ewf.watch(my_frame)
    ewf.Show()

Per certi (pochi) aspetti preferisco ancora la mia versione: per esempio, EventWatcher cattura solo un ``wx.EVT_BUTTON`` senza segnalare i contestuali ``wx.EVT_LEFT_DOWN`` e ``wx.EVT_LEFT_UP``. 

