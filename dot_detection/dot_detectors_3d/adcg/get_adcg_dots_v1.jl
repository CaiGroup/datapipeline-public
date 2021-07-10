ncores = 20

using Distributed
addprocs(ncores)
@everywhere using Pkg
@everywhere Pkg.activate("sparseinverseproblems/")
@everywhere using SparseInverseProblems
using DelimitedFiles
using CSV
using Statistics

#parameters
sigma = 2.2
tau = 2.0*10^12
final_loss_improvement = 2000.0#10.0
max_iters = 200#10000
max_cd_iters = 10
min_allowed_separation = 2.0

img = readdlm(ARGS[1])

noise_mean = exp(mean(log.(img)))

time_fit_img() = @time fit_2048x2048_img_tiles(img, sigma, tau, final_loss_improvement, max_iters, max_cd_iters, noise_mean)

#points = fit_2048x2048_img(img, sigma, tau, final_loss_improvement, max_iters, max_cd_iters)
points_w_dup = time_fit_img()

CSV.write(ARGS[2], points_w_dup)
println("done")
