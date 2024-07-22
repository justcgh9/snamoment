function check_progress(task_id) {
    const button = document.getElementById("btn_conv");
    button.addEventListener("click", function () {

        button.disabled = true;
    });

    function worker() {
        $.get('progress/' + task_id, function (data) {
            if (!isNaN(data)) { // If number
                button.disabled = true;
                if (data < 100) {

                    if (data > 0) {
                        button.textContent = data + "%";
                    } else {
                        button.textContent = "Loading..."
                    }

                }
                setTimeout(worker, 1000);
            } else { // Not number
                if (data === "no info") {

                } else if (data === "Error") {
                    button.textContent = "Error! Try again";
                } else {
                    console.log(window.location.origin + "/preview/" + data)
                    window.location.replace(window.location.origin + "/preview?video_file=" + data);
                }
            }


        })
    }

    worker()
}


$(document).ready(function () {
    console.log(window.location.search.substring(4))
    check_progress(window.location.search.substring(4));
});

