// JavaScript controller for dynamic angular page
var boozeDataApp = angular.module('boozeDataApp', []);

// startFrom filter that picks a starting point in a paginated list
boozeDataApp.filter('startFrom', function () {
    return function (input, start) {
        if (input) {
            start = +start;
            return input.slice(start);
        }
        return [];
    };
});

// define the MVC controller
boozeDataApp.controller('BoozeListCtrl', function ($scope, $http) {
    $http.get('/list').success(function(data) {
        $scope.boozeTypes = data['choices'];
        // pagination vars
        $scope.pgSize = 30;

        $scope.pgTotal=function(filterLen) {
            return Math.ceil(filterLen/$scope.pgSize)
        }
        $scope.pgCur = 0;
        //search param
        $scope.searchBooze = '';
    });
    $scope.orderProp = 'age';
});
