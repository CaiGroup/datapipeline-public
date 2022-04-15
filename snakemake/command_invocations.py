# This is a list of (important) calls to os.system() and subprocess.call() found in the pipeline.
# These are points where snakemake can be probably be used directly to complete a step.

### Begin os.system() invocations

# align_scripts/matlab_dapi.py:55
cmd = """  matlab -r "addpath('{0}');addpath('{1}');full_wrap_alignment('{2}', '{3}'); quit"; """
cmd = cmd.format(matlab_dapi_dir, bfmatlab_dir, mat_dst, dest)
os.system(cmd)

# align_scripts/matlab_dapi/get_matlab_dapi_alignment.py:18
cmd = """  matlab -r "full_wrap_alignment('{0}', '{1}','{2}'); quit"; """
cmd = cmd.format(fixed_src, moving_src, dest)
os.system(cmd)

# chromatic_aberration/run.py:32
cmd = """  
matlab -r "addpath('/home/nrezaee/test_cronjob/chromatic_aberration/scripts'); 
beadtformglobal( '{0}' , {1}, {2}, '{3}'); quit"; 
"""
cmd = cmd.format(beads_dir, num_channels, pos_array, t_forms_dest)
os.system(cmd)

# colocalization/colocalize.py:9
cmd = """  
matlab -r "addpath('/home/nrezaee/test_cronjob/colocalization/');
addpath('/home/nrezaee/test_cronjob/colocalization/matlab');
main_coloc('{0}', '{1}', {2}); quit"; 
"""
radius = 2
cmd = cmd.format(locations_src, dest, radius)
os.system(cmd)

# decoding/decoding_non_parallel.py:73
cmd = """  
matlab -r "addpath('{0}');
main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); 
quit"; 
"""

if channel_index == None and number_of_individual_channels_for_decoding == None:
    cmd = cmd.format(
        decoding_dir,
        barcode_src,
        locations_src,
        dest,
        num_of_rounds,
        total_number_of_channels,
        '[]',
        '[]',
        allowed_diff,
        min_seeds
    )
else:
    cmd = cmd.format(
        decoding_dir,
        barcode_src,
        locations_src,
        dest,
        num_of_rounds,
        total_number_of_channels,
        channel_index + 1,
        number_of_individual_channels_for_decoding,
        allowed_diff,
        min_seeds
    )

os.system(cmd)

# dot_detection/dot_detectors_3d/matlab_dot_detection/matlab_dot_detector.py:68
cmd = """  
/software/Matlab/R2019a/bin/matlab -r "addpath('{0}');addpath('{1}');
biggest_jump('{2}', {3}, {4}, {5}, {6}, '{7}'); quit"; 
"""
cmd = cmd.format(bfmatlab_dir, functions_dir, tiff_src, channel, threshold, nbins, strictness, dest)
os.system(cmd)

# helpers/sync_specific_analysis.py
cmd = 'rclone copy /groups/CaiLab/analyses' + spec_analysis + ' onedrive_caltech:Analyses' + spec_analysis
os.system(cmd)

# read_barcode/read_barcode.py:108
cmd = """  matlab -r "addpath('{2}'); readbarcode( '{0}' , '{1}', 'header'); quit"; """
cmd = cmd.format(barcode_src, barcode_dst, read_barcode_dir)
os.system(cmd)

# segmentation/cellpose_segment/helpers/get_cellpose_labeled_img.py:146
# calls Alex's nucsmoothresize script
resize_script = os.path.join(os.getcwd(), 'segmentation/cellpose_segment/helpers/nucsmoothresize')
cmd = ' '.join(['sh', resize_script, masked_file_path, str(tiff.shape[2]), dst])
print(f'{cmd=}')
os.system(cmd)

# segmentation/cellpose_segment/helpers/get_cyto_labeled_img.py:103
# also resize script
resize_script = os.path.join(os.getcwd(), 'segmentation/cellpose_segment/helpers/nucsmoothresize')
if dst == None:
    temp_path = os.path.join(rand_dir, 'expanded.tif')
    cmd = ' '.join(['sh', resize_script, masked_file_path, str(tiff.shape[2]), temp_path])
    os.system(cmd)

