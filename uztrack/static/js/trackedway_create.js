var app = angular.module('TrackedWayApp', ['ui.select2', 'ui-rangeSlider'])
.factory('hoursFormatter', function() {
  return function(input) {
    var prefix = (input < 10) ? '0' : '';
    return prefix + input.toString() + ':00';
  };
})
.filter('hours', function(hoursFormatter) {return hoursFormatter})
.factory('stationsLookup', function($q) {
  var BASE_URL = 'http://booking.uz.gov.ua/purchase/station/';
  return function(query) {
    var deferred = $q.defer();
    $.ajax({
      url: BASE_URL + query + '/',
      type: 'GET',
      dataType: 'jsonp',
      success: function(data) {
        deferred.resolve(_.map(data.value, function(obj) {
          return {id: obj.station_id, text: obj.title};
        }));
      }
    });
    return deferred.promise;
  };
})
.controller('CreateCtrl', function($scope, $http, $window, stationsLookup, hoursFormatter) {
  $scope.getSelectedDays = function() {
    return _.filter($scope.days, function(day) {return day.enabled;});
  };
  $scope.isValid = function() {
    return (
      $scope.station_from && 
      $scope.station_to && (
        ($scope.is_repeated && ($scope.getSelectedDays().length > 0)) ||
        (!($scope.is_repeated) && $scope.departure_date)
      )
    );
  };
  $scope.submit = function() {
    var config = {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    };
    var data = {
      csrfmiddlewaretoken: $scope.csrftoken,
      station_name_from: $scope.station_from.text,
      station_name_to: $scope.station_to.text,
      is_repeated: $scope.is_repeated,
    };

    var filters = ['dep_max_time', 'dep_min_time',
                   'arr_max_time', 'arr_min_time'];
    _.each(filters, function(filter) {
      var value = $scope[filter];

      if ((value > 0) && (value < 24))
        data[filter] = hoursFormatter(value);
    });

    if ($scope.is_repeated) {
      // Original ``$.param`` will make
      //   ... &days[]=Monday&days[]=Tuesday ...
      // instead of
      //   ... &days=Monday&days=Tuesday ...
      var encodedData = _.reduce($scope.days, function(memo, day) {
        return memo + (day.enabled? ('&days=' + day.name) : '');
      }, $.param(data));
    } else {
      data.departure_date = $scope.departure_date.format('MM/DD/YYYY');
      var encodedData = $.param(data);
    }

    $http.post('#', encodedData, config).success(function(data, code, headers) {
      if (data.errors) {
        $scope.errors = data.errors;
      } else {
        $window.location.pathname = data.redirect;
      }
    });
  };

  var select2Options = {
    station: {
      placeholder: 'Search for station',
      query: function (query) {
        if (query.term) {
          stationsLookup(query.term).then(function(result) {
            query.callback({results: result});
          });
        }
      }
    }
  };

  $scope.csrftoken = getCSRFToken();
  $scope.stationFromSelectOptions = angular.copy(select2Options.station);
  $scope.stationToSelectOptions = angular.copy(select2Options.station);
  $scope.station_from = $scope.station_to = null;
  $scope.is_repeated = true;
  $scope.days = _.map(_.zip(moment.weekdays(), moment.weekdaysShort()), function(pair) {
    return {name: pair[0],  // Monday
            title: pair[1], // Mn
            enabled: false};
  });
  // Making monday as first day of the week
  $scope.days.push($scope.days.shift());
  $scope.departure_date = null;
  $scope.dep_min_time = $scope.arr_min_time = 0;
  $scope.dep_max_time = $scope.arr_max_time = 24;
})
.directive('myDatepicker', function() {
  return {
    restrict: 'A',
    link: function(scope, element, attrs) {
      $(element).datetimepicker({
        pickTime: false,
        showToday: true,
      });
      $(element).on('dp.change', function(e) {
        var date = $(element).data().DateTimePicker.getDate();
        scope.$apply(function() {
          scope.departure_date = date;
        });
      });
    }
  };
});
