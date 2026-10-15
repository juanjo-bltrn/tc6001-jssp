import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def parse_jssp_file(file_path: str):
    """
    Reads JSSP schedule from txt.
    Format: [job, operation_idx, machine, start_time, end_time]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    operations = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 5:
                raise ValueError(f"[!] Line {line_num}: 5 columns expected, {len(parts)} found.")

            job, op_idx, machine, start, end = map(int, parts)
            operations.append({
                'job': job,
                'op_idx': op_idx,
                'machine': machine,
                'start': start,
                'end': end,
                'duration': end - start
            })
            
    return operations


def validate_schedule(operations: list):
    """
    Checks if the schedule is valid:
    1. Valid times (start >= 0, end >= start).
    2. No overlaps on the same machine.
    3. Adherence to precedence constraints in each Job (Op k+1 starts after Op k ends).
    """
    errors = []

    # I. Validation of non-negative and consistent times
    for op in operations:
        if op['start'] < 0 or op['end'] < 0:
            errors.append(f"Negative times in Job {op['job']} (Op {op['op_idx']}): [{op['start']}, {op['end']}]")
        if op['end'] < op['start']:
            errors.append(f"End time is earlier than start time in Job {op['job']} (Op {op['op_idx']}): [{op['start']}, {op['end']}]")

    # II. Validation of machine capacity (No overlaps)
    by_machine = {}
    for op in operations:
        by_machine.setdefault(op['machine'], []).append(op)

    for machine, m_ops in by_machine.items():
        m_ops_sorted = sorted(m_ops, key=lambda x: (x['start'], x['end']))
        for i in range(len(m_ops_sorted) - 1):
            curr = m_ops_sorted[i]
            nxt = m_ops_sorted[i + 1]
            if nxt['start'] < curr['end']:
                errors.append(
                    f"Overlap in Machine {machine}: Job {curr['job']} (Op {curr['op_idx']}, [{curr['start']}-{curr['end']}]) "
                    f"collides with Job {nxt['job']} (Op {nxt['op_idx']}, [{nxt['start']}-{nxt['end']}])"
                )

    # III. Validation of precedence by Job
    by_job = {}
    for op in operations:
        by_job.setdefault(op['job'], []).append(op)

    for job, j_ops in by_job.items():
        j_ops_sorted = sorted(j_ops, key=lambda x: x['op_idx'])
        for i in range(len(j_ops_sorted) - 1):
            curr = j_ops_sorted[i]
            nxt = j_ops_sorted[i + 1]
            if nxt['start'] < curr['end']:
                errors.append(
                    f"Precedence violation in Job {job}: Operation {curr['op_idx']} ends at t={curr['end']}, "
                    f"but Operation {nxt['op_idx']} starts at t={nxt['start']}"
                )

    is_valid = len(errors) == 0
    return is_valid, errors


def plot_jssp_schedule(file_path: str, save_path: str = None, show: bool = False):
    """
    Validates and plots a JSSP schedule.
    """
    operations = parse_jssp_file(file_path)
    is_valid, errors = validate_schedule(operations)

    if not is_valid:
        print("[!] Invalid schedule. Found errors:")
        for err in errors:
            print(f"  • {err}")
        return False

    print("Valid schedule. Generating plot...")

    machines = sorted(list(set(op['machine'] for op in operations)))
    jobs = sorted(list(set(op['job'] for op in operations)))
    makespan = max(op['end'] for op in operations)

    # Texturas...
    colors = plt.cm.Set2.colors if len(jobs) <= 8 else plt.cm.tab20.colors
    hatches = ['///', '\\\\\\', 'ooo', 'xxx', '***', '+++', '///', '...']
    
    job_styles = {}
    for i, j in enumerate(jobs):
        job_styles[j] = {
            'color': colors[i % len(colors)],
            'hatch': hatches[i % len(hatches)]
        }

    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=120)
    
    # Machines in inverted y-axis
    m_to_y = {m: len(machines) - 1 - idx for idx, m in enumerate(machines)}

    for op in operations:
        y = m_to_y[op['machine']]
        start = op['start']
        duration = op['duration']
        job = op['job']
        style = job_styles[job]

        # Dibujar barra de la operación
        ax.broken_barh(
            [(start, duration)], 
            (y - 0.3, 0.6), 
            facecolor=style['color'], 
            edgecolor='#2c3e50', 
            linewidth=1.2, 
            hatch=style['hatch'],
            alpha=0.85
        )

        # Etiqueta interna en la barra
        if duration > 0:
            label = f"J{job}.{op['op_idx']}"
            cx = start + duration / 2
            cy = y
            fontsize = 8 if duration < (makespan * 0.04) else 9.5
            ax.text(
                cx, cy, label, 
                color='#1a252f', 
                weight='bold', 
                fontsize=fontsize, 
                ha='center', 
                va='center',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.9, edgecolor='none')
            )

    # Configuración de ejes
    ax.set_yticks([m_to_y[m] for m in machines])
    ax.set_yticklabels([f"Machine {m}" for m in machines], fontsize=11, fontweight='bold', color='#2c3e50')
    ax.set_xlabel("Time", fontsize=11, fontweight='bold', color='#2c3e50')
    ax.set_xlim(-makespan * 0.02, makespan * 1.04)

    # Estilo visual
    ax.set_title(f"JSSP Schedule Gantt Chart (Instance: {file_path.split('/')[-1]}; Makespan: {makespan})", fontsize=13, fontweight='bold', pad=15, color='#2c3e50')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#2c3e50')
    ax.spines['bottom'].set_color('#2c3e50')
    ax.grid(axis='x', linestyle=':', alpha=0.6, color='#7f8c8d')

    # Leyendas...
    legend_patches = [
        mpatches.Patch(
            facecolor=job_styles[j]['color'], 
            hatch=job_styles[j]['hatch'], 
            edgecolor='#2c3e50', 
            label=f"Job {j}"
        ) for j in jobs
    ]
    ax.legend(
        handles=legend_patches, 
        bbox_to_anchor=(1.02, 1), 
        loc='upper left', 
        title="Jobs", 
        title_fontsize=10,
        frameon=True, 
        facecolor='#f8f9fa',
        edgecolor='#bdc3c7'
    )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved: {save_path}")

    if show:
        plt.show()

    return True


if __name__ == "__main__":
    # Paths
    instance = "la01"
    file_path = f"solutions/uninformed-dfs/{instance}.txt"
    save_path = f"solutions/uninformed-dfs/schedule-{instance}.png"
    
    # Plot and save
    plot_jssp_schedule(file_path, save_path=save_path, show=False)