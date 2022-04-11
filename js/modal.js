$(document).ready(function(){
    var modal = $(".modal");
    var modalInner = $(".modal-content");
    var id = "";
    var err = "ERROR: 無法存取紀錄詳情";
    
    function openModal(id) {
        modal.show(500);
        /* demo id, id format is ddmmyyyy_time
           id 應跟此 format 自動 gen
        */
        if (id == '02022022_1329') {
            /* demo data, LEMON backend */
            $("#modal-type").html("手部治療");
            $("#modal-date").html("2-2-2022, 星期三");
            $("#modal-start-time").html("13:29");
            $("#modal-end-time").html("14:02");
            $("#modal-duration").html("33m");
            $("#modal-comment").html("很好，大多姿勢都正確，改善建議伸直腰避免寒背。\nTest-二\nDebug-三\nDemo-四\nPrototype-五");
        } else if (id == "tutorial_vid" ) {
            console.log("tutorial video modal opened.");
        } else {
            console.log(err);
            $("#modal-type").html("---");
            $("#modal-date").html("---");
            $("#modal-start-time").html("---");
            $("#modal-end-time").html("---");
            $("#modal-duration").html("---");
            $("#modal-comment").html(err);
        }
    }
    window.openModal = openModal;
        
    $(".close").click(function() {
        modal.hide(250);
    });
});
