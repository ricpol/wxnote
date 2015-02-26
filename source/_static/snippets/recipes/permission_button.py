# un wx.Button modificato per chiedere 
# se si e' autorizzati a procedere
# c - Riccardo Polignieri 2015
#

import wx

# una funzione dummy per verificare la password
def check_psw(psw):
    if psw == 'secret': 
        return True
    return False


class CheckPermissionButton(wx.Button):
    """Un wx.Button che chiede la password all'utente 
       prima di procedere."""
    def __init__(self, *a, **k):
        wx.Button.__init__(self, *a, **k)
        self.Bind(wx.EVT_LEFT_UP, self.on_leftup)

    def on_leftup(self, evt):
        msg = 'Inserire la password per procedere:'
        cpt = 'Password richiesta.'
        if check_psw(wx.GetPasswordFromUser(msg, cpt)):
            wx.PostEvent(
                self.GetEventHandler(), 
                wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.GetId()))
        else:
            wx.MessageBox('Password errata!', 'Password errata', 
                          wx.ICON_ERROR|wx.OK)


class TestFrame(wx.Frame): 
    def __init__(self, *a, **k): 
        wx.Frame.__init__(self, *a, **k) 
        p = wx.Panel(self)
        b = CheckPermissionButton(p, -1, 'clic me', pos=((50, 50)))
        b.Bind(wx.EVT_BUTTON, self.onclic)

    def onclic(self, evt):
        wx.MessageBox(
            "Password corretta, procedo con l'azione prevista.")
        # e qui il codice previsto del callback, come di consueto


app = wx.App(False)
TestFrame(None).Show()
app.MainLoop()
