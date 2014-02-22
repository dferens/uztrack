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
            var cfg = { params: { tracked_way: trackedWayId } };
            return $http.get(urls.histories, cfg).then(function(result) {
                var validator = function(history) { return history.last_snapshot != null; }
                return _.map(_.filter(result.data, validator), convertHistory);
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
.filter('ago', function(dateFilter) {
    var _ago = function(delta) {        
        var days = Math.round(delta / 1000 / 60 / 60 / 24);
        if (days > 0) return [days, 'days'];
        var hours = Math.round(delta / 1000 / 60 / 60);
        if (hours > 0) return [hours, 'hours'];
        var minutes = Math.round(delta / 1000 / 60);
        if (minutes > 0) return [minutes, 'minutes'];
        var seconds = Math.round(delta / 1000);
        if (seconds > 0) return [seconds, 'seconds'];
    };
    return function(input) {
        if (input == null) {
            return "~";
        } else {
            var delta = Date.now() - input;
            if (Math.round(delta) == 0) return 'just now';
            return '{0} {1} ago'.format(_ago(delta))
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
