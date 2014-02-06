var myApp = angular.module('myApp', []);

myApp.controller('WayDetailCtrl', function($scope, $http, urls) {
    $scope.getDate = function(date_str) {
        return new Date(Date.parse(date_str));
    };
    $scope.getTrackedWayId = function() {
        var temp = window.location.pathname;
        temp = temp.split('/track/')[1];
        return temp.slice(0, -1);
    }
    $scope.addHistory = function(history) {
        var departure_date = history.departure_date;
        var places_count = history.last_snapshot.total_places_count;
        $scope.data.push({
            date: $scope.getDate(departure_date),
            places_count: places_count,
        });
    };
    $scope.init = function() {
        $scope.data = [];
        $scope.urls = urls;
        $scope.tracked_way_id = $scope.getTrackedWayId();
        
        var cfg = {params: {tracked_way: $scope.tracked_way_id}};
        $http.get(urls.histories, cfg).success(function(data){
            $.each(data, function(i, history) {
                $scope.addHistory(history);
            });
            $scope.initHeatmap();
        });
    };
    $scope.initHeatmap = function() {
        var getStartDate = function() {
            return $scope.data[0].date;
        };
        var getLastDate = function() {
            return $scope.data[$scope.data.length - 1].date;
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
            $.each($scope.data, function(i, value) {
                seconds = value.date.getTime() / 1000;
                result[seconds] = value.places_count;
            });
            return result;
        };
        $scope.heatmap = new CalHeatMap();
        $scope.heatmap.init({
            itemSelector: '#heatmap',
            domain: 'month',
            subDomain: 'x_day',
            cellSize: 20,
            start: getStartDate(),
            range: getRange(),
            highlight: 'now',
            data: generateCalData(),
            subDomainTextFormat: '%d',
            considerMissingDataAsZero: false,
            domainLabelFormat: '%b %Y',
            verticalOrientation: true,
            legendVerticalPosition: 'bottom',
            legendHorizontalPosition: 'right',
            legendMargin: [15, 3, 0, 0],
            legendCellSize: 13,
            legendOrientation: 'horizontal',
            legend: calculateLegend(),
            label: {
                position: 'left',
                width: 80,
                offset: {x: 15, y: 80},
            },
            domainGutter: 0,
            domainDynamicDimension: true,
        });
    };

    $scope.init();
});
