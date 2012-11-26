# una widget per selezionare periodi fissi 
# (mesi, bimestri, trimestri, quadrimestri, semestri)
# c - Riccardo Polignieri 2012
#
import datetime
import wx
import wx.lib.newevent

PeriodEvent, EVT_PERIOD_MODIFIED = wx.lib.newevent.NewCommandEvent()
            
class PeriodWidget(wx.Panel):
    """Un widget per selezionare periodi fissi. Chiamarlo con l'argomento 
       aggiuntivo "period" imposastato a 1 (per selezionare mesi) oppure
       2 (bimestri), 3 (trimestri), 4 (quadrimestri), o 6 (semestri)."""
    months = 'January February March April May June July August September October November December'.split()
    spans = ',, bimester, trimester, quadrimester,, semester'.split(',')
    def __init__(self, *a, **k):
        self.period = k.pop('period')
        wx.Panel.__init__(self, *a, **k)
        if self.period == 1:
            ch = self.months
        else:
            ch = [str(i)+self.spans[self.period] for i in range(1, (12/self.period)+1)]
        self.choose_period = wx.ComboBox(self, -1, choices=ch, 
                                         style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.choose_period.SetSelection(0)
        self.choose_year = wx.SpinCtrl(self, initial=datetime.datetime.now().year, 
                                       min=1800, max=2200, size=((80, -1)))
        s = wx.BoxSizer()
        s.Add(self.choose_period, 1, wx.EXPAND|wx.RIGHT, 5)
        s.Add(self.choose_year, 0, wx.FIXED_MINSIZE|wx.LEFT, 5)
        self.SetSizer(s)
        self.choose_period.Bind(wx.EVT_COMBOBOX, self.on_changed)
        self.choose_year.Bind(wx.EVT_SPINCTRL, self.on_changed)
    
    def on_changed(self, evt):
        my_event = PeriodEvent(self.GetId())
        my_event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(my_event)
        
    def GetValue(self):
        start = datetime.date(
                            self.choose_year.GetValue(), 
                            ((self.period * self.choose_period.GetSelection()) + 1),
                            1)
        end = ((start + 
               datetime.timedelta(days=(30*self.period)+15)).replace(day=1) - 
               datetime.timedelta(days=1))
        return start, end


class TestFrame(wx.Frame): 
    def __init__(self, *a, **k): 
        wx.Frame.__init__(self, *a, **k) 
        period = PeriodWidget(self, period=1)
        period.Bind(EVT_PERIOD_MODIFIED, self.on_period)
        
    def on_period(self, evt):
        print evt.GetEventObject().GetValue()


app = wx.App(False)
TestFrame(None).Show()
app.MainLoop()
