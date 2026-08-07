# TD.4. Thematic Spatial Mapping Framework

## 1. Concept-to-Parameter Mapping

The ZYNTH AI agent should use this table to translate abstract client themes into specific 3D design parameters.

| Theme | Primary Materials | Lighting Palette | Geometry Style |
| :--- | :--- | :--- | :--- |
| **Tech/Innovation** | Brushed Aluminum, Glass, Neon Acrylic | Cool White (6000K), Electric Blue, Cyan | Sharp angles, hex patterns, clean lines. |
| **Luxury/Premium** | Gold/Brass, Dark Marble, Velvet | Warm White (2700K), Amber, Deep Gold | Curves, thick profiles, ornate textures. |
| **Eco/Sustainable** | Light Wood (Oak), Recycled Paper, Moss | Natural Daylight (5000K), Soft Green | Organic shapes, modular units, open space. |
| **Cyberpunk/Urban** | Gritty Concrete, Rusted Metal, Plastic | High Contrast, Pink/Purple Neon, Glitch effects | Asymmetrical, layered, dense details. |
| **Minimalist** | Matte White, Light Grey, Frosted Glass | Diffused Wash, Minimal Shadows | Hidden seams, negative space, thin lines. |

## 2. Lighting Temperature & Emotion

- **2000K - 3000K (Warm)**: Intimate, welcoming, luxury, evening events.
- **4000K - 5000K (Neutral)**: Professional, clean, daytime, retail.
- **6000K+ (Cool)**: High-tech, clinical, futuristic, energetic.

## 3. Material Fidelity (PBR Values)

| Material | Metallic | Roughness | Specular |
| :--- | :--- | :--- | :--- |
| **Polished Steel** | 1.0 | 0.1 | 0.5 |
| **Frosted Glass** | 0.0 | 0.2 (with Transmission) | 0.5 |
| **Matte Plastic** | 0.0 | 0.8 | 0.5 |
| **Wood** | 0.0 | 0.6 | 0.2 |

## 4. SOP: Thematic Design Execution
1.  **Identify Keyword**: Extract the primary theme from the user's brief (e.g., "Futuristic").
2.  **Select Palette**: Load the corresponding materials and lighting from the mapping table.
3.  **Apply to Scene**:
    *   Set the World Background color or HDRI to match the palette.
    *   Apply PBR values to the structural components (walls, truss).
    *   Set light temperatures (K) based on the desired emotion.
4.  **Visual Polish**: Add accent lights (strips/emissive nodes) in the theme's secondary colors.
