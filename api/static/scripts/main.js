#!/usr/bin/node

async function loadBot(bot_id) {
    return request.get('/bot/' + bot_id)
    .then((bot) => {
        $("#daily-pnl").text(bot.today_pnl.toFixed(2))
        $("#current-balance").text("$" + bot.balance.toFixed(2))
        $("#performance-list").html('')
        if (bot.active === true) {
            $("#suspend").html('<i class="fa fa-spinner fa-spin" id="loader2"></i>Suspend bot')
        } else if (bot.active === false) {
            $("#suspend").html('<i class="fa fa-spinner fa-spin" id="loader2"></i>Resume bot')
        }
        for (var item of bot.daily_pnl) {
            $("#performance-list").prepend(
                `<li>${item.date}: ${item.msg.toFixed(2)}\n</li>`
            )
        }
        $("#todays-trades").html('')
        for (var item of bot.trades) {
            var tm = item.date.split(', ')[1]
            $("#todays-trades").prepend(
                `<li>${tm}: ${item.msg}\n</li>`
            )
        }
        var loader = document.getElementById('loader');
        if (loader != null) {
            loader.style.display = "none";
        }
    })
    .catch((err) => {
        console.log(err);
        var loader = document.getElementById('loader');
        if (loader != null) {
            loader.style.display = "none";
        }
        if (err.status === 401) {
            alert("Your session has expired, please sign in again")
            window.location.href = "login2.html"
        } else {
            alert("Error fetching bot");
        }
    })
}

function getProfile() {
    return request.get('/user/me')
    .then((res) => {
        // console.log(res)
        $("#greeting").text(`Hello ${res.username}`)
        $("#capital").text("$" + res.capital)
        window.localStorage.setItem("bot_id", res.bot_id)
        return loadBot(res.bot_id)
    })
    .catch((err) => {
        if (err.status === 401) {
            alert("Your session has expired, please log in again to continue");
            window.location.href = 'login2.html'
        } else {
            alert("There was an error getting user info")
            console.log(err);
        }
    })
}

function refreshPage() {
    $("#reload").on('click', () => {
        var loader = document.getElementById("loader")
        loader.style.display = 'block'

        bot_id = window.localStorage.getItem("bot_id");
        return loadBot(bot_id);
        
    })
}

function suspendBot() {
    $("#suspend").on('click', () => {
        var loader = document.getElementById("loader2")
        loader.style.display = 'block'
        if ($("#suspend").text() === "Suspend bot") {
            conf = window.confirm("Are you sure you want to suspend the bot?")
            if (conf == false) {
                var loader = document.getElementById('loader2');
                if (loader != null) {
                    loader.style.display = "none";
                }
                return
            }
            var payload = JSON.stringify({
                'active': false
            })
            var new_text = "Resume bot";
            var alert_msg = "Your bot has been temporarily suspended"
        } else if ($("#suspend").text() === 'Resume bot') {
            var payload = JSON.stringify({
                'active' : true
            })
            var new_text = 'Suspend bot'
            var alert_msg = "Your bot has been restored"
        }
        request.put('/bot', payload)
        .then(() => {
            var loader = document.getElementById('loader2');
            if (loader != null) {
                loader.style.display = "none";
            }
            alert(alert_msg)
            $("#suspend").html('<i class="fa fa-spinner fa-spin" id="loader2"></i>' + new_text)
        })
        .catch((err) => {
            var loader = document.getElementById('loader2');
            if (loader != null) {
                loader.style.display = "none";
            }
            if (err.responseJSON) {
                alert(err.responseJSON)
            } else if (err.status === 401) {
                alert("Your session has expired, please log in again")
                window.location.href = 'login2.html'
            } else {
                alert("An error has occured please try again later")
            }
        })
    })
}

function editBot() {
    $("#edit").on('click', () => {
        var editForm = document.getElementById('edit-form')
        editForm.style.display = 'block';
    })
    $("#submit-edit-form").on('click', () => {
        var loader = document.getElementById('edit-loader');
        loader.style.display = 'block'
        var payload = JSON.stringify({
            'capital': parseInt($('#newCapital').val())
        })
        request.put('/bot', payload)
        .then(() => {
            alert("Your bot capital has been updated successfully")
            loader.style.display = 'none'
            var editForm = document.getElementById('edit-form')
            editForm.style.display = 'none'
        }).catch((err) => {
            loader.style.display = 'none'
            if (err.responseJSON) {
                alert(err.responseJSON)
            } else {
                alert("An error occured, please try again later")
            }
        })
    })
    $("#cancel-edit-form").on('click', () => {
        var editForm = document.getElementById('edit-form')
        editForm.style.display = 'none'
    })
}


Promise.all([getProfile(), refreshPage(), suspendBot(), editBot()])
.then(() => {
    var loader = document.getElementById('preloader');
	if (loader != null) {
		loader.style.display = "none";
	}
})
