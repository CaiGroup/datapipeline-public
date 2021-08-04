configfile: 'analysis.yaml'

# something that creates a file detailing every hyb and position
# as well as extra information: barcode key, seg images,
# experiment metadata
rule gen_manifest:
    input:
        # some config values
    expand('HybCycle_{hyb}/MMStack_Pos{position}.ome.tif',
        hyb=range(config['n_hybs']),
        position=range(config['n_positions'])
    )
    output:
        'experiment_manifest'


####### BEGIN per hyb per position

# can run per hyb per position, using hyb0 as input
rule alignment:
    input:
        'experiment_manifest',
        expand('HybCycle_0/MMStack_Pos{thispos}',
            thispos=config['pos']),
        expand('HybCycle_{thishyb}/MMStack_Pos{thispos}',
               # some way of passing which hyb and pos each job is running
               thishyb=config['hyb'],
               thispos=config['pos'])
    output:
        'offsets.json',
        expand('Hyb{thishyb}_Pos{thispos}_aligned.tif',
           # some way of passing which hyb and pos each job is running
           thishyb=config['hyb'],
           thispos=config['pos'])
    log:
        # HybX_PosY_alignment.log


# can run per hyb per position
# run alignment first so that we segment aligned/shifted images
rule segmentation:
    input:
        'experiment_manifest',
        'offsets.json',
        expand('HybCycle_{thishyb}/MMStack_Pos{thispos}',
            # some way of passing which hyb and pos each job is running
            thishyb=config['hyb'],
            thispos=config['pos'])
    output:
        'labeled_img.tif'
    log:
        # HybX_PosY_segmentation.log

# can run per hyb per position
rule preprocessing:
    input:
        'experiment_manifest',
        expand('Hyb{thishyb}_Pos{thispos}_aligned.tif',
           # some way of passing which hyb and pos each job is running
           thishyb=config['hyb'],
           thispos=config['pos'])
    output:
        temp(expand('Hyb{thishyb}_Pos{thispos}_preprocessed.tif',
               # some way of passing which hyb and pos each job is running
               thishyb=config['hyb'],
               thispos=config['pos']))
    log:
        # HybX_PosY_preprocessing.log

# can run per hyb per position (per channel)
rule dot_detection:
    input:
        'experiment_manifest',
        temp(expand('Hyb{thishyb}_Pos{thispos}_preprocessed.tif',
               # some way of passing which hyb and pos each job is running
               thishyb=config['hyb'],
               thispos=config['pos'])),
        'offsets.json'
    output:
        'locations.csv'
    log:
        # HybX_PosY_dotdetection.log

###### END per hyb per position


rule combine_data:
    input:
        'experiment_manifest',
        'locations.csv' # expand all hybs
        'offsets.json' # expand all hybs
    output:
        'locations_combined_aligned.csv'


# can run per position, not per hyb - needs all
# possible per channel or not
rule decoding:
    input:
        'experiment_manifest',
        'preprocessed_images',
        'labeled_img.tif',
        'locations_combined_aligned.csv',
        'barcodekey',
        # various config options
    output:
        'pre_seg_diff_1_minseeds_3_filtered.csv',
        'gene_locations_assigned_to_cell.csv',
        'count_matrix.csv',
        'count_matrix_all_channels.csv'

rule stitch:
    input:
        'locations.csv',
        'gene_locations_assigned_to_cell.csv',
        'position.pos'
    output:
        'overview.tif',
        'locations_stitched.csv'