[img, R1] = readgeoraster('SL_Norm_Thar_2020.tif');
[ref, R2] = readgeoraster('UNCCD_SDS_Thar_Annual.tif');

[rows, cols, bands] = size(img);
img_vec = img(:);
ref_vec = ref(:);

ref_vec = ref_vec(~isnan(img_vec));
img_vec = img_vec(~isnan(img_vec));

filtered_img = img_vec(ref_vec ~= 0);
filtered_ref = ref_vec(ref_vec ~= 0);

r_max = max(filtered_ref);
r_min = min(filtered_ref);

i_max = mean(filtered_img) + (3.5 * std(filtered_img));
i_min = mean(filtered_img) - (3.5 * std(filtered_img));

gain = (r_max - r_min)/(i_max - i_min);
new_img = gain.*(img - i_min);

geotiffwrite('SL_NormUNCCD_Thar_2020.tif', new_img, R1, 'coordRefSysCode', 4326);
