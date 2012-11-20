# validatori: un dialogo con validazione automatica
#
import wx

class NotEmptyValidator(wx.PyValidator):
    def Clone(self): return NotEmptyValidator()
    def TransferToWindow(self): return True
    def TransferFromWindow(self): return True
    
    def Validate(self, ctl):
        win = self.GetWindow()
        val = win.GetValue().strip()
        if val == '':
            msg = '%s: manca del testo!' % win.GetName()
            wx.MessageBox(msg)
            return False
        else:
            return True

class NotInBadListValidator(wx.PyValidator):
    def __init__(self, badlist):
        wx.PyValidator.__init__(self)
        self._badlist=badlist
    
    def Clone(self): return NotInBadListValidator(self._badlist)
    def TransferToWindow(self): return True
    def TransferFromWindow(self): return True
    
    def Validate(self, ctl):
        win = self.GetWindow()
        val = win.GetValue().strip()
        if val in self._badlist:
            msg = '%s: non valido!' % win.GetName()
            wx.MessageBox(msg)
            return False
        else:
            return True
    
class NameDialog(wx.Dialog):
    def __init__(self, *a, **k):
        wx.Dialog.__init__(self, *a, **k)
        ugly_names = ('Cunegonda', 'Dagoberto', 'Emerenzio', 'Pancrazia')
        self.first_name = wx.TextCtrl(self, name='Nome', 
                                      validator=NotInBadListValidator(ugly_names))
        self.family_name = wx.TextCtrl(self, name='Cognome',
                                       validator=NotEmptyValidator())
        validate = wx.Button(self, wx.ID_OK, 'valida')
        cancel = wx.Button(self, wx.ID_CANCEL, 'annulla')
                           
        s = wx.FlexGridSizer(2, 2, 5, 5)
        s.AddGrowableCol(1)
        s.Add(wx.StaticText(self, -1, 'nome:'), 0, wx.ALIGN_CENTER_VERTICAL)
        s.Add(self.first_name, 1, wx.EXPAND)
        s.Add(wx.StaticText(self, -1, 'cognome:'), 0, wx.ALIGN_CENTER_VERTICAL)
        s.Add(self.family_name, 1, wx.EXPAND) 

        s1 = wx.BoxSizer()
        s1.Add(validate, 1, wx.EXPAND|wx.ALL, 5)
        s1.Add(cancel, 1, wx.EXPAND|wx.ALL, 5)
        
        s2 = wx.BoxSizer(wx.VERTICAL)
        s2.Add(s, 1, wx.EXPAND|wx.ALL, 5)
        s2.Add(s1, 0, wx.EXPAND)
        self.SetSizer(s2)
        s2.Fit(self)

class MyTopFrame(wx.Frame):
    def __init__(self, *a, **k):
        wx.Frame.__init__(self, *a, **k)
        b = wx.Button(self, -1, 'mostra dialogo')
        b.Bind(wx.EVT_BUTTON, self.on_clic)
        
    def on_clic(self, evt):
        dlg = NameDialog(self)
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            print 'confermato'
        else:
            print 'annullato'
        dlg.Destroy()
        

app = wx.App(False)
MyTopFrame(None, size=(200, 200)).Show()
app.MainLoop()