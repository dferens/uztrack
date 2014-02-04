var myApp = angular.module('myApp', ['ui.calendar']);

myApp.controller('WayDetailCtrl', function($scope, $http, urls) {
    $scope.uiConfig = {
        calendar: {
            firstDay: 1,
            editable: true,
            header:{
              left: '',
              center: 'title',
              right: 'today prev,next'
            },
        }
    };
    $scope.events = [];
    $scope.eventSources = [$scope.events];
    $scope.urls = urls;
    $scope.tracked_way_id = window.location.pathname.split('/track/')[1].slice(0, -1);

    $scope.loadEvents = function() {
        var cfg = {params: {tracked_way: $scope.tracked_way_id}};
        $http.get(urls.histories, cfg).success(function(data){
            $.each(data, function(i, history) {
                $scope.addHistory(history);
            });
        });
    };
    $scope.addHistory = function(history) {
        var departure_date = history.departure_date;
        var places_count = history.last_snapshot.total_places_count;
        $scope.events.push({
            title: places_count.toString(),
            start: departure_date,
        });
    };

    $scope.loadEvents();
});
