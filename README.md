# SpiralGen Pro: Advanced Planar Inductor Generator for KiCad

[![KiCad Version](https://img.shields.io/badge/KiCad-9.0%2B-blue.svg)](https://kicad.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)]()

**SpiralGen Pro** is a professional-grade EDA (Electronic Design Automation) plugin developed for **KiCad 9**. It bridges the gap between **Computer Science** (Geometric Algorithms) and **RF Electronics** (Inductance Physics) to automate the design of planar spiral inductors.

Unlike standard drawing tools, SpiralGen Pro is **physics-aware**: it calculates the electrical inductance of your component in real-time as you design it.

---

## ⚡ Key Features

### 1. Multi-Geometry Engine
Generate complex spiral geometries with mathematical precision:
- **Circular Spirals**: Smooth Archimedean spirals for standard RF applications.
- **Square Spirals**: High-density layouts for compact PCBs.
- **Octagonal Spirals**: The perfect balance between Q-factor and area efficiency.

### 2. Real-Time Physics Feedback
Don't just draw blindly. **SpiralGen Pro** integrates the **Mohan’s Data Dependent Expressions**, providing instant feedback on the electrical properties of your design:
- **Live Inductance Calculation (nH)**
- Updates dynamically as you adjust Turns, Width, or Spacing.

### 3. Practical Design Automation
Built for real-world manufacturing:
- **Automated Via Stitching**: Option to automatically place a center thermal/ground via.
- **DRC-Compliant Tracks**: Generates native KiCad `PCB_TRACK` objects that respect board constraints.

---

## 🚀 Installation

1.  **Download** this repository.
2.  **Locate** your KiCad plugins directory:
    - **Windows**: `%USERPROFILE%\Documents\KiCad\9.0\scripting\plugins`
    - **macOS**: `~/Documents/KiCad/9.0/scripting/plugins`
    - **Linux**: `~/.local/share/kicad/9.0/scripting/plugins`
3.  **Copy** the `SpiralGen` folder into the `plugins` directory.
4.  **Restart** KiCad PCB Editor.

---

## 📖 Usage Guide

1.  Open **KiCad PCB New**.
2.  Click the **SpiralGen Pro** icon on the top toolbar (or access via `Tools > External Plugins`).
3.  **Configure Parameters**:
    | Parameter | Description |
    | :--- | :--- |
    | **Shape** | Select Circular, Square, or Octagonal geometry. |
    | **Turns** | Number of full rotations (e.g., 4.5). |
    | **Track Width** | Width of the copper trace in mm. |
    | **Spacing** | Air gap between adjacent traces in mm. |
    | **Inner Radius** | Distance from center to the start of the spiral. |
4.  **Observe**: Watch the *Estimated Inductance* update in real-time.
5.  Click **OK** to generate the footprint at the center of your viewport.

---

## 🧠 Technical Implementation

### Algorithms
The plugin utilizes a custom `GeometryEngine` class that implements:
- **Archimedean Spiral Equation**: $r = a + b\theta$ for circular generation.
- **Piecewise Linear Approximations**: For polygon spirals (Square/Octagon), generating vertices that expand radially by $\frac{\text{pitch}}{\text{sides}}$ per step.

### System Architecture
```mermaid
classDiagram
    class SpiralDialog {
        +GetValues()
        +OnParamChange()
    }
    class GeometryEngine {
        +GeneratePoints()
        +CalculateInductance()
    }
    class KiCadInterface {
        +DrawTracks()
        +PlaceVia()
    }
    
    SpiralDialog --> GeometryEngine : Requests Data
    SpiralDialog --> KiCadInterface : Triggers Draw
    KiCadInterface --> GeometryEngine : Consumes Points
```

### Physics Model
Inductance is estimated using the **Current Sheet Approximation**:

$$ L = \frac{K_1 \cdot \mu_0 \cdot n^2 \cdot d_{avg}}{1 + K_2 \cdot \rho} $$

Where:
- $L$: Inductance in Henrys
- $d_{avg}$: Average Diameter
- $\rho$: Fill Ratio
- $K_1, K_2$: Shape-dependent coefficients (e.g., Square: $K_1=2.34, K_2=2.75$)

For a complete architectural overview, please refer to the **[Design Document](design_document.md)**.

---

## 👨‍💻 Developer Info

This plugin was developed as part of the **eSim Semester Long Internship Spring 2026 (Task 6)**. It demonstrates the powerful synergy between Python scripting and Electronic Design Automation.

**License**: MIT License
