clear;
clc;

% rng(1);

[bdod, R] = readgeoraster('BDOD_SDG.tif');
ocs = readgeoraster('OCS_SDG.tif');
moisture = readgeoraster('SoilMoistureR_Thar_2016.tif');
evi = readgeoraster('EVI_Thar_2016.tif');
lst = readgeoraster('LST_Thar_2016.tif');
pc = readgeoraster('PC_Thar_2016.tif');
evaporation = readgeoraster('EvaporationR_Thar_2016.tif');
precipitation = readgeoraster('PrecipitationR_Thar_2016.tif');
pressure = readgeoraster('SurfacePressureR_Thar_2016.tif');
windsp = readgeoraster('WindSpeedR_Thar_2016.tif');
gt = readgeoraster('GT_Erosion_2016.tif');
rweq = readgeoraster('SL_Thar_2016_clipped.tif');

[rows, cols] = size(bdod);

% moisture = imresize(moisture, [rows+50, cols+50], 'lanczos3');
% evaporation = imresize(evaporation, [rows+50, cols+50], 'lanczos3');
% precipitation = imresize(precipitation, [rows+50, cols+50], 'lanczos3');
% pressure = imresize(pressure, [rows+50, cols*50], 'lanczos3');
% windsp = imresize(windsp, [rows+50, cols+50], 'lanczos3');
% winddir = imresize(winddir, [rows+50, cols+50], 'lanczos3');

% moisture = imresize(moisture, [rows, cols], 'lanczos3');
% evaporation = imresize(evaporation, [rows, cols], 'lanczos3');
% precipitation = imresize(precipitation, [rows, cols], 'lanczos3');
% pressure = imresize(pressure, [rows, cols], 'lanczos3');
% windsp = imresize(windsp, [rows, cols], 'lanczos3');
% winddir = imresize(winddir, [rows, cols], 'lanczos3');

% moisture = medfilt2(moisture, [50 50]);
% evaporation = medfilt2(evaporation, [50 50]);
% precipitation = medfilt2(precipitation, [50 50]);
% pressure = medfilt2(pressure, [50 50]);
% windsp = medfilt2(windsp, [50 50]);
% winddir = medfilt2(winddir, [50 50]);

% moisture = imresize(moisture, [rows, cols], 'lanczos3');
% evaporation = imresize(evaporation, [rows, cols], 'lanczos3');
% precipitation = imresize(precipitation, [rows, cols], 'lanczos3');
% pressure = imresize(pressure, [rows, cols], 'lanczos3');
% windsp = imresize(windsp, [rows, cols], 'lanczos3');
% winddir = imresize(winddir, [rows, cols], 'lanczos3');

bdod = double(bdod(:));
ocs = double(ocs(:));
moisture = double(moisture(:));
evi = double(evi(:));
lst = double(lst(:));
pc = double(pc(:));
evaporation = double(evaporation(:));
precipitation = double(precipitation(:));
pressure = double(pressure(:));
windsp = double(windsp(:));
gt = double(gt(:));
rweq = double(rweq(:));

bdod1 = (bdod - min(bdod(:)))./(max(bdod(:)) - min(bdod(:)));
ocs1 = (ocs - min(ocs(:)))./(max(ocs(:)) - min(ocs(:)));
moisture1 = (moisture - min(moisture(:)))./(max(moisture(:)) - min(moisture(:)));
evi1 = (evi - min(evi(:)))./(max(evi(:)) - min(evi(:)));
lst1 = (lst - min(lst(:)))./(max(lst(:)) - min(lst(:)));
pc1 = (pc - min(pc(:)))./(max(pc(:)) - min(pc(:)));
evaporation1 = (evaporation - min(evaporation(:)))./(max(evaporation(:)) - min(evaporation(:)));
precipitation1 = (precipitation - min(precipitation(:)))./(max(precipitation(:)) - min(precipitation(:)));
pressure1 = (pressure - min(pressure(:)))./(max(pressure(:)) - min(pressure(:)));
windsp1 = (windsp - min(windsp(:)))./(max(windsp(:)) - min(windsp(:)));

X = [bdod1 ocs1 moisture1 evi1 lst1 pc1 evaporation1 precipitation1 pressure1 windsp1];
% y = gt; % Train using InSAR GT
y = rweq; % Train using RWEQ

% for i = 1:10
%     temp = X(:,i);
%     temp(temp == min(temp)) = NaN;
%     X(:,i) = temp;
% end
% 
% temp = dataNew(:,11);
y(y == min(y)) = NaN;
% dataNew(:,11) = temp;
% 
% dataNew(any(isnan(dataNew),2),:) = [];

X = X(~isnan(y),:);
y = y(~isnan(y));

% cv = cvpartition(size(X,1),'HoldOut',0.3);
% idx = cv.test;
% 
% Xtrain = X(~idx,:);
% Xtest  = X(idx,:);
% ytrain = y(~idx);
% ytest  = y(idx);