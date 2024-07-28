import subprocess
import os
import platform
import wx
import pcbnew

class JLC2KiCadPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "JLC2KiCad Integration"
        self.category = "Library Management"
        self.description = "Import JLCPCB parts into KiCad libraries"

    def Run(self):
        # Create a new dialog window
        dialog = JLC2KiCadDialog(None, title="JLC2KiCad Integration")
        dialog.ShowModal()
        dialog.Destroy()


class JLC2KiCadDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(JLC2KiCadDialog, self).__init__(parent, title=title, size=(500, 400))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        base_path = ''

        # Base directory for KiCad
        self.base_label = wx.StaticText(panel, label="Base Directory (KiCad):")
        self.base_text = wx.TextCtrl(panel)
        self.base_button = wx.Button(panel, label="Browse...")
        self.base_button.Bind(wx.EVT_BUTTON, self.on_browse_base)
        self.base_text.SetValue(base_path)

        # JLC Part Number
        self.part_label = wx.StaticText(panel, label="JLC Part Number:")
        self.part_text = wx.TextCtrl(panel)

        # Symbol Library Path
        self.symbol_label = wx.StaticText(panel, label="Symbol Library Path:")
        self.symbol_text = wx.TextCtrl(panel)
        self.symbol_button = wx.Button(panel, label="Browse...")
        self.symbol_button.Bind(wx.EVT_BUTTON, self.on_browse_symbol)

        # Footprint Library Path
        self.footprint_label = wx.StaticText(panel, label="Footprint Library Path:")
        self.footprint_text = wx.TextCtrl(panel)
        self.footprint_button = wx.Button(panel, label="Browse...")
        self.footprint_button.Bind(wx.EVT_BUTTON, self.on_browse_footprint)

        # Run Button
        self.run_button = wx.Button(panel, label="Run")
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run)

        # Layout
        vbox.Add(self.base_label, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(self.base_text, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(self.base_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add(self.part_label, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(self.part_text, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        hbox_symbol = wx.BoxSizer(wx.HORIZONTAL)
        hbox_symbol.Add(self.symbol_text, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=10)
        hbox_symbol.Add(self.symbol_button, flag=wx.EXPAND)
        vbox.Add(self.symbol_label, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox_symbol, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        hbox_footprint = wx.BoxSizer(wx.HORIZONTAL)
        hbox_footprint.Add(self.footprint_text, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=10)
        hbox_footprint.Add(self.footprint_button, flag=wx.EXPAND)
        vbox.Add(self.footprint_label, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox_footprint, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add(self.run_button, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

    def on_browse_base(self, event):
        with wx.DirDialog(self, "Choose base directory for KiCad") as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            path = dirDialog.GetPath()
            self.base_text.SetValue(path)

    def on_browse_symbol(self, event):
        base_path = self.base_text.GetValue()
        with wx.FileDialog(self, "Choose symbol library file", wildcard="KiCad Symbol files (*.kicad_sym)|*.kicad_sym", defaultDir=base_path, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            path = fileDialog.GetPath()
            relative_path = os.path.relpath(path, base_path)
            symbol_path = os.path.splitext(relative_path)[0].replace(os.path.sep, "\\")
            self.symbol_text.SetValue(symbol_path)

    def on_browse_footprint(self, event):
        base_path = self.base_text.GetValue()
        with wx.DirDialog(self, "Choose footprint library directory", defaultPath=base_path) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            path = dirDialog.GetPath()
            if not path.endswith(".pretty"):
                wx.MessageBox("The selected directory must end with .pretty", "Error", wx.OK | wx.ICON_ERROR)
                return
            footprint_path = os.path.relpath(path, base_path)
            self.footprint_text.SetValue(footprint_path)

    def on_run(self, event):
        base_path = self.base_text.GetValue()
        part = self.part_text.GetValue()
        symbol_path = self.symbol_text.GetValue()
        symbol_lib = symbol_path.split("\\")[-1]
        symbol_path = "\\".join(symbol_path.split("\\")[:-1])
        footprint_path = self.footprint_text.GetValue()

        command = f"JLC2KiCadLib {part} -dir {base_path} -symbol_lib {symbol_lib} -symbol_lib_dir {symbol_path} -footprint_lib {footprint_path} " \
                  f"-model_dir 3dmodels"

        try:
            activate_cmd = f"conda activate KiCad && {command}"
            subprocess.run(["cmd.exe", "/k", activate_cmd], stdin=subprocess.PIPE)
            wx.MessageBox('JLC Part Imported Successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)
        except subprocess.CalledProcessError as e:
            wx.MessageBox(f'Error: {e}', 'Error', wx.OK | wx.ICON_ERROR)


JLC2KiCadPlugin().register()
