
#   PIA - Modelado y Simulación de Sistemas Dinámicos
#       Equipo #2
#       2043930 - Emmanuel Gerard Espinosa Almaguer
#       2050012 - Jose Miguel Urdiales Carrales
#       
#       
#       
#       

# Problema 5.2: Ruleta con 10 rojos, 10 negros y 2 verdes.
# - Estrategia Simple:    apuesta $1 al rojo siempre.
# - Estrategia Martingala: dobla la apuesta al perder (máx $500),
#                         reinicia a $1 al ganar o superar el límite.
# Regla verde: se re-gira hasta obtener rojo o negro.
# Si sale el color apostado → empate (no gana/pierde).
# Si sale el otro color    → pierde la apuesta.

import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ─── Colores del tema ─────────────────────────────────────────────────────────
BG_DARK  = '#0d1117'
BG_CARD  = '#161b22'
BG_INPUT = '#21262d'
C_RED    = '#e94560'
C_GREEN  = '#3fb950'
C_BLUE   = '#58a6ff'
C_GOLD   = '#d4a017'
TEXT     = '#c9d1d9'
TEXT_DIM = '#8b949e'
WHITE    = '#f0f6fc'

# ─── Lógica de la Ruleta ──────────────────────────────────────────────────────

RUEDA = ['rojo'] * 10 + ['negro'] * 10 + ['verde'] * 2


def girar():
    return random.choice(RUEDA)


def jugar_ronda(color_apostado: str) -> str:
    """
    Simula una ronda completa según las reglas del problema.
    Retorna: 'ganar', 'perder' o 'empate'
    """
    resultado = girar()
    if resultado == 'verde':
        # Re-girar hasta obtener rojo o negro
        while resultado == 'verde':
            resultado = girar()
        return 'empate' if resultado == color_apostado else 'perder'
    return 'ganar' if resultado == color_apostado else 'perder'


# ─── Estrategias ──────────────────────────────────────────────────────────────

def estrategia_simple(balance_inicial: float, rondas: int) -> list:
    
    # Apuesta $1 al rojo en cada ronda.
    
    balance = balance_inicial
    historial = [balance]
    for _ in range(rondas):
        if balance <= 0:
            historial.append(0.0)
            continue
        resultado = jugar_ronda('rojo')
        if resultado == 'ganar':
            balance += 1
        elif resultado == 'perder':
            balance = max(0.0, balance - 1)
        historial.append(balance)
    return historial


def estrategia_martingala(balance_inicial: float, rondas: int, apuesta_max: float = 500.0) -> list:
    
    # Dobla la apuesta al perder hasta apuesta_max.
    # Reinicia a $1 al ganar o al perder la apuesta máxima.
    
    balance = balance_inicial
    historial = [balance]
    apuesta = 1.0
    for _ in range(rondas):
        if balance <= 0:
            historial.append(0.0)
            continue
        monto = min(apuesta, balance, apuesta_max)
        resultado = jugar_ronda('rojo')
        if resultado == 'ganar':
            balance += monto
            apuesta = 1.0
        elif resultado == 'perder':
            balance = max(0.0, balance - monto)
            # Si la apuesta actual alcanzó o superó el límite → reiniciar
            apuesta = 1.0 if apuesta >= apuesta_max else min(apuesta * 2, apuesta_max)
        # empate: balance y apuesta no cambian
        historial.append(balance)
    return historial


def simular_n_veces(estrategia_fn, balance, rondas, n, **kw) -> list:
    return [estrategia_fn(balance, rondas, **kw) for _ in range(n)]


# ─── Interfaz Gráfica ─────────────────────────────────────────────────────────

