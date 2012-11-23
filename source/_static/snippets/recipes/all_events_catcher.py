# una ricetta per catturare tutti gli eventi emessi da un widget
# c - Riccardo Polignieri 2012
#
#
import wx

class TopFrame(wx.Frame):
    def __init__(self, *a, **k):
        wx.Frame.__init__(self, *a, **k)
        p = wx.Panel(self)
        # qui mettete il widget che volete testare, al posto del wx.Button
        test_widget = wx.Button(p, -1, 'test me!')
        
        self.output = wx.TextCtrl(p, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(test_widget, 1, wx.EXPAND|wx.ALL, 5)
        s.Add(self.output, 1, wx.EXPAND|wx.ALL, 5)
        p.SetSizer(s)

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
            obj_binder = getattr(wx, binder_name)
            if len(obj_binder.evtType) == 1:
                test_widget.Bind(obj_binder, self.callback)
                binder_type = obj_binder.evtType[0]
                self.binder_dict[binder_type] = binder_name
        
        self.last_printed_event = ''

    def callback(self, evt): 
        evt.Skip()
        evt_type = self.binder_dict[evt.GetEventType()]
        if evt_type != self.last_printed_event:
            txt =  '\n%s %s' % (evt.__class__.__name__, evt_type)
            self.last_printed_event = evt_type
        else:
            txt = '-'
        self.output.AppendText(txt)


app = wx.App(False)
TopFrame(None, title='Event Test').Show()
app.MainLoop()

