var myApp = angular.module('myApp', []);

myApp.factory('api', function($http, urls) {
    return {
        getHistories: function(trackedWayId) {
            var cfg = { params: { trackedWay: trackedWayId } };
            return $http.get(urls.histories, cfg).then(function(result) {
                return _.map(result.data, function(history) {
                    return {
                        id: history.id,
                        date: new Date(Date.parse(history.departure_date)),
                        placesCount: history.last_snapshot.total_places_count,
                    };
                });
            });
        },
        getSnaphots: function(dayHistoryId) {
            var cfg = { params: { history: dayHistoryId } };
            return $http.get(urls.snapshots, cfg).then(function(result) {
                return _.map(result.data, function(snapshot) {
                    return {
                        id: snapshot.id,
                        date: Date.parse(snapshot.made_on),
                        placesCount: snapshot.total_places_count,
                    };
                });
            });
        },
    }
})
.controller('WayDetailCtrl', function($scope, api) {
    $scope.getTrackedWayId = function() {
        var temp = window.location.pathname;
        temp = temp.split('/track/')[1];
        return temp.slice(0, -1);
    };
    $scope.selectHistory = function(history) {
        $scope.dayHistory = history;
    };
    $scope.init = function() {
        $scope.trackedWayId = $scope.getTrackedWayId();
        api.getHistories($scope.trackedWayId).then(function(data) {
            $scope.dayHistories = data;
        });
    };

    $scope.init();
})
.directive('heatmap', function() {
    var calMapConfig = {
        cellSize: 20,
        considerMissingDataAsZero: false,
        domain: 'month',
        domainDynamicDimension: true,
        domainGutter: 0,
        domainLabelFormat: '%b %Y',
        highlight: 'now',
        itemName: 'place',
        itemSelector: '#heatmap',
        label: { position: 'left',
                 width: 80,
                 offset: { x: 15, y: 80 } },
        legend: [50, 100, 250, 500],
        legendCellSize: 13,
        legendHorizontalPosition: 'right',
        legendMargin: [15, 3, 0, 0],
        legendOrientation: 'horizontal',
        legendVerticalPosition: 'bottom',
        subDomain: 'x_day',
        subDomainTextFormat: '%d',
        verticalOrientation: true,
    };
    var linker = function(scope, element, attrs) {
        scope.$watch('histories', function() {
            var histories = scope.histories;
            if ((histories != null) && (histories.length > 0)) {
                var startDate = histories[0].date;
                var lastDate = histories[_.size(histories) - 1].date;
                
                calMapConfig.start = startDate;
                calMapConfig.range = lastDate.getMonth() - startDate.getMonth() + 1;
                calMapConfig.data = _.reduce(histories, function(res, h) {
                    res[h.date.getTime() / 1000] = h.placesCount;
                    return res;
                }, {});
                calMapConfig.onClick = function(date, nb) {
                    if (nb !== null) {
                        scope.$apply(function() {
                            scope.$parent.selectHistory(_.find(histories, function(h) {
                                return h.date.toDateString() == date.toDateString();
                            }));
                        });
                    }
                };

                scope.heatmap = new CalHeatMap();
                scope.heatmap.init(calMapConfig);
            }
        });
    };
    return {
        restrict: 'E',
        template: '<div></div>',
        transclude: true,
        replace: true,
        scope: { histories: '=histories' },
        link: linker,
    };
})
.directive('chart', function() {
    var chartConfig = {
        chart: {
            renderTo: 'chart',
            shadow: true,
        },
        legend : {
            enabled: true,
        },
        rangeSelector: { enabled: false },
        title: { text: 'Places chart' },
        series: [],
    };
    return {
        restrict: 'E',
        template: '<div></div>',
        transclude: true,
        replace: true,
        controller: function($scope, api) {
            $scope.loadHistorySnaphots = function() {
                api.getSnaphots($scope.dayHistory.id).then(function(result) {
                    while($scope.chart.series.length > 0) $scope.chart.series[0].remove(true);
                    $scope.chart.addSeries({
                        name: 'Total number of tickets',
                        data: _.map(result, function(s) {return [s.date, s.placesCount]}),
                        tooltip: { valueDecimals: 2 },
                    });
                });
            };
            $scope.initChart = function() {
                $scope.chart = new Highcharts.StockChart(chartConfig);
            };
            $scope.chartData = [];
            $scope.initChart();
            $scope.$watch('dayHistory', function() {
                if ($scope.dayHistory != null) $scope.loadHistorySnaphots();
            });
        },
    };
});
