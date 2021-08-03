
* Take config from similar file as webfish uses - file paths, that kind of stuff

First rule: either given one user+dataset or just the base file path, create a spreadsheet or other database
 (entry) for datasets with some basic metadata: n hybs, n pos, presence of background or segmentation images,
 creation/mtime


Second rule: given the basic dataset metadata that's up to date, create a new analysis

^^^ Extensive logging and recordkeeping is a luxury, but at the most basic and direct level, we can reimplement
the current pipeline with improved modularity and transparency. Possibly better error handling as well -
e.g., checks are nice but not *required* as input files for subsequent steps, so don't fail if they give an error

Probably requires breaking up into callable (and importable) scripts more neatly.
This could be a potential entry point for people's customizations: if we can make a simple,
uniform format for a script at each step, then anyone can substitute in their own script.
e.g. - standardized input and output filenames for preprocessing, then you can write a
script or notebook that does whatever as long as it conforms to that pattern.

* check_for_jsons.py calls kickoff_analysis.sh FOR EACH POSITION
    (thin wrapper around json_analysis.py).
    So the following is done for each position in parallel:
Input files: barcode key, hyb cycle folders, optional experiment metadata
1. Segmentation: segmenter.retrieve_labeled_img() -> labeled_img.tif
2. Alignment: run_alignment.run_alignment() (calls an alignment script) -> offsets.json
3. Chromatic aberration (this is preprocessing)
4. Preprocessing (currently rolled into dot detection) -> preprocessed images + record of what was done, possibly
    temporary? But good to save for reuse possibly.
5. Dot detection on preprocessed images (parallelized: each hyb) -> locations.csv (+checks)
6. Decoding: splits up into cells by indexing labeled_img with rounded coords of detected dots
    and writing these segments of the dot spreadsheet to per-cell directories (seg_locs.py).
    Output of decoding per cell is "pre_seg_diff_1_minseeds_3_filtered.csv" file, these
    are combined with segmentation info to Segmentation/Channel_X/gene_locations_assigned_to_cell.csv
    As well as count_matrix.csv
7. Finally, these could be combined across channels if needed for the final cell x gene matrix
    (e.g. count_matrix_all_channels.csv)

