from load_tiff import tiffy

src = '/groups/CaiLab/personal/michalp/raw/michal_1/HybCycle_10/MMStack_Pos14.ome.tif'

tiff = tiffy.load(src)

print(tiff.shape)
