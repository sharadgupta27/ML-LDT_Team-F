rng(1);

data = [data1;data2];
[nrows, ncols] = size(data);

for i = 1:ncols
    temp = data(:,i);
    temp(temp == min(temp)) = NaN;
    dataNew(:,i) = temp;
end

temp = dataNew(:,11);
temp(temp == 0) = NaN;
dataNew(:,11) = temp;

dataNew(any(isnan(dataNew),2),:) = [];

% y = [target1;target2];
% X = X(~isnan(y),:);
% y = y(~isnan(y));

% cv = cvpartition(size(X,1),'HoldOut',0.2);
% idx = cv.test;
% 
% Xtrain = X(~idx,:);
% Xtest  = X(idx,:);
% ytrain = y(~idx);
% ytest  = y(idx);