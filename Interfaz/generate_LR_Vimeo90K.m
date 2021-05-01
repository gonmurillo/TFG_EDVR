function generate_LR_Vimeo90K()
%% matlab code to genetate bicubic-downsampled for Vimeo90K dataset

up_scale = 4;
mod_scale = 4;
idx = 0;	
filepaths = dir('/home/gonzalo/Escritorio/data/*.png');
for i = 1 : length(filepaths)
    [~,imname,ext] = fileparts(filepaths(i).name);
    folder_path = filepaths(i).folder;
    save_LR_folder = strrep(folder_path,'data','data_matlabLRx4');
    if ~exist(save_LR_folder, 'dir')
        mkdir(save_LR_folder);
    end
    if isempty(imname)
        disp('Ignore . folder.');
    elseif strcmp(imname, '.')
        disp('Ignore .. folder.');
    else
        idx = idx + 1;
        str_result = sprintf('%d\t%s.\n', idx, imname);
        fprintf(str_result);
        % read image
        img = imread(fullfile(folder_path, [imname, ext]));
        img = im2double(img);							# converts the image I to double precision
        % modcrop
        img = modcrop(img, mod_scale);
        % LR
        im_LR = imresize(img, 1/up_scale, 'bicubic');			# cambia el tamaño de la imágen procesada
        if exist('save_LR_folder', 'var')
            imwrite(im_LR, fullfile(save_LR_folder, [imname, '.png']));
        end
    end
end
end

%% modcrop
function img = modcrop(img, modulo)
if size(img,3) == 1 			% GRISES
    sz = size(img); 			% Obtener tamaño de imagen
    sz = sz - mod(sz, modulo);	% de altura y ancho toman el resto del módulo y restan este resto, de modo que el tamaño de la imagen se pueda dividir exactamente por módulo
    img = img(1:sz(1), 1:sz(2));	% Obtener una imagen de nuevo tamaño
else  					% COLOR
    tmpsz = size(img);
    sz = tmpsz(1:2);			# El ancho de altura de la imagen
    sz = sz - mod(sz, modulo);
    img = img(1:sz(1), 1:sz(2),:);
end
end
