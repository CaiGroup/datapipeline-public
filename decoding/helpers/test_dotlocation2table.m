
foo_loaded = load('/home/nrezaee/test_cronjob_multi_dot/foo.mat')
dotlocations = foo_loaded.dotlocations
barcodekeyNames = foo_loaded.barcodekeyNames
minseeds = foo_loaded.minNumSeeds
dotlocations2table(dotlocations, barcodekeyNames, minseeds)