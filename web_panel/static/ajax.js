$SCRIPT_ROOT = ""
function ajax_complete(data, status){
  if(status == "success"){
    var obj = $.parseJSON(data.responseText);
    $.each(obj, function (index, value){
      $( ".view" ).append("<tr><td>" + value.username + "</td><td>" + value.message + "</td></tr>")})
    }else{
        if(status != "notmodified"){alert(status)}
    }
}
function start_ajax(sid){
    setInterval(function(){
      $.ajax({
        complete:ajax_complete,
        method:"POST",
        url:$SCRIPT_ROOT + "/" + sid +"/ajax_api/"
})},2000)}
