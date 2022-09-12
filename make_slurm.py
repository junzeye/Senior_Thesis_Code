import sys, os
from itertools import product

alpha = [0.001, 0.01, 0.1]
depth = [4,6,8]
seeds = [37, 42, 53]
hidden_dims = [20, 40, 60, 80, 100, 120]

# create the folder to store all the slurm .out files
dirpath = 'synthetic_tests/CTG_width/out'
os.makedirs(dirpath, exist_ok = True)

# create the folder to store all the slurm scripts
dirpath = 'slurm_scripts/vary_width'
os.makedirs(dirpath, exist_ok = True)

for a, d, s, hidden_dim in product(alpha, depth, seeds, hidden_dims):

    slurm_msg = (
        '#!/bin/bash\n'
        f'#SBATCH --job-name=oct_dim{hidden_dim}_a{a}_d{d}_s{s}\n'
        '#SBATCH --nodes=1                # node count\n'
        '#SBATCH --ntasks=1               # total number of tasks across all nodes\n'
        '#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)\n'
        '#SBATCH --mem-per-cpu=12G         # memory per cpu-core (4G is default)\n\n'
        f'#SBATCH --output=./synthetic_tests/CTG_width/out/oct_dim{hidden_dim}_a{a}_d{d}_s{s}.out    # Standard output and error log\n'
        '#SBATCH --time=3:59:00          # total run time limit (HH:MM:SS)\n'
        '#SBATCH --mail-type=fail         # send email if job fails\n'
        '#SBATCH --mail-user=junzey@princeton.edu\n\n'

        'module purge\n'
        'module load anaconda3/2022.5 gurobi/9.5.1\n'
        'conda activate thesis\n\n'

        'python experiment_instance.py '
        f'--a {a} --d {d} --s {s} --hidden_dim {hidden_dim}'
    )

    script_name = dirpath + '/' + f'oct_dim_{hidden_dim}_a_{a}_d_{d}_s_{s}.slurm'

    with open(script_name, 'w') as f:
        f.write(slurm_msg)