import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import textwrap

def create_sipoc_diagram(output_path):
    # Set figure size and DPI for high-resolution crisp export
    fig_w, fig_h = 24, 13.5
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300, facecolor='#0B132B')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0B132B')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette - Modern Glassmorphism & High-Contrast Tech
    colors = {
        'S': {'header': '#1C2541', 'border': '#3A86FF', 'badge': '#3A86FF', 'card': '#141E36', 'text_title': '#60A5FA'},
        'I': {'header': '#112F41', 'border': '#00F5D4', 'badge': '#00F5D4', 'card': '#0E2736', 'text_title': '#2DD4BF'},
        'P': {'header': '#2A1B4E', 'border': '#9D4EDD', 'badge': '#9D4EDD', 'card': '#20153D', 'text_title': '#C084FC'},
        'O': {'header': '#3D2214', 'border': '#FF9E00', 'badge': '#FF9E00', 'card': '#301B10', 'text_title': '#FBBF24'},
        'C': {'header': '#133326', 'border': '#10B981', 'badge': '#10B981', 'card': '#0E291E', 'text_title': '#34D399'}
    }

    # Header section
    ax.text(50, 96.5, "DIAGRAMA SIPOC — SISTEMA DE ATENCIÓN PREHOSPITALARIA (APH)", 
            fontsize=24, fontweight='bold', color='#FFFFFF', ha='center', va='center', fontfamily='sans-serif')
    
    subtext = "Optimización de Localización-Asignación y Reubicación de Ambulancias para Urgencias Viales en Montería, Córdoba (2026)"
    ax.text(50, 93.8, subtext, fontsize=13, color='#94A3B8', ha='center', va='center', fontfamily='sans-serif')

    # Columns configuration
    columns = [
        {
            'key': 'S',
            'letter': 'S',
            'title': 'PROVEEDORES',
            'eng': 'Suppliers',
            'items': [
                ("Ciudadanía y Reportantes", "Testigos y usuarios que llaman al 123 reportando siniestros en vías."),
                ("Equipo Gemba Walk", "Levantamiento empírico de 338 incidentes viales georreferenciados (2021-2026)."),
                ("OpenStreetMap (OSMnx)", "Cartografía vial urbana y distancias de la red de transporte de Montería."),
                ("Operadores de Flota APH", "Empresas públicas/privadas que aportan disponibilidad de ambulancias y bases."),
                ("Literatura & Plataformas IA", "Modelos matemáticos (Scopus), Solvers (PuLP/SciPy), SimPy y Gemini API.")
            ]
        },
        {
            'key': 'I',
            'letter': 'I',
            'title': 'ENTRADAS',
            'eng': 'Inputs',
            'items': [
                ("Dataset 338 Siniestros", "Coordenadas lat/lon, fechas, horas y nivel de severidad (víctimas/graves)."),
                ("Matriz de Tiempos T_ij", "Tiempos origen-destino ajustados por congestión horaria (1.0 valle, 1.6 pico)."),
                ("Parámetros del Sistema", "Demanda (d_i), tiempo meta T_max (10 min), flota (p) y capacidad de bases (C_j)."),
                ("Modelo Poisson No Homogéneo", "Distribución estocástica de frecuencia y tasa de ocurrencia de siniestros."),
                ("Nodos Candidatos (J)", "Puntos geográficos preseleccionados para posicionamiento estratégico.")
            ]
        },
        {
            'key': 'P',
            'letter': 'P',
            'title': 'PROCESO',
            'eng': 'Process',
            'items': [
                ("P1. Caracterización Espacial", "Clusterización de puntos calientes (Mocarí, Circunvalar, Centro, Mogambo)."),
                ("P2. Formulación MILP", "Planteamiento matemático: Max cobertura de demanda y penalización por exceso."),
                ("P3. Optimización de Bases", "Resolución científica del solver para asignación óptima inicial de ambulancias."),
                ("P4. Simulación Dinámica SimPy", "Emulación estocástica de eventos discretos, colas de atención y reubicación."),
                ("P5. Gemelo Digital y Despacho", "Generación de recomendaciones operativas y monitoreo asistido por IA.")
            ]
        },
        {
            'key': 'O',
            'letter': 'O',
            'title': 'SALIDAS',
            'eng': 'Outputs',
            'items': [
                ("Plan Óptimo de Asignación", "Ubicación estratégica y política preventiva superando el modelo 'closest-idle'."),
                ("Tiempo T_resp <= 10 min", "Reducción mínima proyectada del 25% frente al esquema reactivo tradicional."),
                ("Métricas Operativas (KPIs)", "Tasa de cobertura efectiva, utilización de flota (rho_k) y tiempos de cola."),
                ("Dashboard Gemelo Digital", "Entorno web interactivo en Streamlit/Gradio con mapas de calor en vivo."),
                ("Reportes y Consultas LLM", "Recomendaciones explicables generadas por Gemini API para el operador.")
            ]
        },
        {
            'key': 'C',
            'letter': 'C',
            'title': 'CLIENTES',
            'eng': 'Customers',
            'items': [
                ("Operadores CRUE / Línea 123", "Despachadores que toman decisiones tácticas y operativas de asignación."),
                ("Tripulaciones Paramédicas", "Conductores y personal APH con rutas más rápidas y bases estratégicas."),
                ("Víctimas de Siniestros Viales", "Ciudadanos atendidos oportunamente dentro de la ventana de la 'Hora Dorada'."),
                ("Secretarías de Salud y Tránsito", "Autoridades gubernamentales para planificación urbana y prevención vial."),
                ("Comunidad Científica (IO)", "Investigadores en logística de emergencias en ciudades intermedias de LATAM.")
            ]
        }
    ]

    col_w = 17.6
    col_gap = 1.9
    start_x = 2.0
    top_y = 89.0
    box_h = 75.0

    for idx, col in enumerate(columns):
        x = start_x + idx * (col_w + col_gap)
        c_theme = colors[col['key']]

        # Main Column Container Card with subtle shadow
        shadow = patches.FancyBboxPatch(
            (x + 0.3, top_y - box_h - 0.3), col_w, box_h,
            boxstyle="round,pad=0.3,rounding_size=0.8",
            facecolor='#050B1A', edgecolor='none', alpha=0.5, zorder=1
        )
        ax.add_patch(shadow)

        container = patches.FancyBboxPatch(
            (x, top_y - box_h), col_w, box_h,
            boxstyle="round,pad=0.3,rounding_size=0.8",
            facecolor=c_theme['card'], edgecolor=c_theme['border'],
            linewidth=1.8, alpha=0.92, zorder=2
        )
        ax.add_patch(container)

        # Header Box
        header_h = 7.2
        header_box = patches.FancyBboxPatch(
            (x, top_y - header_h), col_w, header_h,
            boxstyle="round,pad=0.2,rounding_size=0.7",
            facecolor=c_theme['header'], edgecolor=c_theme['border'],
            linewidth=1.2, zorder=3
        )
        ax.add_patch(header_box)

        # Letter Badge Circle
        badge_circle = patches.Circle(
            (x + 2.2, top_y - header_h/2), 2.2,
            facecolor=c_theme['badge'], edgecolor='#FFFFFF', linewidth=1.5, zorder=4
        )
        ax.add_patch(badge_circle)
        ax.text(x + 2.2, top_y - header_h/2, col['letter'],
                fontsize=16, fontweight='heavy', color='#FFFFFF' if col['letter'] != 'I' else '#0F172A',
                ha='center', va='center', zorder=5, fontfamily='sans-serif')

        # Header Titles
        ax.text(x + 5.2, top_y - 2.5, col['title'],
                fontsize=13.5, fontweight='bold', color='#FFFFFF', ha='left', va='center', zorder=4, fontfamily='sans-serif')
        ax.text(x + 5.2, top_y - 4.9, col['eng'].upper(),
                fontsize=9.5, fontweight='semibold', color=c_theme['text_title'], ha='left', va='center', zorder=4, fontfamily='sans-serif')

        # Render Items (Cards inside the column)
        card_y = top_y - header_h - 2.2
        card_h = 12.0
        card_gap = 1.3

        for item_idx, (item_title, item_desc) in enumerate(col['items']):
            iy = card_y - (item_idx * (card_h + card_gap))

            item_box = patches.FancyBboxPatch(
                (x + 0.6, iy - card_h), col_w - 1.2, card_h,
                boxstyle="round,pad=0.2,rounding_size=0.5",
                facecolor='#0B1326', edgecolor=c_theme['border'],
                linewidth=0.8, alpha=0.85, zorder=3
            )
            ax.add_patch(item_box)

            # Bullet indicator / step tag
            ax.plot([x + 1.2, x + 1.2], [iy - 1.8, iy - card_h + 1.8], color=c_theme['badge'], linewidth=2.5, zorder=4)

            # Title
            ax.text(x + 2.0, iy - 2.4, item_title,
                    fontsize=10.2, fontweight='bold', color=c_theme['text_title'],
                    ha='left', va='center', zorder=4, fontfamily='sans-serif')

            # Description wrapped
            wrapped_text = "\n".join(textwrap.wrap(item_desc, width=28))
            ax.text(x + 2.0, iy - 7.0, wrapped_text,
                    fontsize=8.4, color='#E2E8F0',
                    ha='left', va='center', zorder=4, fontfamily='sans-serif', linespacing=1.25)

        # Connecting Chevron / Arrow to next column (between columns)
        if idx < len(columns) - 1:
            arrow_x = x + col_w + (col_gap / 2)
            arrow_y = top_y - (box_h / 2)
            ax.annotate('', xy=(arrow_x + 0.6, arrow_y), xytext=(arrow_x - 0.6, arrow_y),
                        arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.6",
                                        color='#64748B', lw=2.2), zorder=5)

    # Footer Metadata Bar
    foot_box = patches.FancyBboxPatch(
        (2.0, 2.0), 96.0, 8.5,
        boxstyle="round,pad=0.3,rounding_size=0.6",
        facecolor='#141E33', edgecolor='#334155', linewidth=1.2, zorder=2
    )
    ax.add_patch(foot_box)

    kpi1_title = "ESTÁNDAR META (HORA DORADA)"
    kpi1_val = "Tiempo respuesta ≤ 10 min | Reducción ≥ 25%"
    kpi2_title = "BASE DE DATOS & VALIDACIÓN"
    kpi2_val = "338 siniestros georreferenciados (Gemba Walk 2021-2026)"
    kpi3_title = "PILAR TECNOLÓGICO Y MATEMÁTICO"
    kpi3_val = "MILP + Procesos Poisson + SimPy + Gemini API"

    ax.text(18.0, 7.0, kpi1_title, fontsize=9.5, fontweight='bold', color='#38BDF8', ha='center', va='center', fontfamily='sans-serif')
    ax.text(18.0, 4.4, kpi1_val, fontsize=9.0, color='#F8FAFC', ha='center', va='center', fontfamily='sans-serif')

    ax.plot([34, 34], [3.2, 9.2], color='#334155', linewidth=1.2, zorder=3)

    ax.text(50.0, 7.0, kpi2_title, fontsize=9.5, fontweight='bold', color='#34D399', ha='center', va='center', fontfamily='sans-serif')
    ax.text(50.0, 4.4, kpi2_val, fontsize=9.0, color='#F8FAFC', ha='center', va='center', fontfamily='sans-serif')

    ax.plot([66, 66], [3.2, 9.2], color='#334155', linewidth=1.2, zorder=3)

    ax.text(82.0, 7.0, kpi3_title, fontsize=9.5, fontweight='bold', color='#FBBF24', ha='center', va='center', fontfamily='sans-serif')
    ax.text(82.0, 4.4, kpi3_val, fontsize=9.0, color='#F8FAFC', ha='center', va='center', fontfamily='sans-serif')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Diagram saved successfully to: {output_path}")

if __name__ == '__main__':
    target = r"c:\Users\pc\OneDrive\Desktop\Proyecto integrador 2\diagrama_sipoc_ambulancias_monteria.png"
    create_sipoc_diagram(target)
