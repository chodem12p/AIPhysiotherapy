$(document).ready(function(){
    //alert("new filter running!");
    var ft_content = $(".filter-card-content");
    var ca_icon = $("#caret-icon");

    $("#btn-filter-showhide").click(function() {
        if (ft_content.css("display") == "none") {
            ft_content.slideDown(400);
            ca_icon.removeClass("bi-caret-down");
            ca_icon.addClass("bi-caret-up");
        } else {
            ft_content.slideUp(400);
            ca_icon.removeClass("bi-caret-up");
            ca_icon.addClass("bi-caret-down");
        }
    });
});