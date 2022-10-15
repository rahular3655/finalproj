{/* $("#add_b").click(function (e) {
    e.preventDefault();
    var nick_name = $(this).val();
    // GET AJAX request
    $.ajax({
        type: 'GET',
        url: "{% url 'add_cart' %}",
        data: {"nick_name": nick_name},
        success: function (response) {
            // if not valid user, alert the user
            if(!response["valid"]){
                alert("You cannot create a friend with same nick name");
                var nickName = $("#id_nick_name");
                nickName.val("")
                nickName.focus()
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}) */}


