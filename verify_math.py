import math

class GeometryEngine:
    @staticmethod
    def calculate_inductance(shape, n, avg_diameter_um, fill_ratio):
        u0 = 4 * math.pi * 1e-7 
        coeffs = {
            'Square': (2.34, 2.75),
            'Octagonal': (2.25, 3.55),
            'Circular': (2.25, 3.55)
        }
        k1, k2 = coeffs.get(shape, (2.25, 3.55))
        d_avg_m = avg_diameter_um * 1e-6
        if d_avg_m <= 0: return 0
        num = k1 * u0 * (n ** 2) * d_avg_m
        den = 1 + k2 * fill_ratio
        l_henry = num / den
        return l_henry * 1e9

    @staticmethod
    def generate_points(shape, center_x, center_y, turns, width, spacing, radius):
        points = []
        pitch = width + spacing
        
        # Simple simulation of point generation logic
        segments_per_turn = 64 if shape == 'Circular' else (4 if shape == 'Square' else 8)
        total_steps = int(turns * segments_per_turn)
        
        if shape == 'Circular':
             b = pitch / (2 * math.pi)
             step_angle = (2 * math.pi) / segments_per_turn
             for i in range(total_steps + 1):
                theta = i * step_angle
                r = radius + b * theta
                x = center_x + r * math.cos(theta)
                y = center_y + r * math.sin(theta)
                points.append((x, y))
        
        elif shape in ['Square', 'Octagonal']:
            sides = 4 if shape == 'Square' else 8
            angle_per_step = (2 * math.pi) / sides
            dr = pitch / sides
            start_angle = -math.pi / sides if shape == 'Octagonal' else -math.pi/4
            current_r = radius
            for i in range(total_steps + 1):
                theta = start_angle + i * angle_per_step
                x = center_x + current_r * math.cos(theta)
                y = center_y + current_r * math.sin(theta)
                points.append((x, y))
                current_r += dr
        return points

def test_spiral_growth():
    center_x, center_y = 0, 0
    turns = 3
    width = 0.5
    spacing = 0.5
    radius = 5.0
    
    shapes = ['Circular', 'Square', 'Octagonal']
    
    for shape in shapes:
        print(f"Testing {shape}...")
        points = GeometryEngine.generate_points(shape, center_x, center_y, turns, width, spacing, radius)
        print(f"  Generated {len(points)} points.")
        
        prev_dist = 0
        for i, (x, y) in enumerate(points):
            dist = math.sqrt(x**2 + y**2)
            if i > 0:
                # For polygons, distance might not be strictly monotonic at every microscopic point if we interpolated,
                # but vertices should be increasing or equal (e.g., corners vs edges).
                # Actually, our simplified logic just generates vertices which strictly increase in radius.
                assert dist >= prev_dist, f"  {shape} radius check failed at step {i}"
            prev_dist = dist
        
        # Test Inductance
        d_out = radius*2 + 2 * (turns * (width + spacing))
        d_avg = ((radius*2) + d_out) / 2
        fill = (d_out - radius*2) / (d_out + radius*2)
        
        l = GeometryEngine.calculate_inductance(shape, turns, d_avg * 1000, fill)
        print(f"  Estimated Inductance: {l:.2f} nH")
        assert l > 0, f"  Inductance should be positive"

    print("SUCCESS: All shapes generated and inductance calculated.")
    return True

if __name__ == "__main__":
    test_spiral_growth()