class AppRuleta(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Simulación de Ruleta — Estrategia Simple vs. Martingala')
        self.geometry('1340x820')
        self.minsize(900, 600)
        self.configure(bg=BG_DARK)
        self._construir_ui()

    # ── Construcción del layout ───────────────────────────────────────────────

    def _construir_ui(self):
        self._cabecera()
        cuerpo = tk.Frame(self, bg=BG_DARK)
        cuerpo.pack(fill='both', expand=True, padx=12, pady=(0, 10))
        self._panel_controles(cuerpo)
        self._panel_graficas(cuerpo)

    def _cabecera(self):
        hdr = tk.Frame(self, bg=BG_CARD, pady=14)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Simulación de Ruleta',
                 font=('Segoe UI', 22, 'bold'), fg=C_RED, bg=BG_CARD).pack()
        tk.Label(hdr,
                 text='Problema 5.2 · Comparación de Estrategias de Apuesta',
                 font=('Segoe UI', 11), fg=TEXT_DIM, bg=BG_CARD).pack()
        tk.Label(hdr,
                 text='Ruleta: 10 rojos · 10 negros · 2 verdes  |  '
                      'Balance inicial: $200',
                 font=('Segoe UI', 9), fg=TEXT_DIM, bg=BG_CARD).pack(pady=(2, 0))

    def _panel_controles(self, padre):
        panel = tk.Frame(padre, bg=BG_CARD, width=270, padx=18, pady=18)
        panel.pack(side='left', fill='y', padx=(0, 12), pady=8)
        panel.pack_propagate(False)

        # ── Parámetros ──
        self._titulo_seccion(panel, 'Parámetros de Simulación')

        self.v_balance  = tk.StringVar(value='200')
        self.v_rondas   = tk.StringVar(value='500')
        self.v_sims     = tk.StringVar(value='30')
        self.v_apmax    = tk.StringVar(value='500')

        campos = [
            ('Balance inicial ($):', self.v_balance),
            ('Número de rondas:', self.v_rondas),
            ('Número de simulaciones:', self.v_sims),
            ('Apuesta máx. Martingala ($):', self.v_apmax),
        ]
        for etiqueta, var in campos:
            self._campo(panel, etiqueta, var)

        tk.Button(
            panel, text='▶   Ejecutar Simulación',
            command=self._ejecutar,
            bg=C_RED, fg=WHITE,
            font=('Segoe UI', 12, 'bold'),
            relief='flat', pady=10, cursor='hand2',
            activebackground='#c0392b', activeforeground=WHITE,
        ).pack(fill='x', pady=(10, 20))

        # ── Resultados ──
        self._titulo_seccion(panel, 'Resultados')

        self.stat_vars = {}
        filas = [
            (None,       'Estrategia Simple'),
            ('sim_avg',  '  Balance promedio final:'),
            ('sim_min',  '  Balance mínimo final:'),
            ('sim_max',  '  Balance máximo final:'),
            ('sim_ruin', '  Simulaciones en ruina:'),
            (None,       'Estrategia Martingala'),
            ('mar_avg',  '  Balance promedio final:'),
            ('mar_min',  '  Balance mínimo final:'),
            ('mar_max',  '  Balance máximo final:'),
            ('mar_ruin', '  Simulaciones en ruina:'),
            (None,       'Veredicto'),
            ('veredicto', None),
        ]
        for key, texto in filas:
            if key is None and texto:
                tk.Label(panel, text=texto,
                         font=('Segoe UI', 10, 'bold'), fg=C_BLUE, bg=BG_CARD
                         ).pack(anchor='w', pady=(8, 0))
            elif key == 'veredicto':
                v = tk.StringVar(value='—')
                self.stat_vars[key] = v
                tk.Label(panel, textvariable=v, wraplength=230,
                         font=('Segoe UI', 9, 'italic'),
                         fg=C_GOLD, bg=BG_CARD, justify='left'
                         ).pack(anchor='w', pady=(4, 0))
            else:
                fila = tk.Frame(panel, bg=BG_CARD)
                fila.pack(fill='x')
                tk.Label(fila, text=texto, font=('Segoe UI', 8),
                         fg=TEXT_DIM, bg=BG_CARD).pack(side='left', anchor='w')
                v = tk.StringVar(value='—')
                self.stat_vars[key] = v
                tk.Label(fila, textvariable=v, font=('Segoe UI', 9, 'bold'),
                         fg=WHITE, bg=BG_CARD).pack(side='right', anchor='e')

        # ── Banner del ganador ──
        tk.Frame(panel, bg=TEXT_DIM, height=1).pack(fill='x', pady=(16, 10))
        tk.Label(panel, text='MEJOR ESTRATEGIA EN ESTA SIMULACIÓN',
                 font=('Segoe UI', 8, 'bold'), fg=TEXT_DIM, bg=BG_CARD).pack()
        self.ganador_var = tk.StringVar(value='—')
        self.ganador_label = tk.Label(panel, textvariable=self.ganador_var,
                                      font=('Segoe UI', 15, 'bold'),
                                      fg=C_GOLD, bg=BG_CARD)
        self.ganador_label.pack(pady=(4, 0))

    def _panel_graficas(self, padre):
        contenedor = tk.Frame(padre, bg=BG_DARK)
        contenedor.pack(side='right', fill='both', expand=True, pady=8)

        self.fig = Figure(figsize=(10, 7), facecolor=BG_DARK)
        gs = self.fig.add_gridspec(2, 2, hspace=0.40, wspace=0.30,
                                   left=0.07, right=0.97,
                                   top=0.93, bottom=0.08)
        self.ax_sim  = self.fig.add_subplot(gs[0, 0])  # historial Simple
        self.ax_mar  = self.fig.add_subplot(gs[0, 1])  # historial Martingala
        self.ax_box  = self.fig.add_subplot(gs[1, 0])  # boxplot comparativo
        self.ax_hist = self.fig.add_subplot(gs[1, 1])  # histograma balances

        for ax in (self.ax_sim, self.ax_mar, self.ax_box, self.ax_hist):
            self._estilo_ax(ax)

        canvas = FigureCanvasTkAgg(self.fig, master=contenedor)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.canvas = canvas

    # ── Helpers de UI ─────────────────────────────────────────────────────────

    def _titulo_seccion(self, padre, texto):
        tk.Label(padre, text=texto, font=('Segoe UI', 12, 'bold'),
                 fg=C_RED, bg=BG_CARD).pack(anchor='w', pady=(0, 4))
        tk.Frame(padre, bg=C_RED, height=1).pack(fill='x', pady=(0, 10))

    def _campo(self, padre, etiqueta, var):
        tk.Label(padre, text=etiqueta, font=('Segoe UI', 9),
                 fg=TEXT, bg=BG_CARD).pack(anchor='w')
        tk.Entry(padre, textvariable=var, font=('Segoe UI', 11),
                 bg=BG_INPUT, fg=WHITE, insertbackground=WHITE,
                 relief='flat', bd=4).pack(fill='x', pady=(2, 9))

    def _estilo_ax(self, ax):
        ax.set_facecolor(BG_CARD)
        for spine in ax.spines.values():
            spine.set_color(TEXT_DIM)
            spine.set_linewidth(0.6)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        ax.xaxis.label.set_color(TEXT_DIM)
        ax.yaxis.label.set_color(TEXT_DIM)
        ax.title.set_color(WHITE)

    # ── Simulación ────────────────────────────────────────────────────────────

    def _ejecutar(self):
        try:
            balance = float(self.v_balance.get())
            rondas  = int(self.v_rondas.get())
            n_sims  = int(self.v_sims.get())
            ap_max  = float(self.v_apmax.get())
            assert balance > 0 and rondas > 0 and n_sims > 0 and ap_max >= 1
        except Exception:
            messagebox.showerror(
                'Entrada inválida',
                'Verifica que todos los valores sean numéricos y positivos.')
            return

        runs_sim = simular_n_veces(estrategia_simple, balance, rondas, n_sims)
        runs_mar = simular_n_veces(
            estrategia_martingala, balance, rondas, n_sims, apuesta_max=ap_max)

        self._dibujar_graficas(runs_sim, runs_mar, balance, rondas)
        self._actualizar_stats(runs_sim, runs_mar, balance)

    # ── Gráficas ──────────────────────────────────────────────────────────────

    def _dibujar_graficas(self, runs_sim, runs_mar, balance_ini, rondas):
        x = np.arange(rondas + 1)

        # — Historial Simple —
        ax = self.ax_sim
        ax.clear(); self._estilo_ax(ax)
        for run in runs_sim:
            ax.plot(x, run, alpha=0.18, color=C_BLUE, linewidth=0.7)
        prom_sim = np.mean(runs_sim, axis=0)
        ax.plot(x, prom_sim, color=C_BLUE, linewidth=2.2, label='Promedio')
        ax.axhline(balance_ini, color=WHITE, linestyle='--',
                   linewidth=1, alpha=0.45, label=f'Inicio ${balance_ini:.0f}')
        ax.axhline(0, color=C_RED, linewidth=1, alpha=0.6)
        ax.set_title('Estrategia Simple  ($1 siempre)', fontsize=10, pad=6)
        ax.set_xlabel('Ronda'); ax.set_ylabel('Balance ($)')
        ax.legend(fontsize=8, facecolor=BG_CARD, labelcolor=WHITE,
                  edgecolor=TEXT_DIM)

        # — Historial Martingala —
        ax = self.ax_mar
        ax.clear(); self._estilo_ax(ax)
        for run in runs_mar:
            ax.plot(x, run, alpha=0.18, color=C_GREEN, linewidth=0.7)
        prom_mar = np.mean(runs_mar, axis=0)
        ax.plot(x, prom_mar, color=C_GREEN, linewidth=2.2, label='Promedio')
        ax.axhline(balance_ini, color=WHITE, linestyle='--',
                   linewidth=1, alpha=0.45, label=f'Inicio ${balance_ini:.0f}')
        ax.axhline(0, color=C_RED, linewidth=1, alpha=0.6)
        ax.set_title('Estrategia Martingala  (dobla al perder)', fontsize=10, pad=6)
        ax.set_xlabel('Ronda'); ax.set_ylabel('Balance ($)')
        ax.legend(fontsize=8, facecolor=BG_CARD, labelcolor=WHITE,
                  edgecolor=TEXT_DIM)

        # — Boxplot comparativo —
        ax = self.ax_box
        ax.clear(); self._estilo_ax(ax)
        finals_sim = [r[-1] for r in runs_sim]
        finals_mar = [r[-1] for r in runs_mar]
        bp = ax.boxplot([finals_sim, finals_mar],
                        patch_artist=True, widths=0.4,
                        medianprops=dict(color=WHITE, linewidth=2))
        bp['boxes'][0].set_facecolor(C_BLUE + '55')
        bp['boxes'][1].set_facecolor(C_GREEN + '55')
        for whisker in bp['whiskers']:
            whisker.set_color(TEXT_DIM)
        for cap in bp['caps']:
            cap.set_color(TEXT_DIM)
        for flier in bp['fliers']:
            flier.set(marker='o', color=TEXT_DIM, alpha=0.5, markersize=3)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['Simple', 'Martingala'], color=TEXT_DIM, fontsize=9)
        ax.axhline(balance_ini, color=WHITE, linestyle='--',
                   linewidth=1, alpha=0.45)
        ax.axhline(0, color=C_RED, linewidth=1, alpha=0.6)
        ax.set_title('Distribución del Balance Final', fontsize=10, pad=6)
        ax.set_ylabel('Balance final ($)')

        # — Histograma de balances finales —
        ax = self.ax_hist
        ax.clear(); self._estilo_ax(ax)
        bins = np.linspace(
            min(min(finals_sim), min(finals_mar)),
            max(max(finals_sim), max(finals_mar)),
            25)
        ax.hist(finals_sim, bins=bins, alpha=0.6, color=C_BLUE,  label='Simple')
        ax.hist(finals_mar, bins=bins, alpha=0.6, color=C_GREEN, label='Martingala')
        ax.axvline(balance_ini, color=WHITE, linestyle='--',
                   linewidth=1.2, alpha=0.6, label=f'Inicio ${balance_ini:.0f}')
        ax.axvline(0, color=C_RED, linewidth=1.2, alpha=0.7)
        ax.set_title('Histograma de Balance Final', fontsize=10, pad=6)
        ax.set_xlabel('Balance final ($)'); ax.set_ylabel('Frecuencia')
        ax.legend(fontsize=8, facecolor=BG_CARD, labelcolor=WHITE,
                  edgecolor=TEXT_DIM)

        self.canvas.draw()

    # ── Estadísticas ──────────────────────────────────────────────────────────

    def _actualizar_stats(self, runs_sim, runs_mar, balance_ini):
        def calc(runs):
            finals = np.array([r[-1] for r in runs])
            return {
                'avg':  finals.mean(),
                'min':  finals.min(),
                'max':  finals.max(),
                'ruin': 100 * (finals <= 0).sum() / len(finals),
            }

        s, m = calc(runs_sim), calc(runs_mar)

        self.stat_vars['sim_avg'].set(f'${s["avg"]:.2f}')
        self.stat_vars['sim_min'].set(f'${s["min"]:.2f}')
        self.stat_vars['sim_max'].set(f'${s["max"]:.2f}')
        self.stat_vars['sim_ruin'].set(f'{s["ruin"]:.1f} %')

        self.stat_vars['mar_avg'].set(f'${m["avg"]:.2f}')
        self.stat_vars['mar_min'].set(f'${m["min"]:.2f}')
        self.stat_vars['mar_max'].set(f'${m["max"]:.2f}')
        self.stat_vars['mar_ruin'].set(f'{m["ruin"]:.1f} %')

        # Veredicto
        if s['avg'] > m['avg'] and s['ruin'] <= m['ruin']:
            v = ('La estrategia Simple preserva mejor el capital con menor '
                 'riesgo de ruina. Martingala puede dar ganancias altas '
                 'pero es más volátil.')
        elif m['avg'] > s['avg'] and m['ruin'] <= s['ruin']:
            v = ('La Martingala supera a la Simple en promedio y con menor '
                 'riesgo. Sin embargo, la volatilidad es mayor.')
        else:
            v = ('Ambas estrategias pierden dinero a largo plazo. '
                 'La Simple es más estable; la Martingala es más volátil '
                 'pero puede recuperar pérdidas consecutivas.')
        self.stat_vars['veredicto'].set(v)

        # Ganador explícito (basado en balance promedio y % de ruina)
        pts_sim = (1 if s['avg'] >= m['avg'] else 0) + (1 if s['ruin'] <= m['ruin'] else 0)
        pts_mar = (1 if m['avg'] > s['avg'] else 0) + (1 if m['ruin'] < s['ruin'] else 0)
        if pts_sim > pts_mar:
            nombre, color = 'Estrategia Simple', C_BLUE
        elif pts_mar > pts_sim:
            nombre, color = 'Estrategia Martingala', C_GREEN
        else:
            nombre, color = 'Empate', C_GOLD
        self.ganador_var.set(f'🏆  {nombre}')
        self.ganador_label.config(fg=color)


# ─── Punto de entrada ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = AppRuleta()
    app.mainloop()