# segmentation/post_processing/match_cyto_to_nuclei/nuccymatch.py:52
# calls Alex's nuc to cyto match script
nuccy_path = os.path.join(post_process_dir, 'match_cyto_to_nuclei', 'nuccytomatch')
cmd = 'sh ' + nuccy_path + ' ' + temp_nuclei_path + ' ' \
      + cyto_2d_src + ' ' + temp_match_path + ' ' + str(area_tol)
os.system(cmd)

# Not shown due to being not as important now:
# decoding/previous_locations_decoding.py
# decoding/previous_points_decoding.py
# deployment_tests/*
# dot_detection/dot_detectors_3d/ilastik*
# dot_detection/dot_detectors_3d/inflection_point.py
# dot_detection/gaussian_fitting_better
# dot_detection/radial_center

### Begin subprocess.call() invocations

# check_for_jsons.py:574
# this is the per-position invocation of the kickoff script
kickoff_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kickoff_analysis.sh")
subprocess.call([
    "sbatch", "--job-name", batch_name,
    "--nodes", nodes,
    "--ntasks", ntasks,
    "--mem-per-cpu", mem_per_cpu,
    "--time", time,
    "--mail-type=BEGIN", "--mail-type=END", "--mail-type=FAIL",
    "--output", output_file_path,
    kickoff_script, json_name, position, data["personal"], data["experiment_name"],
    running_in_slurm, os.path.dirname(os.path.abspath(__file__)), email
])

# align_scripts/run_alignment.py:200
# this is the main entry point into the alignment. Note that it writes the python command
# to the script (in the temp dir) and just calls this script with sbatch.
list_cmd = [
    'python',
    align_dir + '/' + align_function + '.py',
    '--fixed_src', fixed_file_path,
    '--moving_src', tiff_file_path,
    '--rand', rand_dir,
    '--num_wav', str(num_wav)
]
cmd = ' '.join(list_cmd)

script_name = os.path.join(rand_dir, 'align.sh')
out_file_path = os.path.join(rand_dir, 'slurm_align.out')

with open(script_name, 'w') as f:
    f.write('#!/bin/bash \n')
    f.write(cmd)

if align_function == 'matlab_dapi':
    time_for_slurm = '00:20:00'
    ntasks = str(5)
    mem_per_cpu = '15G'
else:
    time_for_slurm = '00:10:00'
    ntasks = str(1)
    mem_per_cpu = '10G'

call_me = [
    'sbatch',
    '--output', out_file_path,
    '--job-name', rand_list[sub_dirs.index(sub_dir)],
    "--time", time_for_slurm,
    "--mem-per-cpu", mem_per_cpu,
    "--ntasks", ntasks,
    script_name
]
subprocess.call(call_me)

# decoding/decoding_parallel.py:123
# this is the main entry point to the current per-cell job decoding workflow.
# again, the matlab command is written to the script in the temp directory,
# then sbatch is invoked on this script.
cmd = """  
matlab -r "addpath('{0}');
main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); 
quit"; 
"""

cwd = os.getcwd()
cwd = cwd[cwd.find('/home'):]

if debug:
    decoding_dir = os.path.join(cwd, 'helpers')
else:
    decoding_dir = os.path.join(cwd, 'decoding', 'helpers')

if channel_index == None and number_of_individual_channels_for_decoding == None:
    cmd = cmd.format(
        decoding_dir,
        barcode_src,
        locations_cell_path,
        dest,
        num_of_rounds,
        total_number_of_channels,
        '[]',
        '[]',
        allowed_diff,
        min_seeds
    )
else:
    cmd = cmd.format(
        decoding_dir,
        barcode_src,
        locations_cell_path,
        dest,
        num_of_rounds,
        total_number_of_channels,
        channel_index+1,
        number_of_individual_channels_for_decoding,
        allowed_diff,
        min_seeds
    )

script_name = os.path.join(dest, 'decoding.sh')
with open(script_name , 'w') as f:
    f.write('#!/bin/bash \n')
    f.write(cmd)

output_path = os.path.join(dest, 'slurm_decoding.out')

