using Distributed
addprocs(snakemake.threads)
@everywhere using Pkg
@everywhere Pkg.activate("sparseinverseproblems/")
@everywhere using SparseInverseProblems
using DelimitedFiles
using CSV
using Statistics

#parameters
sigma_lb = snakemake.params["sigma_lb"]
sigma_ub = snakemake.params["sigma_ub"]
#sigma = 2.2
tau = 2.0*10^12
final_loss_improvement = snakemake.params["final_loss_improvement"]
min_weight = snakemake.params["min_weight"]
#final_loss_improvement = 2000.0#500.0#10.0
max_iters = snakemake.params["max_iters"]
#max_iters = 200#10000
#max_cd_iters = 10
max_cd_iters = snakemake.params["max_cd_iters"]

#file = "HybCycle_0"

img = readdlm(snakemake.input[1])#"dlm_ims/"*file*".txt")

#mean_int = 0.0#mean(img)
threshold = exp(mean(log.(img)))

#points = fit_2048x2048_img(img, sigma, tau, final_loss_improvement, max_iters, max_cd_iters)
points = fit_2048x2048_img_tiles(img, sigma_lb, sigma_ub, tau, final_loss_improvement, min_weight, max_iters, max_cd_iters, threshold)#mean_int)


#CSV.write("fit_dots/"*file*".csv", points)
CSV.write(snakemake.output[1], points)

# https://gitlab.com/jawhitect/sparseinverseproblems
