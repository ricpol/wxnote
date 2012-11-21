# una ricetta per catturare tutti gli eventi emessi da un widget
# c - Riccardo Polignieri 2012
#
#
import wx

class TopFrame(wx.Dialog):
    def __init__(self, *a, **k):
        wx.Dialog.__init__(self, *a, **k)
        b1 = wx.Button(self, -1, 'riempitivo')
        
        # qui mettete il widget che volete testare, al posto del wx.Button
        test_widget = wx.Button(self)
        
        b2 = wx.TextCtrl(self, -1, 'altro riempitivo')
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(b1, 0, wx.EXPAND|wx.ALL, 5)
        s.Add(test_widget, 1, wx.EXPAND|wx.ALL, 5)
        s.Add(b2, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(s)

        binder_names = [i for i in dir(wx) if i.startswith('EVT_')]
        # questi due non si possono collegare con Bind:
        binder_names.remove('EVT_COMMAND')
        binder_names.remove('EVT_COMMAND_RANGE')
        
        # qui rimuovete gli eventi che non volete registrare:
        # per es. questi si ripetono di continuo e producono rumore di fondo
        for b in ('EVT_IDLE', 'EVT_UPDATE_UI', 'EVT_UPDATE_UI_RANGE', 
                  'EVT_MOTION', 'EVT_SET_CURSOR'):
            binder_names.remove(b)
            
        self.binder_dict = {}
        
        for binder_name in binder_names:
            obj_binder = eval('wx.'+binder_name)
            if len(obj_binder.evtType) == 1:
                test_widget.Bind(obj_binder, self.callback)
                binder_type = obj_binder.evtType[0]
                self.binder_dict[binder_type] = binder_name
        
        self.last_printed_event = ''

    def callback(self, evt): 
        evt.Skip()
        evt_type = self.binder_dict[evt.GetEventType()]
        if evt_type != self.last_printed_event:
            print '\n'+evt_type, 
            self.last_printed_event = evt_type
        else:
            print '.',


app = wx.App(False)
TopFrame(None).Show()
app.MainLoop()

