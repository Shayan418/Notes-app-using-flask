window.onload = function () {

    var timer = null;
    $('#username').keydown(function () {
        clearTimeout(timer);
        document.getElementById("usernameInfo").innerHTML = ""
        document.getElementById("usernameUpdate").setAttribute('disabled', '')
        timer = setTimeout(doStuff, 2000)
    });

    function doStuff() {

        let username = document.getElementById('username');

        if (username.value.length >= 4) {
            fetch(`${window.origin}/api/username`, {
                    method: "POST",
                    dentials: "include",
                    body: JSON.stringify(username.value),
                    cache: "no-cache",
                    headers: new Headers({
                        "content-type": "application/json"
                    })

                })
                .then(function (responce) {

                    if (responce.status != 200) {
                        console.log(`Responce bad : ${responce.status}`)
                    }

                    responce.json().then(function (data) {
                        if (data == 0) {
                            document.getElementById("usernameInfo").innerHTML = "username available"
                            document.getElementById("usernameInfo").style.color = "#00bf00";
                            document.getElementById("usernameUpdate").removeAttribute('disabled');
                        } else if (data == -1) {
                            document.getElementById("usernameInfo").innerHTML = "Use only alphabets and number"
                            document.getElementById("usernameInfo").style.color = "red";
                            document.getElementById("usernameUpdate").setAttribute('disabled', '');
                        } else {
                            document.getElementById("usernameInfo").innerHTML = "username not available"
                            document.getElementById("usernameInfo").style.color = "red";
                            document.getElementById("usernameUpdate").setAttribute('disabled', '');
                        }


                    })

                })
        }
        else{
            document.getElementById("usernameInfo").innerHTML = "username should be more than 4 characters"
            document.getElementById("usernameInfo").style.color = "red";
            document.getElementById("usernameUpdate").setAttribute('disabled', '');
        }
    }

};