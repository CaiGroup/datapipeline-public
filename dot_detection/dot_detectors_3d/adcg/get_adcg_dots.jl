#ncores = 5

using Distributed
# addprocs(ncores)
# @everywhere using Pkg
# @everywhere Pkg.activate("sparseinverseproblems/")
# @everywhere using SparseInverseProblems
using SparseInverseProblems
using DelimitedFiles
using CSV
using Statistics

#parameters
sigma = 1.32#2.2
tau = 2.0*10^12
final_loss_improvement = 300.0#10.0
max_iters = 200#10000s
max_cd_iters = 30
min_allowed_separation = 2.0

img = readdlm(ARGS[1])

noise_mean = exp(mean(log.(img)))

time_fit_img() = @time fit_2048x2048_img_tiles(img, sigma, tau, final_loss_improvement, max_iters, max_cd_iters, noise_mean)

#points = fit_2048x2048_img(img, sigma, tau, final_loss_improvement, max_iters, max_cd_iters)
points_w_dup = time_fit_img()

time_remove_duplicates(points) = @time remove_duplicates(points, img, sigma, tau, noise_mean, min_allowed_separation)

points = time_remove_duplicates(points_w_dup)

CSV.write(ARGS[2], points)
