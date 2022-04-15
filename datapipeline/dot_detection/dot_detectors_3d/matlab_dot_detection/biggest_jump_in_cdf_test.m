
vars = load('biggest_jump_vars.mat')

intensity = vars.intensity;
dots = vars.dots;
dst = 'foo/foo.mat'


[thresh_dots, thresh_intensity] = get_biggest_jump_in_cdf(intensity, dots, strictness, nbins, dst);