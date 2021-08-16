using Pkg
Pkg.activate("decode_env")

using SeqFISHSyndromeDecoding
using CSV
using DataFrames
using Statistics
using DelimitedFiles


#pnts =  DataFrame(CSV.File("aligned_dots_mw_600_ch_0_rbr_3.3.csv")) # DataFrame(CSV.File(ARGS[1]))#
pnts =  DataFrame(CSV.File(ARGS[1]))#
pnts.hyb = UInt8.(pnts.hyb)
pnts.x = Float64.(pnts.x)
pnts.y = Float64.(pnts.y)
pnts.z = zeros(Float64, nrow(pnts))

#H = [1 1 1 -1;]


#cb_name = "E2019_cb_all_control_ch_0.txt" #ARGS[2]
cb_name = ARGS[2]
cb = readdlm(cb_name, UInt8)


pnts.dot_ID = Array(1:nrow(pnts))
ndots = nrow(pnts)

# Cost Parameters
#lat_var_factor = 180 #parse(Float64, ARGS[4])
#z_var_factor = 0 #parse(Float64, ARGS[5])
#lw_var_factor = 8 #parse(Float64, ARGS[6])

lat_var_factor = parse(Float64, ARGS[4])
z_var_factor = parse(Float64, ARGS[5])
lw_var_factor = parse(Float64, ARGS[6])

#Hpath = "H.csv", #ARGS[7]
#H = readdlm("H.csv", ',', Int64)
H = readdlm(ARGS[7], ',', Int64)

println("cost parameters: $lat_var_factor, $lw_var_factor")
params = DecodeParams()

lat_thresh = sqrt(params.free_dot_cost*size(H)[2]/lat_var_factor)*3
z_thresh = sqrt(params.free_dot_cost*size(H)[2]/z_var_factor)*3

set_xy_search_radius(params, lat_thresh)
set_z_search_radius(params, z_thresh)
set_n_allowed_drops(params, 0)
set_lat_var_cost_coeff(params, lat_var_factor)
set_z_var_cost_coeff(params, z_var_factor)
set_lw_var_cost_coeff(params, lw_var_factor)

mpaths = decode_syndromes!(pnts, cb, H, params)
println("finished decoding")
xs = [pnts.x[dots] for dots in mpaths.cpath]
ys = [pnts.y[dots] for dots in mpaths.cpath]
zs = [pnts.z[dots] for dots in mpaths.cpath]


mpaths[!,"xs"] = xs
mpaths[!,"ys"] = ys
mpaths[!,"zs"] = zs

save_df = pnts#[:,append!(Array(1:4), Array(11:11))]

#save_df = pnts[:,append!(Array(1:4), Array(10:11))]

n_mpaths = nrow(mpaths)

save_name = "decode_lvf"*string(lat_var_factor)*"_zvf"*string(z_var_factor)*"_lwvf"*string(lw_var_factor)*".csv"
println(save_name)


#dst_dir = "output"#ARGS[3]
dst_dir = ARGS[3]
println(joinpath(dst_dir, "mpaths_" * save_name))
CSV.write(joinpath(dst_dir, "mpaths_" * save_name), mpaths)
CSV.write(joinpath(dst_dir, save_name), save_df)
