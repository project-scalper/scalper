#!/usr/bin/node

var token = window.localStorage.getItem("session_id")

class Requests {
    constructor() {
        this.api = "https://scalper-cyk6.onrender.com/bot"
    }

    get(endpoint) {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'GET',
                url: this.api + endpoint,
                contentType: 'application/json',
                headers: {
                    'Authorization': "scalper " + token
                },
                crossDomain: true,
                dataType: 'json',
                success: function(data) {
                    resolve(data);
                },
                error: function(err) {
                    reject(err);
                }
            })
        })
    }

    post(endpoint, payload) {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'POST',
                url: this.api + endpoint,
                data: payload,
                contentType: 'application/json',
                headers: {
                    'Authorization': "scalper " + token
                },
                dataType: 'json',
                success: function(data) {
                    resolve(data);
                },
                error: function(err) {
                    reject(err);
                }
            })
        })
    }

    put(endpoint, payload) {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'PUT',
                url: this.api + endpoint,
                data: payload,
                contentType: 'application/json',
                headers: {
                    'Authorization': "scalper " + token
                },
                dataType: 'json',
                success: function(data) {
                    resolve(data);
                },
                error: function(err) {
                    reject(err);
                }
            })
        })
    }

    put(endpoint, payload) {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'PUT',
                url: this.api + endpoint,
                data: payload,
                contentType: 'application/json',
                headers: {
                    'Authorization': "scalper " + token
                },
                dataType: 'json',
                success: function(data) {
                    resolve(data);
                },
                error: function(err) {
                    reject(err);
                }
            })
        })
    }

    destroy(endpoint, payload=null) {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'DELETE',
                url: this.api + endpoint,
                contentType: 'application/json',
                headers: {
                    'Authorization': "scalper " + token
                },
                crossDomain: true,
                dataType: 'json',
                success: function(data) {
                    resolve(data);
                },
                error: function(err) {
                    reject(err);
                }
            })
        })
    }

    signin(email, password) {
        var payload = JSON.stringify({
            email,
            password,
        })
        return new Promise((res, rej) => {
            this.post('/auth/login', payload)
            .then((user) => {
                res(user);
            }).catch((err) => {
                rej(err)
            })
        })
    }

    signout() {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'DELETE',
                url: this.api + '/logout',
                contentType: 'application/json',
                headers: {
                    'Authorization': "scalper " + token
                },
                dataType: 'json',
                success: function(data) {
                    resolve(data);
                },
                error: function(err) {
                    reject(err);
                }
            })
        })
    }
}

request = new Requests();