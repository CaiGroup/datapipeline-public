
using DelimitedFiles
using CSV
using DataFrames

sigma = 2.2
tau = 2.0*10^12
min_allowed_separation = 2.0

img = readdlm(ARGS[1])

noise_mean = exp(mean(log.(img)))

time_remove_duplicates(points) = @time remove_duplicates(points, img, sigma, tau, noise_mean, min_allowed_separation)

points_w_dup = DataFrame(CSV.File("test_results_duplicates.csv"))

points = time_remove_duplicates(points_w_dup)

CSV.write(ARGS[2], points)