call_me = [
    'sbatch',
    '--begin', 'now+120',
    '--job-name', rand,
    "--output", output_path,
    "--time", "0:50:00",
    "--mem-per-cpu", "8G",
    '--ntasks', '1', script_name
]

subprocess.call(call_me)

# dot_detection/dot_detection_class12.py:557
# this is the invocation of the different dot detection methods. It's precedeed
# by a long if/else chain for different dot detection methods, each of which is in
# a different script and requires a LONG list of different arguments.
# This in invoked for every hyb in the experiment folder.
if 'top' in self.dot_detection:

    n_dots = int(self.dot_detection.split('top')[1].split('dots')[0])

    list_cmd = [
        'python', dot_detection_dir + '/get_top_n_dots.py', '--offset0', offset[0],
        '--offset1', offset[1], '--offset2', offset[2], '--analysis_name', self.analysis_name,
        '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction,
        '--tiff_src', tiff_file_path, '--norm', self.normalization, '--channels', self.decoding_individual,
        '--chromatic', self.chromatic_aberration, '--n_dots', n_dots, '--num_wav', self.num_wav,
        '--rand', rand_dir, '--num_z', self.num_z, '--stack_z_s', self.stack_z_dots,
        '--rolling_ball', self.rolling_ball, '--tophat', self.tophat, '--blur', self.blur
    ]

    list_cmd = [str(i) for i in list_cmd]

    time_for_slurm = "00:11:00"

elif self.dot_detection == "biggest jump":

    list_cmd = [
        'python', dot_detection_dir + '/hist_jump.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2',
        offset[2],
        '--analysis_name', self.analysis_name, '--vis_dots', self.visualize_dots, '--back_subtract',
        self.background_subtraction,
        '--tiff_src', tiff_file_path, '--norm', self.normalization, '--channels', self.decoding_individual,
        '--chromatic', self.chromatic_aberration, '--rand', rand_dir, '--gaussian', self.gaussian_fitting,
        '--radial_center', self.radial_center, '--strictness', self.strictness_dot_detection,
        '--num_wav', self.num_wav, '--z_slices', z_slice, '--back_blob_removal', self.background_blob_removal
    ]

    list_cmd = [str(i) for i in list_cmd]

    time_for_slurm = "0:12:00"

elif self.dot_detection == "matlab 3d":

    list_cmd = [
        'python', dot_detection_dir + '/matlab_3d.py', '--offset0', offset[0], '--offset1', offset[1],
        '--offset2', offset[2], '--analysis_name', self.analysis_name, '--vis_dots', self.visualize_dots,
        '--back_subtract', self.background_subtraction, '--tiff_src', tiff_file_path, '--norm', self.normalization,
        '--channels', self.decoding_individual, '--chromatic', self.chromatic_aberration,
        '--rand', rand_dir, '--gaussian', self.gaussian_fitting, '--radial_center', self.radial_center,
        '--strictness', self.strictness_dot_detection, '--num_wav', self.num_wav, '--z_slices', z_slice,
        '--nbins', self.nbins, '--threshold', self.threshold, '--stack_z_s', self.stack_z_dots,
        '--back_blob_removal', self.background_blob_removal, '--rolling_ball', self.rolling_ball,
        '--tophat', self.tophat, '--blur', self.blur, '--blur_kernel_size', self.blur_kernel_size,
        '--rolling_ball_kernel_size', self.rolling_ball_kernel_size, '--tophat_kernel_size', self.tophat_kernel_size
    ]

    list_cmd = [str(i) for i in list_cmd]

    time_for_slurm = "02:00:00"


