function [pos] = get_pos_from_path(tiff_path)
    [filepath,name,ext] = fileparts(tiff_path);
    n_ome = strsplit(name, 'Pos');
    str_pos = strsplit(n_ome{2}, '.ome');
    pos = str2double(str_pos{1});
    
end
