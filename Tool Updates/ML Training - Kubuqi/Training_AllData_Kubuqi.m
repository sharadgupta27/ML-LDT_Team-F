% clear;
% clc;

% rng(1);

[bdod, R] = readgeoraster('BDOD_SDG_clipped.tif');
ocs = readgeoraster('OCS_SDG_clipped.tif');
moisture = readgeoraster('SoilMoistureR_Kubuqi_2018_clipped.tif');
evi = readgeoraster('EVI_Kubuqi_2018_clipped.tif');
lst = readgeoraster('LST_Kubuqi_2018_clipped.tif');
pc = readgeoraster('PC_Kubuqi_2018_clipped.tif');
evaporation = readgeoraster('EvaporationR_Kubuqi_2018_clipped.tif');
precipitation = readgeoraster('PrecipitationR_Kubuqi_2018_clipped.tif');
pressure = readgeoraster('SurfacePressureR_Kubuqi_2018_clipped.tif');
windsp = readgeoraster('WindSpeedR_Kubuqi_2018_clipped.tif');
gt = readgeoraster('rivernS1_2018_Ln_NORM_clipped.tif');

[rows, cols] = size(bdod);

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

X = [bdod1 ocs1 moisture1 evi1 lst1 pc1 evaporation1 precipitation1 pressure1 windsp1 gt];
% X = [bdod ocs moisture evi lst pc evaporation precipitation pressure windsp gt];
% y = gt;

data2 = X;
% target2 = y;

% X = X(~isnan(gt),:);
% y = y(~isnan(gt));

% cv = cvpartition(size(X,1),'HoldOut',0.3);
% idx = cv.test;
% 
% Xtrain = X(~idx,:);
% Xtest  = X(idx,:);
% ytrain = y(~idx);
% ytest  = y(idx);