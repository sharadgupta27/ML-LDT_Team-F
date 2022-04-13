clear;
clc;

year = 2017
fname = "SL_Thar_StackNew_" + num2str(year) + ".tif";
imgs = readgeoraster(fname);

img = imgs(:,:,1);
ref = imgs(:,:,2);
% im11 = img; 
% im22 = ref; 

img(img < 10^-2) = NaN;
ref(ref < 10^-5) = NaN;

% [img, R1] = readgeoraster('BagPredicted_Thar_2017.tif');
% [ref, R2] = readgeoraster('SL_Thar_2017.tif');

% imgs(imgs < 0.05) = NaN; 

[rows, cols, bands] = size(imgs);
img_vec = img(:);
ref_vec = ref(:);

ref_vec = ref_vec(~isnan(img_vec));
img_vec = img_vec(~isnan(img_vec));

filtered_img = img_vec(ref_vec ~= 0);
filtered_ref = ref_vec(ref_vec ~= 0);

r_max = max(filtered_ref);
r_min = min(filtered_ref);

filtered_img = filtered_img(~isnan(filtered_ref));
filtered_ref = filtered_ref(~isnan(filtered_ref));
filtered_img = filtered_img(~isnan(filtered_img));
filtered_ref = filtered_ref(~isnan(filtered_img));
 
i_max = mean(filtered_img) + (3.5 * std(filtered_img));
i_min = mean(filtered_img) - (3.5 * std(filtered_img));

gain = (r_max - r_min)/(i_max - i_min);
imgNew = gain.*(img - i_min);

% geotiffwrite('BagPredicted_Thar_Normalized_2017.tif', new_img, R1, 'coordRefSysCode', 32643);