elif self.dot_detection == "biggest jump 3d":

    list_cmd = [
        'python', dot_detection_dir + '/hist_jump_3d.py', '--offset0', offset[0], '--offset1', offset[1],
        '--offset2', offset[2], '--analysis_name', self.analysis_name, '--vis_dots', self.visualize_dots,
        '--back_subtract', self.background_subtraction, '--tiff_src', tiff_file_path,
        '--norm', self.normalization, '--channels', self.decoding_individual, '--chromatic', self.chromatic_aberration,
        '--rand', rand_dir, '--gaussian', self.gaussian_fitting, '--radial_center', self.radial_center,
        '--strictness', self.strictness_dot_detection, '--num_wav', self.num_wav, '--z_slices', z_slice,
        '--num_z', self.num_z, '--nbins', self.nbins, '--threshold', self.threshold, '--radius_step', self.radius_step,
        '--num_radii', self.num_radii, '--stack_z_s', self.stack_z_dots, '--back_blob_removal',
        self.background_blob_removal,
        '--rolling_ball', self.rolling_ball, '--tophat', self.tophat, '--blur', self.blur,
        '--blur_kernel_size', self.blur_kernel_size, '--rolling_ball_kernel_size', self.rolling_ball_kernel_size,
        '--tophat_kernel_size', self.tophat_kernel_size, '--min_sigma', self.min_sigma,
        '--max_sigma', self.max_sigma, '--num_sigma', self.num_sigma, '--bool_remove_bright_dots',
        self.bool_remove_bright_dots,
        '--tophat_raw_data', self.tophat_raw_data, '--tophat_raw_data_kernel', self.tophat_raw_data_kernel_size,
        '--dilate_background_kernel', self.dilate_background_kernel_size
    ]

    list_cmd = [str(i) for i in list_cmd]

    time_for_slurm = "0:35:00"
else:

    raise Exception("The dot detection argument was not valid.")

cmd = ' '.join(list_cmd)

script_name = os.path.join(rand_dir, 'dot_detection.sh')
with open(script_name, 'w') as f:
    print('#!/bin/bash', file=f)
    print(cmd, file=f)

out_path = os.path.join(rand_dir, 'slurm.out')
call_me = [
    'sbatch',
    '--job-name', rand_list[sub_dirs.index(sub_dir)],
    '--output', out_path,
    "--time", time_for_slurm,
    "--mem-per-cpu", "10G",
    '--ntasks', '2',
    script_name
]

subprocess.call(call_me)

# segmentation/cellpose_segment/helpers/get_cellpose_labeled_img.py:135
# this is the main entry point for calling cellpose in the singularity container.
# Again, the singularity/python command is written to the batch file in the tmpdir,
# and then sbatch is invoked on this file.

diameter_param = ' --diameter ' + str(float(nuclei_radius)*2)
flow_thresh_param = ' --flow_threshold ' + str(flow_threshold)
cell_prob_thresh_param = ' --cellprob_threshold ' + str(cell_prob_threshold)

bind_paths = f'/central/scratch/{USER},/groups/CaiLab/personal/temp,/groups/CaiLab/personal/singularity/lib/python3.6/site-packages:/usr/lib/python3.6/site-packages'
sing_and_cellpose_cmd = f'singularity  exec --bind {bind_paths} --nv /groups/CaiLab/personal/singularity/tensorflow-20.02-tf1-py3.sif python -m cellpose '
default_params = ' --img_filter dapi_channel --pretrained_model cyto --use_gpu --no_npy --save_tif --dir '
import time; time.sleep(1)

if num_z >= 4:
    command_for_cellpose = sing_and_cellpose_cmd + ' --do_3D' + diameter_param + flow_thresh_param + \
                        cell_prob_thresh_param + default_params
if num_z < 4:
    command_for_cellpose = sing_and_cellpose_cmd + diameter_param + flow_thresh_param + \

command_for_cellpose_with_dir = command_for_cellpose + rand_dir
script_name = os.path.join(rand_dir, 'seg.sh')

slurm_out_dst = os.path.join(rand_dir, 'slurm_seg.out')

os.system('chmod 777 ' +  rand_dir)
os.system('chmod 777 -R ' +  rand_dir)

with open(script_name , 'w') as f:
    f.write('#!/bin/bash \n')
    f.write('#SBATCH --gres=gpu:1 \n')
    f.write('#SBATCH -o ' + slurm_out_dst + ' \n')
    f.write('module load singularity/3.5.2 \n')
    f.write(command_for_cellpose_with_dir)

call_me = [
    'sbatch',
    '--job-name',
    rand_list[0],
    "--time",
    "0:05:00",
    "--mem-per-cpu",
    "5G",
    script_name
]
subprocess.call(call_me)

