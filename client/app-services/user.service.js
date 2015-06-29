(function () {
  'use strict';

  angular
    .module('app')
    .factory('UserService', UserService);

  UserService.$inject = ['$http', 'API_URL'];
  function UserService($http, API_URL) {
    var service = {};

    service.GetAll = GetAll;
    service.GetById = GetById;
    service.GetByUsername = GetByUsername;
    service.Create = Create;
    service.Update = Update;
    service.Delete = Delete;

    return service;

    function GetAll() {
      return $http.get(
        API_URL + '/users'
      ).then(
        handleSuccess,
        handleError('Error getting all users')
      );
    }

    function GetById(id) {
      return $http.get(
        API_URL + '/users/' + id
      ).then(
        handleSuccess,
        handleError('Error getting user by id')
      );
    }

    function GetByUsername(username) {
      return $http.get(
        API_URL + '/users/' + username
      ).then(
        handleSuccess,
        handleError('Error getting user by username')
      );
    }

    function Create(user) {
      return $http.post(
        API_URL + '/users',
        user,
        { headers: { 'content-type': 'application/json'} }
      ).then(
        handleSuccess,
        handleError('Error creating user')
      );
    }

    function Update(user) {
      return $http.put(
        API_URL + '/users/' + user.id, user
      ).then(
        handleSuccess,
        handleError('Error updating user')
      );
    }

    function Delete(id) {
      return $http.delete(
        API_URL + '/users/' + id
      ).then(
        handleSuccess,
        handleError('Error deleting user')
      );
    }

    // private functions

    function handleSuccess(data) {
      data.success = true;
      return data;
    }

    function handleError(error) {
      // TODO(eso) why necessary to return function instead of dict?
      // return { success: false, message: error }; // this doesn't work
      return function () {
        return { success: false, message: error };
      };
    }
  }

})();
