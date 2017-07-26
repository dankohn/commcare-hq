var url = hqImport('hqwebapp/js/urllib.js').reverse;

window.angular.module('icdsApp').factory('demographicsService', ['$http', function($http) {
    return {
        getRegisteredHouseholdData: function(step, params) {
            var get_url = url('registered_household', step);
            return  $http({
                method: "GET",
                url: get_url,
                params: params,
            });
        },
    };
}]);