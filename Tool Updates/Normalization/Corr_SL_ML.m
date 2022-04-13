% clear;
% clc;

year = 2020
fname = "SL_Thar_Stack_RWEQ_SDS_" + num2str(year) + ".tif";
[img, R] = readgeoraster(fname);
[row, col] = size(img);

im1 = img(:,:,1);
im2 = img(:,:,2);
im11 = im1;
% im22 = im2;
im1 = im1(:);
im2 = im2(:);

im1(im1 < 10^-2) = NaN;
im2(im2 < 10^-5) = NaN;

im1 = im1(im2 ~= 0);
im2 = im2(im2 ~= 0);
im1 = im1(im1 ~= 0);
im2 = im2(im1 ~= 0);

im1 = im1(~isnan(im2));
im2 = im2(~isnan(im2));
im1 = im1(~isnan(im1));
im2 = im2(~isnan(im1));

% figure(1); hold on
% subplot(1,2,1), imshow(img(:,:,1),[])
% subplot(1,2,2), imshow(img(:,:,2),[])
% hold off

% figure(2); plot(im1,im2,'r.');
c = polyfit(im1,im2,1);
imgNew = c(1) .* im11 + c(2);
imgNew(isnan(im22)) = NaN;

figure(3), imagesc(imgNew), colorbar
foutName = "SL_Normalized_TharByRWEQ-SDS_" + num2str(year) + ".tif";
geotiffwrite(foutName, imgNew, R, 'coordRefSysCode', 32642);