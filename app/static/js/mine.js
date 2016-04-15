/**
 * Created by Administrator on 2016/3/12.
 */
$(function () {
    $('#myTab li:eq(1) a').tab('show');
});
$(function () {
    $('#myTab1 li:eq(1) a').tab('show');
});

$(document).ready(function(){
    $("a .rsp").hide()
    $(".section button").hide();
    $(".section .ttext").hide();
    $(".section").hover(function(){
            $(this).find(".ttext").stop().fadeTo(200,1);
        $(this).find(".rsp").stop().fadeTo(200,0.4)
            $(this).find("button").stop().fadeTo(200,1);


        }
        ,function(){
        $(this).find(".rsp").stop().fadeTo(200,0)
        $(this).find("button").stop().fadeTo(200,0)
            $(this).find(".ttext").stop().fadeTo(200,0)

        });

});

$(document).ready(function(){
    $("a .rrsp").hide()
    $(".section1 button").hide();
    $(".section1 .ttext1").hide();
    $(".section1").hover(function(){
            $(this).find(".ttext1").stop().fadeTo(200,1);
            $(this).find(".rrsp").stop().fadeTo(200,0.4)
            $(this).find("button").stop().fadeTo(200,1);
            $(".section1 .ttext2").hide();
        }
        ,function(){
            $(this).find(".rrsp").stop().fadeTo(200,0)
            $(this).find("button").stop().fadeTo(200,0)
            $(this).find(".ttext1").stop().fadeTo(200,0)
            $(this).find(".ttext2").stop().fadeTo(200,1);

        });

});

$(document).ready(function(){
    $("a .rsp").hide()
    $(".section2 button").hide();
    $(".section2 .ttext").hide();
    $(".section2").hover(function(){
            $(this).find(".ttext").stop().fadeTo(200,1);
            $(this).find(".rsp").stop().fadeTo(200,0.4)
            $(this).find("button").stop().fadeTo(200,1);
            $(".section2 .ttext3").hide();


        }
        ,function(){
            $(this).find(".rsp").stop().fadeTo(200,0)
            $(this).find("button").stop().fadeTo(200,0)
            $(this).find(".ttext").stop().fadeTo(200,0)
            $(this).find(".ttext3").stop().fadeTo(200,1);

        });

});

$(document).ready(function(){
    $("a .rsp").hide()
    $(".section6 button").hide();
    $(".section6 .ttext").hide();
    $(".section6").hover(function(){
            $(this).find(".ttext").stop().fadeTo(200,1);
            $(this).find(".rsp").stop().fadeTo(200,0.4)
            $(this).find("button").stop().fadeTo(200,1);
            $(".section6 .ttext3").hide();


        }
        ,function(){
            $(this).find(".rsp").stop().fadeTo(200,0)
            $(this).find("button").stop().fadeTo(200,0)
            $(this).find(".ttext").stop().fadeTo(200,0)
            $(this).find(".ttext3").stop().fadeTo(200,1);

        });

});




$(document).ready(function(){
    $(".sp .is").hide();
    $(".sp .is1").hide();
    $(".sp1").hover(function(){
            $(this).find(" .is").stop().fadeTo(200,1);
            $(this).find(" .is1").stop().fadeTo(200,1);



        }
        ,function(){
            $(this).find(".is").stop().fadeTo(200,0)
            $(this).find(".is1").stop().fadeTo(200,0)

        });

});
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})


