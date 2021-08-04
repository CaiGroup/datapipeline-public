import pandas as pd
import numpy as np
from pathlib import Path

MAIN = config.get('main_dir', '/groups/CaiLab')
USER = config.get('user', 'lincoln')
DATASET = config.get('dataset', '2020-08-08-takei')

RAW_DIR = Path(MAIN, 'personal', USER, 'raw', DATASET)

OUT_DIR = Path(MAIN, 'personal', 'lincoln', 'snakemake_test', DATASET)

rule find_experiment_files:
    input:
        RAW_DIR
    output:
        exp_tab=OUT_DIR / "exp_tab.csv"
    run:
        globbed = glob_wildcards(input[0] + '/HybCycle_{hyb, \d+}/MMStack_Pos{position, \d+}.ome.tif')

        filenames = [f'{RAW_DIR}/HybCycle_{h}/MMStack_Pos{p}.ome.tif' for p, h in zip(globbed.position, globbed.hyb)]

        df = pd.DataFrame({'position': globbed.position, 'hyb': globbed.hyb, 'filename': filenames})
        df['position'] = df['position'].astype(int)
        df['hyb'] = df['hyb'].astype(int)

        df = df.set_index(['position', 'hyb']).sort_index()
        df.to_csv(output.exp_tab)


