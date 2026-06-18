import json
import os
from manim import *

class SVM3DVisualization(ThreeDScene):
    def construct(self):
        # 1. Load data generated from Phase 1
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "svm_data.json")
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(
                f"Data file '{data_path}' not found! Please run 'svm_data.py' first."
            )
            
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        points_data = data["points"]
        meta = data["meta"]
        
        # 2. Setup 3D Axes
        # X and Y are coordinates from make_circles (in range [-1.2, 1.2])
        # Z is the decision function score (in range [-1.5, 1.5] typically)
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 0.5],
            y_range=[-2.5, 2.5, 0.5],
            z_range=[-2.0, 2.0, 0.5],
            x_length=7,
            y_length=7,
            z_length=4.5,
            axis_config={"color": GREY_B, "stroke_width": 2}
        )
        
        # Scale coordinates for visualization
        # We multiply X and Y by a scaling factor to spread them nicely on the axes.
        # Since our axes length is 7 units for [-2.5, 2.5], we map them directly.
        # Let's write helper function to convert database coordinates to axes positions
        def map_coords(x, y, z):
            # Map values to axes coordinate system
            # x and y are in [-1.2, 1.2], z is typically in [-1.5, 1.5]
            # Since the axes ranges are configured, c2p handles the correct scaling
            return axes.c2p(x * 1.5, y * 1.5, z * 0.8)

        # 3. Create Title and Info Labels (2D overlays)
        # Using standard Text instead of MathTex/Tex to prevent LaTeX dependencies
        title = Text("SVM RBF Kernel 3D Visualization", font_size=24, color=WHITE)
        title.to_edge(UP)
        
        desc_2d = Text(
            "2D Space: Outer circle (blue) and inner circle (red) are linearly inseparable.",
            font_size=14,
            color=LIGHT_GREY
        )
        desc_2d.next_to(title, DOWN, buff=0.2)
        
        desc_3d = Text(
            "3D Space: Mapping points to Z = SVM Decision Score.\nRed points (Class 0) rise up, blue points (Class 1) fall down.\nClasses are now linearly separable!",
            font_size=14,
            color=LIGHT_GREY
        )
        desc_3d.next_to(title, DOWN, buff=0.2)
        
        # 4. Create Mobjects for data points
        color_class_0 = "#FF4D4D"  # Coral Red (Inner Circle)
        color_class_1 = "#3399FF"  # Dodger Blue (Outer Circle)
        color_sv = "#FFD700"       # Gold (Support Vectors)
        
        dots = VGroup()
        target_positions = []
        sv_elements = []  # Store support vectors for later animation
        
        for pt in points_data:
            x, y, z = pt["x"], pt["y"], pt["z"]
            label = pt["label"]
            is_sv = pt["is_support_vector"]
            
            # Identify class color
            dot_color = color_class_0 if label == meta["inner_class"] else color_class_1
            
            # Start dots at Z = 0 in 2D
            initial_pos = map_coords(x, y, 0)
            
            # Draw standard Dot. To make it stand out in 3D, Dot3D can be used.
            # However, standard Dot is fully compatible and renders very cleanly in ThreeDScene too.
            # We'll use Dot3D for a true 3D spherical look.
            dot = Dot3D(
                point=initial_pos,
                radius=0.07,
                color=dot_color
            )
            dots.add(dot)
            
            # Calculate lifted target position
            final_pos = map_coords(x, y, z)
            target_positions.append(final_pos)
            
            if is_sv:
                sv_elements.append((dot, dot_color, final_pos))

        # 5. Build Animation
        
        # Setup camera to 2D flat mode first (looking straight down)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        
        # Fade in Title, 2D Description, Axes and 2D Dots
        self.add_fixed_in_frame_mobjects(title, desc_2d)
        self.play(
            FadeIn(axes),
            FadeIn(dots),
            run_time=2.5
        )
        self.wait(2.5)
        
        # Step B: Dimension Lifting (Transition to 3D & Elevation)
        self.remove_fixed_in_frame_mobjects(desc_2d)
        self.add_fixed_in_frame_mobjects(desc_3d)
        
        # We rotate camera to a tilted 3D angle: phi=72, theta=-45
        # And simultaneously animate all points moving to their 3D (x, y, z) coordinates.
        self.move_camera(
            phi=72 * DEGREES,
            theta=-45 * DEGREES,
            added_anims=[dot.animate.move_to(pos) for dot, pos in zip(dots, target_positions)],
            run_time=4.5
        )
        self.wait(1.5)
        
        # Step C: Render Decision Hyperplane
        # Create a horizontal plane at Z = 0 (decision boundary in SVM feature space)
        # Using a Polygon to represent the plane spanning the axes bounds
        p1 = map_coords(-2.0, -2.0, 0)
        p2 = map_coords(2.0, -2.0, 0)
        p3 = map_coords(2.0, 2.0, 0)
        p4 = map_coords(-2.0, 2.0, 0)
        
        hyperplane = Polygon(
            p1, p2, p3, p4,
            fill_color=GREY_A,
            fill_opacity=0.35,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        # Enable 3D shading
        hyperplane.set_shade_in_3d(True)
        
        # Hyperplane label
        plane_label = Text("Decision Hyperplane (Z = 0)", font_size=12, color=LIGHT_GREY)
        plane_label.move_to(map_coords(1.6, -1.6, 0.15))
        
        self.play(
            FadeIn(hyperplane),
            Write(plane_label),
            run_time=2.0
        )
        self.wait(2.0)
        
        # Step D: Highlight Support Vectors
        # Animate support vectors to turn gold and scale up
        highlight_anims = []
        for dot, _, _ in sv_elements:
            highlight_anims.append(dot.animate.set_color(color_sv).scale(1.6))
            
        self.play(*highlight_anims, run_time=1.5)
        
        # Indicate Support Vectors with a pulse effect
        self.play(
            *[Indicate(dot, scale_factor=1.3, color=color_sv) for dot, _, _ in sv_elements],
            run_time=2.0
        )
        
        # Display Support Vectors explanation
        sv_explanation = Text(
            "Gold dots represent Support Vectors that lie closest to the decision hyperplane.",
            font_size=13,
            color=color_sv
        )
        sv_explanation.to_edge(DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(sv_explanation)
        self.wait(2.0)
        
        # Step E: Camera Orbiting
        # Ambient camera rotation allows viewing the 3D separating plane from different angles
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(7.0)
        self.stop_ambient_camera_rotation()
        
        # Step F: End Scene & Optional Interactive Camera Interaction (Phase 3)
        # If running in an interactive environment, start mouse control.
        # Otherwise, wrap up the video.
        try:
            self.camera.start_mouse_interaction()
        except AttributeError:
            pass
            
        self.wait(1.5)
        
        # Fade out everything at the end
        self.remove_fixed_in_frame_mobjects(title, desc_3d, sv_explanation)
        self.play(
            FadeOut(dots),
            FadeOut(axes),
            FadeOut(hyperplane),
            FadeOut(plane_label),
            run_time=2.0
        )
        self.wait(1)
