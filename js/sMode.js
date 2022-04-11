//<div id='btnsimple' class='col-3 btn btn-danger'>簡易介面</div>
$(document).ready(function () {
    var btnsimp = $('#insert-btnsimp');
    btnsimp.addClass("col-5");
    btnsimp.html("<i id='btnsimp-toggle-icon' class='bi bi-toggle-off'></i>簡易顯示");
    var icon = $('#btnsimp-toggle-icon');

    var aa = 1;
    btnsimp.click(function () {
        aa += 1;
        if (aa % 2 == 0) {
            icon.removeClass("bi-toggle-off");
            icon.addClass("bi-toggle-on");
            icon.css("color","green");
            $("img").not(".logo").hide();
        } else {
            icon.removeClass("bi-toggle-on");
            icon.addClass("bi-toggle-off");
            icon.css("color","black");
            $("img").not(".logo").show();
        }
    });
});