# segmentation/cellpose_segment/helpers/get_cyto_labeled_img.py:75
# This is the entry point to cellpose segmentation for cytoplasm, almost identical to above.

command_for_cellpose = 'singularity  exec --bind /central/scratch/$USER'
                       '--nv /home/nrezaee/sandbox/cellpose/gpu/tensorflow-20.02-tf1-py3.sif '
                       'python -m cellpose  --img_filter dapi_channel_2d --pretrained_model cyto '
                       '--diameter 0 --use_gpu --no_npy --save_png --dir '
command_for_cellpose_with_dir = command_for_cellpose + rand_dir

script_name = os.path.join(rand_dir, 'seg.sh')
with open(script_name, 'w') as f:
    f.write('#!/bin/bash \n')
    f.write('#SBATCH --gres=gpu:1 \n')
    f.write(command_for_cellpose_with_dir)

call_me = [
    'sbatch',
    '--job-name',
    rand_list[0],
    "--time",
    "1:00:00",
    "--mem-per-cpu",
    "10G",
    script_name
]
subprocess.call(call_me)

# segmentation/cellpose_segment/helpers/get_cyto_labeled_img.py:107
# This calls Alex's nucsmoothresize script. For some reason, it's called by os.system()
# in one clause of an if/else but subprocess.call() in the other.
resize_script = os.path.join(os.getcwd(), 'segmentation/cellpose_segment/helpers/nucsmoothresize')

if dst == None:
    temp_path = os.path.join(rand_dir, 'expanded.tif')
    cmd = ' '.join(['sh', resize_script, masked_file_path, str(tiff.shape[2]), temp_path])
    os.system(cmd)
    labeled_img = tifffile.imread(temp_path)
else:
    subprocess.call(['sh', resize_script, masked_file_path, str(tiff.shape[2]), dst])
    labeled_img = imageio.imread(dst)

# segmentation/post_processing/get_cyto_labeled_img.py:88
# This seems to be nearly exactly the same as the above file... I'm not sure it's actually used
# It also calls the resize script the same as the above file.

sing_and_cellpose_cmd = 'singularity  exec --bind /central/scratch/$USER '
                        '--nv /home/nrezaee/sandbox/cellpose/gpu/tensorflow-20.02-tf1-py3.sif '
                        'python -m cellpose '
persistent_params = ' --img_filter dapi_channel_2d --pretrained_model cyto --use_gpu --no_npy --save_png '
cyto_cell_prob_thresh_cmd = ' --cellprob_threshold ' + str(cell_prob_threshold)
cyto_flow_thresh_cmd = ' --flow_threshold ' + str(cell_flow_threshold)
diameter_cmd = ' --diameter ' + str(cyto_radius)

command_for_cellpose = sing_and_cellpose_cmd + persistent_params + cyto_cell_prob_thresh_cmd + cyto_flow_thresh_cmd + diameter_cmd + ' --dir '
command_for_cellpose_with_dir = command_for_cellpose + rand_dir

script_name = os.path.join(rand_dir, 'seg.sh')
with open(script_name, 'w') as f:
    f.write('#!/bin/bash \n')
    f.write('#SBATCH --gres=gpu:1 \n')
    f.write(command_for_cellpose_with_dir)

call_me = [
    'sbatch',
    '--job-name', rand_list[0],
    "--time", "1:00:00",
    "--mem-per-cpu", "10G",
    script_name
]
subprocess.call(call_me)

# segmentation/post_processing/distance_between_cells/get_distance_between_cells.py:17
# This calls Alex's nuctouchresize script
nuctouchresize_file_path = os.path.join(post_process_dir, 'distance_between_cells', 'nuctouchresize')
subprocess.call(['sh', nuctouchresize_file_path, label_img_src, str(dist_between_nuclei)])

# segmentation/post_processing/edge_deletion/get_edge_deletion.py:16
# This calls Alex's nucboundzap script
nucboundzap_file_path = os.path.join(post_process_dir, 'edge_deletion', 'nucboundzap')
subprocess.call(['sh', nucboundzap_file_path, label_img_src, str(edge_delete_dist)])
