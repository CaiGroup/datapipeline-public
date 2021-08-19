using DelimitedFiles
using CSV
using DataFrames
using Statistics
using SparseInverseProblems

sigma_ub = snakemake.params["sigma_ub"]#1.6
sigma_lb = snakemake.params["sigma_lb"]#0.7
tau = 2.0*10^12
min_allowed_separation = snakemake.params["min_allowed_separation"]#2.0


img = readdlm(snakemake.input[1])

points_w_dup = DataFrame(CSV.File(snakemake.input[2]))

noise_mean = 0.0

points = remove_duplicates(points_w_dup, img, sigma_lb, sigma_ub, tau, noise_mean, min_allowed_separation)


CSV.write(snakemake.output[1], points)
