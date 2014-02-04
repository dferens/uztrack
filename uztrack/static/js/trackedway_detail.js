var myApp = angular.module('myApp', ['ui.calendar']);

myApp.controller('WayDetailCtrl', function($scope) {
    $scope.uiConfig = {
        calendar: {
            firstDay: 1,
            editable: true,
            header:{
              left: '',
              center: 'title',
              right: 'today prev,next'
            },
            dayClick: $scope.alertEventOnClick,
            eventDrop: $scope.alertOnDrop,
            eventResize: $scope.alertOnResize
        }
    };
    $scope.eventSources = [];
});
