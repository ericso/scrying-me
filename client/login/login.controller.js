(function () {
  'use strict';

  angular
    .module('app')
    .controller('LoginController', LoginController);

  LoginController.$inject = ['$location', 'AuthenticationService', 'FlashService'];
  function LoginController($location, AuthenticationService, FlashService) {
    var vm = this;

    vm.login = login;

    (function initController() {
      // reset login status
      AuthenticationService.ClearCredentials();
    })();

    function login() {
      vm.dataLoading = true;
      AuthenticationService.Login(vm.username, vm.password, function (response) {
        console.log(response);
        if (response.success) {
          AuthenticationService.SetCredentials(vm.username, vm.password);
          FlashService.Success(
            "Welcome, " + vm.username + "!",
            true
          );
          $location.path('/');
        } else {
          console.log("not successfully logged in");
          FlashService.Error(response.message);
          vm.dataLoading = false;
        }
      });
    };
  }

})();
