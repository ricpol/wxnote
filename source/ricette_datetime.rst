.. index:: 
   single: date
   single: wx.DateTime
   single: date; wx.DateTime

.. _ricette_datetime:

Convertire le date tra Python e wxPython.
=========================================

Questa ricetta è un vero e proprio classico, e ne trovate diverse versioni in rete. Vale la pena comunque di riportarla, e avercela sottomano. 

Python utilizza per le date la comoda struttura ``datetime.datetime``, e in genere vogliamo lavorare con questa. Purtroppo wxPython deve ereditare il formato del framework c++ sottostante, e quindi utilizza la classe ``wx.DateTime``, che però è più scomoda da usare, e soprattutto incompatibile con qualsiasi cosa al di fuori di wxPython. 

Niente paura, basta usare queste pratiche funzioni di conversione tra i due formati (la cosa migliore sarebbe tenerle in un qualche "utils.py" da dove importarle alla bisogna)::

    import wx, datetime

    def pydate2wxdate(pydate):
        'Accetta una datetime.datetime e restutuisce una wx.DateTime'
        tt = pydate.timetuple()
        dmy = (tt[2], tt[1]-1, tt[0])
        return wx.DateTimeFromDMY(*dmy)

    def wxdate2pydate(wxdate):
        'Accetta una wx.DateTime e restutuisce una datetime.datetime'
        ymd = map(int, wxdate.FormatISODate().split('-'))
        return datetime.datetime(*ymd) 

In realtà, col passare del tempo queste funzioni di conversione diventano sempre meno utili, perché i diversi widget di wxPython si sono arricchiti nel frattempo di metodi "pythonici" che accettano e restituiscono oggetti ``datetime``. 
Per esempio, ``CalendarCtrl`` accanto ai vecchi metodi ``GetDate`` e ``SetDate`` ha anche le versioni ``PyGetDate`` e ``PySetDate``, e così molti altri widget. 
Prima di utilizzare questa ricetta, controllate quindi sempre che il vostro widget non sia già pronto a fare il lavoro sporco dietro le quinte. 

