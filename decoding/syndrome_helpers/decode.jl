using SeqFISHPointDecoding
using CSV
using DataFrames
using Statistics
using Profile
using DelimitedFiles

pnts = DataFrame(CSV.File(ARGS[1]))#
pnts.hyb = UInt8.(pnts.hyb)
pnts.x = Float64.(pnts.x)
pnts.y = Float64.(pnts.y)
pnts.z = zeros(Float64, nrow(pnts))

#last semicolon is important because it makes it matrix and allows for more parity checks
H = [1 1 1 -1;]

#Search radius 
    #if smaller it takes less time
    #upper bound on how far dots are away
lat_thresh = 2

#Set z thresh 2 for default
z_thresh = 0.0
cb_name = ARGS[2]
cb = readdlm(cb_name, UInt8)

ndrops=0

pnts.dot_ID = Array(1:nrow(pnts))
ndots = nrow(pnts)

# Cost Parameters
free_dot_cost = 5.0
lat_var_factor = 112.0
z_var_factor = 0.0
lw_var_factor = 4.0
s_var_factor = 0.0
erasure_penalty = 4.0

#Simulated Annealing Parameters
converge_thresh = 100 * ndots
c_final = 1
n_chains = 100
l_chain = 20
cooling_factor = free_dot_cost * 40
# keep in mind
mip_sa_thresh = 80
cooling_timescale = exp(cooling_factor/c_final-1)/(n_chains*l_chain)
n_chains = 50

println("cost parameters: $lat_var_factor, $lw_var_factor")

params = SeqFISHPointDecoding.DecodeParams(
    lat_thresh,
    z_thresh,
    ndrops,
    mip_sa_thresh,
    n_chains,
    l_chain,
    free_dot_cost,
    cooling_factor,
    cooling_timescale,
    lat_var_factor,
    z_var_factor,
    lw_var_factor,
    s_var_factor,
    erasure_penalty,
    converge_thresh
)

mpaths = decode_syndromes!(pnts, cb, H, params)

#@profile mpaths = decode_syndromes!(pnts_cp, lat_thresh, z_thresh, code, ndrops, sa_params)
xs = [pnts.x[dots] for dots in mpaths.cpath]
ys = [pnts.y[dots] for dots in mpaths.cpath]
zs = [pnts.z[dots] for dots in mpaths.cpath]

println("decoded ", sum(pnts.decoded .!= 0), " dots of ", nrow(pnts))
println("Done")

mpaths[!,"xs"] = xs
mpaths[!,"ys"] = ys
mpaths[!,"zs"] = zs

println("decoded ", sum(pnts.decoded .!= 0), " dots of ", nrow(pnts))

save_df = pnts[:,append!(Array(1:4), Array(10:11))]

n_mpaths = nrow(mpaths)

n_neg_cntrl_mpaths = sum(mpaths.value .> 3334)
println("Number of mpaths: $n_mpaths")
println("Number of negative control mpaths: $n_neg_cntrl_mpaths")
println("lat var factor: $lat_var_factor")
println("lw var factor: $lw_var_factor")

if cb_name == "Eng2019_647.csv"
    ctrl = "no_neg_ctrl"
else
    ctrl = "w_neg_ctrl"
end

save_name = "decode_" * ctrl* "_lvf$lat_var_factor"*"_lwvf$lw_var_factor"*"dr$ndrops"*".csv"

dst_dir = ARGS[3]
CSV.write(joinpath(dst_dir, save_name), save_df)

CSV.write(joinpath(dst_dir, "mpaths_" * save_name), mpaths)
