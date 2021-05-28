using Distributed
@everywhere using Pkg
@everywhere Pkg.activate("sparseinverseproblems/")
@everywhere using SparseInverseProblems
using DelimitedFiles
using CSV
using Statistics

#parameters
sigma_lb = 1.0
sigma_ub = 1.4
tau = 2.0*10^12
final_loss_improvement = 1000.0
min_weight = 600.0
max_iters = 200
max_cd_iters = 10

img = readdlm(ARGS[1])

threshold = 0.0 

points = fit_2048x2048_img_tiles(img, sigma_lb, sigma_ub, tau, final_loss_improvement, min_weight, max_iters, max_cd_iters, threshold)

CSV.write(ARGS[2], points)

