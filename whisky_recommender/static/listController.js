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
boozeDataApp.controller('BoozeListCtrl', function ($scope, $http, $q) {
    $http.get('/list').success(function(data) {
        $scope.boozeTypes = data['choices'];
        // pagination vars/functs
        $scope.pgSize = 10;
        $scope.pgTotal = function(filterLen) {
            return Math.ceil(filterLen/$scope.pgSize);
        }
        $scope.pgCur = 0;
        //search param
        $scope.searchBooze = '';
        //handle dynamic recomendations loading
        $scope.suggest = {}
        $scope.clickSuggest = function(booze) {
            booze.expand = true;
            $http.get('/suggest', {params: {"name": booze.name}}).then( function(data) {
                $scope.suggest[booze.name] = data.data['favorites'];
            })
        }
    });
    $scope.orderProp = 'age';
});
