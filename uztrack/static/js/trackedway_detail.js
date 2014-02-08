var myApp = angular.module('myApp', []);

myApp.controller('WayDetailCtrl', function($scope, $http, $q, urls) {
    $scope.getDate = function(date_str) {
        return new Date(Date.parse(date_str));
    };
    $scope.getTrackedWayId = function() {
        var temp = window.location.pathname;
        temp = temp.split('/track/')[1];
        return temp.slice(0, -1);
    };
    $scope.selectHistory = function(history) {
        $scope.$apply(function() {
            $scope.dayHistory = history;
        });
    };
    $scope.init = function() {
        $scope.urls = urls;
        $scope.trackedWayId = $scope.getTrackedWayId();
        $scope.dayHistories = $scope._loadDayHistories()

        $scope.dayHistories.then(function(data) {
            $scope.dayHistories = data;
            $scope._initHeatmap();
        });
    };
    $scope._loadDayHistories = function() {
        var deferred = $q.defer();
        var cfg = {params: {tracked_way: $scope.trackedWayId}};
        $http.get(urls.histories, cfg).success(function(data){
            var result = [];
            $.each(data, function(i, history) {
                result.push({
                    id: history.id,
                    date: $scope.getDate(history.departure_date),
                    placesCount: history.last_snapshot.total_places_count,
                });
            });
            deferred.resolve(result);
        });
        return deferred.promise;
    };
    $scope._initHeatmap = function() {
        var getStartDate = function() {
            return $scope.dayHistories[0].date;
        };
        var getLastDate = function() {
            return $scope.dayHistories[$scope.dayHistories.length - 1].date;
        }
        var getRange = function() {
            var lastMonth = getLastDate().getMonth() + 1;
            var firstMonth = getStartDate().getMonth();
            return lastMonth - firstMonth;
        };
        var calculateLegend = function() {
            return [50, 100, 250, 500]
        };
        var generateCalData = function() {
            var result = {}, seconds;
            console.log($scope.dayHistories);
            $.each($scope.dayHistories, function(i, value) {                
                seconds = value.date.getTime() / 1000;
                result[seconds] = value.placesCount;
            });
            return result;
        };
        $scope.heatmap = new CalHeatMap();
        $scope.heatmap.init({
            cellSize: 20,
            considerMissingDataAsZero: false,
            data: generateCalData(),
            domain: 'month',
            domainDynamicDimension: true,
            domainGutter: 0,
            domainLabelFormat: '%b %Y',
            highlight: 'now',
            itemName: 'place',
            itemSelector: '#heatmap',
            label: {
                position: 'left',
                width: 80,
                offset: {x: 15, y: 80},
            },
            legend: calculateLegend(),
            legendCellSize: 13,
            legendHorizontalPosition: 'right',
            legendMargin: [15, 3, 0, 0],
            legendOrientation: 'horizontal',
            legendVerticalPosition: 'bottom',
            onClick: function(date, nb) {
                if (nb !== null) {
                    $.each($scope.dayHistories, function(i, history) {
                        if (history.date.toDateString() == date.toDateString()) {
                            return $scope.selectHistory(history);
                        }
                    });
                }
            },
            range: getRange(),
            start: getStartDate(),
            subDomain: 'x_day',
            subDomainTextFormat: '%d',
            verticalOrientation: true,
        });
    };

    $scope.init();
});
