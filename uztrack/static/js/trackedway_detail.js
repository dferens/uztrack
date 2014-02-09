var myApp = angular.module('myApp', ['ui.bootstrap']);

myApp.factory('api', function($http, urls) {
    var convertHistory = function(rawHistory) {
        return {
            id: rawHistory.id,
            date: new Date(Date.parse(rawHistory.departure_date)),
            placesCount: rawHistory.last_snapshot.total_places_count,
            lastSnapshot: convertSnapshot(rawHistory.last_snapshot),
        };
    };
    var convertSnapshot = function(rawSnapshot) {
        return {
            id: rawSnapshot.id,
            date: Date.parse(rawSnapshot.made_on),
            placesCount: rawSnapshot.total_places_count,
        };
    };
    return {
        getHistories: function(trackedWayId) {
            var cfg = { params: { trackedWay: trackedWayId } };
            return $http.get(urls.histories, cfg).then(function(result) {
                return _.map(result.data, convertHistory);
            });
        },
        getSnaphots: function(dayHistoryId) {
            var cfg = { params: { history: dayHistoryId } };
            return $http.get(urls.snapshots, cfg).then(function(result) {
                return _.map(result.data, convertSnapshot);
            });
        },
    }
})
.filter('daysago', function(dateFilter) {
    return function(input) {
        if (input == null) {
            return "~";
        } else {
            var delta = Date.now() - input;
            delta = Math.round(delta / 1000 / 60 / 60 / 24);
            return delta.toString() + " days ago";
        }
    };
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
        scope: { histories: '=' },
        link: linker,
    };
})
.directive('chart', function() {
    var chartConfig = {
        chart: {
            renderTo: 'chart',
            shadow: true,
        },
        credits: { enabled: false },
        legend : {
            enabled: true,
        },
        rangeSelector: {
            buttons: [{ type: 'all', text: 'All' }],
            enabled: true,
            selected: 0,
        },
        title: { text: 'Places chart' },
        series: [],
        yAxis: {
            allowDecimals: false,
            min: 0,
            minorTickInterval: 20,
        },
    };
    return {
        restrict: 'E',
        template: '<div></div>',
        transclude: true,
        replace: true,
        controller: function($scope, api) {
            $scope.loadHistorySnaphots = function() {
                api.getSnaphots($scope.dayHistory.id).then(function(result) {
                    if ($scope.snapshotsSerie) $scope.snapshotsSerie.remove();
                    $scope.snapshotsSerie = $scope.chart.addSeries({
                        name: 'Total number of tickets',
                        data: _.map(result, function(s) {return [s.date, s.placesCount]}),
                        tooltip: { valueDecimals: 2 },
                    });
                    _.each($scope.chart.xAxis, function(axis) {
                        axis.setExtremes(_.head(result).date, new Date());
                    });
                    $scope.dayHistory.snapshots = result;
                });
            };
            $scope.chartData = [];
            $scope.chart = new Highcharts.StockChart(chartConfig);
            $scope.snapshotsSerie = null;
            $scope.$watch('dayHistory', function() {
                if ($scope.dayHistory != null) $scope.loadHistorySnaphots();
            });
        },
    };
});
