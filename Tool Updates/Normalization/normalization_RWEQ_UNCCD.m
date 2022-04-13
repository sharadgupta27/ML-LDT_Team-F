clear;
clc;

year = 2020;

[img, R1] = readgeoraster('BagPredicted_Thar_2017.tif');
[ref, R2] = readgeoraster('SL_Thar_2017.tif');

img(img < -10) = NaN;

ref(ref == 0) = NaN;
img(isnan(ref)) = NaN;

[rows, cols, bands] = size(img);
img_vec = img(:);
ref_vec = ref(:);

ref_vec = ref_vec(~isnan(img_vec));
img_vec = img_vec(~isnan(img_vec));

ref_vec = ref_vec(~isnan(ref_vec));
img_vec = img_vec(~isnan(ref_vec));

filtered_img = img_vec(ref_vec ~= 0);
filtered_ref = ref_vec(ref_vec ~= 0);

% geotiffwrite('BagPredicted_Normalized_Thar_2016.tif', new_img, R1, 'coordRefSysCode', 32642);


figure(1); plot(filtered_img,filtered_ref,'r.');
c = polyfit(filtered_img,filtered_ref,1);

% disp(['Equation is y = ' num2str(c(1)) '*x + ' num2str(c(2))])
newStr = ['Equation is y = ' num2str(c(1)) '*x + ' num2str(c(2))];
fprintf(newStr);
fprintf('\n');
% y_est = polyval(c,filtered_img);

imgNew = c(1) .* img + c(2);

subplot(1,2,1), imshow(imgNew,[]), colorbar;
subplot(1,2,2), imshow(img,[]), colorbar;
% 
% imgNew = (ref - c(2))./ c(1);

% titleStr = ['Relation b/w UNCCD and ML based erosion for year - ' num2str(year)];
% hold on
% plot(filtered_img,y_est,'b--','LineWidth',1.5)
% legend('Data', newStr);
% title(titleStr);

fprintf('\n');
foutName = "SL_Normalized_Thar_" + num2str(year) + ".tif";
geotiffwrite(foutName, imgNew, R1, 'coordRefSysCode', 4326);