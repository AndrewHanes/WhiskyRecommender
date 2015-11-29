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
        $scope.suggest = {};
        $scope.user_reviews = {};

        $scope.setReview = function(name) {
            $http.post('/set_rate', {params: {"name": name, rating: $scope.user_reviews[name]}}).then(function(data) {
            });

        };

        $scope.ratePrompt = function(name) {
            var score = 50;
            score = window.prompt("Enter Rating (1 - 100)", score);
            if(/^\+?\d+$/.test(score)) {
                score = parseInt(score);
                if(score > 100 || score < 1) {
                    alert("Score must be between 1 and 100");
                    return;
                }
            }
            else {
                alert("Invalid Score");
                return;
            }
            $scope.user_reviews[name] = score;
        };

        $scope.clickSuggest = function(booze) {
            booze.expand = true;
            $http.get('/suggest', {params: {"name": booze.name}}).then( function(data) {
                $scope.suggest[booze.name] = data.data['favorites'];
                $(data.data['favorites']).each(function(k,v) {
                    $http.get('/get_rate?name='+ v.name).then(function(data) {
                        var rating = data.data['user_rating'];
                        if(!rating[0]) {
                            rating = 0;
                        }
                        else {
                            rating = rating[0][2];
                        }
                        var name = v.name;
                        $scope.user_reviews[name] = parseInt(rating);
                    });
                });
            });
            //$http.post('/get_rate' {})
        }

        $scope.get_review = function(name) {
            console.log(name);
            if($scope.user_reviews[name]) {
                return $scope.user_reviews[name];
            }
            return "Rate Now";
        }
    });
    $scope.orderProp = 'age';
});
