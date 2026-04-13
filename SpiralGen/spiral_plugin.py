import pcbnew
import wx
import math

class GeometryEngine:
    @staticmethod
    def calculate_inductance(shape, n, avg_diameter_um, fill_ratio):
        """
        Calculates inductance using Modified Wheeler / Mohan's Data Dependent Expression.
        L = (K1 * u0 * n^2 * d_avg) / (1 + K2 * rho)
        
        Where:
        u0 = 4 * pi * 10^-7 H/m
        d_avg = average diameter
        rho = fill ratio ((d_out - d_in) / (d_out + d_in))
        
        Coefficients (K1, K2):
        Square: K1=2.34, K2=2.75
        Hexagonal: K1=2.33, K2=3.82 (Not implemented yet)
        Octagonal: K1=2.25, K2=3.55
        Circular: Coeffs vary, but commonly used approximations:
                  L = (u0 * n^2 * d_avg * c1) / (ln(c2/rho) + c3*rho + c4*rho^2)
                  Let's use the Monomial expression for simplicity or similar Mohan form.
                  Mohan Circular: K1=2.25 (approx), K2=3.55 (similar to Octagonal)
                  Actually, let's use the standard output:
                  Square: K1=2.34, K2=2.75
                  Octagonal: K1=2.25, K2=3.55
                  Circular: K1=2.25, K2=3.55 (Close approximation)
        """
        # Vacuum permeability in H/m
        u0 = 4 * math.pi * 1e-7 

        # Coefficients dictionary [K1, K2]
        coeffs = {
            'Square': (2.34, 2.75),
            'Octagonal': (2.25, 3.55),
            'Circular': (2.25, 3.55) # Approximation
        }
        
        k1, k2 = coeffs.get(shape, (2.25, 3.55))
        
        d_avg_m = avg_diameter_um * 1e-6
        if d_avg_m <= 0: return 0
        
        # Formula: L = beta * d_avg * n^2
        # But let's use the Current Sheet Approximation specific one:
        # L = (K1 * u0 * n^2 * d_avg) / (1 + K2 * rho)
        
        num = k1 * u0 * (n ** 2) * d_avg_m
        den = 1 + k2 * fill_ratio
        
        l_henry = num / den
        return l_henry * 1e9 # Return in nH

    @staticmethod
    def generate_points(shape, center_x_nm, center_y_nm, turns, width_mm, spacing_mm, radius_mm):
        points = []
        
        # Parameters
        pitch = width_mm + spacing_mm
        segments_per_turn = 64 if shape == 'Circular' else (4 if shape == 'Square' else 8)
        
        total_steps = int(turns * segments_per_turn)
        
        # Different logic for polygons
        if shape == 'Circular':
             b = pitch / (2 * math.pi)
             step_angle = (2 * math.pi) / segments_per_turn
             for i in range(total_steps + 1):
                theta = i * step_angle
                r = radius_mm + b * theta
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                points.append(pcbnew.VECTOR2I(int(center_x_nm + pcbnew.FromMM(x)), int(center_y_nm + pcbnew.FromMM(y))))
        
        elif shape in ['Square', 'Octagonal']:
            # For polygons, we spiral out by increasing radius at vertices.
            # Effectively, radius increases by pitch/sides per step.
            sides = 4 if shape == 'Square' else 8
            angle_per_step = (2 * math.pi) / sides
            dr = pitch / sides
            
            # Start angle correction to make flat side down or appropriate orientation
            start_angle = -math.pi / sides if shape == 'Octagonal' else -math.pi/4
            
            current_r = radius_mm
            
            for i in range(total_steps + 1):
                theta = start_angle + i * angle_per_step
                
                # Correction for straight lines between vertices:
                # We just generate vertices, PCB_TRACK will make straight lines.
                
                x = current_r * math.cos(theta)
                y = current_r * math.sin(theta)
                points.append(pcbnew.VECTOR2I(int(center_x_nm + pcbnew.FromMM(x)), int(center_y_nm + pcbnew.FromMM(y))))
                
                current_r += dr
                
        return points

class SpiralDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="SpiralGen Pro Inductor Generator")

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.inputs = {}
        
        # Grid
        grid = wx.FlexGridSizer(rows=7, cols=2, vgap=10, hgap=10)
        
        # Shape selection
        grid.Add(wx.StaticText(self, label="Shape:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.combo_shape = wx.ComboBox(self, choices=['Circular', 'Square', 'Octagonal'], style=wx.CB_READONLY)
        self.combo_shape.SetSelection(0)
        grid.Add(self.combo_shape, 1, wx.EXPAND)
        
        # Fields
        def add_field(label, key, default):
            lbl = wx.StaticText(self, label=label)
            txt = wx.TextCtrl(self, value=str(default))
            grid.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(txt, 1, wx.EXPAND)
            self.inputs[key] = txt
            txt.Bind(wx.EVT_TEXT, self.on_change)

        add_field("Number of Turns:", 'turns', "5")
        add_field("Track Width (mm):", 'width', "0.2")
        add_field("Track Spacing (mm):", 'spacing', "0.2")
        add_field("Inner Radius (mm):", 'radius', "1.0")
        
        # Via option
        self.cb_via = wx.CheckBox(self, label="Add Center Via")
        grid.Add(wx.StaticText(self, label="Options:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.cb_via, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 10)

        # Inductance Display
        self.lbl_inductance = wx.StaticText(self, label="Estimated L: --- nH")
        font = self.lbl_inductance.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.lbl_inductance.SetFont(font)
        sizer.Add(self.lbl_inductance, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_cancel = wx.Button(self, wx.ID_CANCEL)
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()

        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        self.combo_shape.Bind(wx.EVT_COMBOBOX, self.on_change)
        self.SetSizer(sizer)
        self.Fit()
        
        # Initial calc
        self.on_change(None)

    def get_values(self):
        try:
            return {
                'shape': self.combo_shape.GetStringSelection(),
                'turns': float(self.inputs['turns'].GetValue()),
                'width': float(self.inputs['width'].GetValue()),
                'spacing': float(self.inputs['spacing'].GetValue()),
                'radius': float(self.inputs['radius'].GetValue()),
                'via': self.cb_via.IsChecked()
            }
        except ValueError:
            return None

    def on_change(self, event):
        vals = self.get_values()
        if vals:
            # Calculate physical params for inductance
            d_in = vals['radius'] * 2
            # Approximation of outer diameter:
            # d_out = d_in + 2 * (turns * (width + spacing))
            d_out = d_in + 2 * (vals['turns'] * (vals['width'] + vals['spacing']))
            d_avg = (d_out + d_in) / 2
            
            fill_ratio = 0
            if (d_out + d_in) > 0:
                fill_ratio = (d_out - d_in) / (d_out + d_in)
                
            l = GeometryEngine.calculate_inductance(
                vals['shape'], vals['turns'], d_avg * 1000, fill_ratio
            )
            self.lbl_inductance.SetLabel(f"Estimated L: {l:.2f} nH")

class SpiralGeneratorPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "SpiralGen Pro"
        self.category = "RF"
        self.description = "Generates planar spiral inductors (Square/Oct/Circ) with inductance calc."
        self.show_toolbar_button = True
        self.icon_file_name = "icon.png"

    def Run(self):
        parent = wx.GetApp().GetTopWindow()
        dlg = SpiralDialog(parent)

        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.get_values()
            if values:
                self.generate_spiral(values)
        
        dlg.Destroy()

    def generate_spiral(self, p):
        board = pcbnew.GetBoard()
        
        width_nm = pcbnew.FromMM(p['width'])
        center_x = pcbnew.FromMM(100)
        center_y = pcbnew.FromMM(100)
        
        points = GeometryEngine.generate_points(
            p['shape'], center_x, center_y, 
            p['turns'], p['width'], p['spacing'], p['radius']
        )
            
        # Draw tracks
        track_layer = pcbnew.F_Cu
        for i in range(len(points) - 1):
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(points[i])
            track.SetEnd(points[i+1])
            track.SetWidth(width_nm)
            track.SetLayer(track_layer)
            board.Add(track)
            
        # Add Via if requested
        if p['via']:
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(center_x, center_y))
            # Defaults for via size - can be improved later
            via.SetWidth(pcbnew.FromMM(0.6))
            via.SetDrill(pcbnew.FromMM(0.3))
            board.Add(via)
            
        pcbnew.Refresh()

