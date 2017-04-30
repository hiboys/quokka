var refresh_captcha = function () {
  var jqxhr = $.ajax("/captcha/captcha_refresh/", {
    contentType : 'application/json',
    type: 'GET',
  })
  .done(function(data) {
    $("#captcha_img").attr("src", data.image_url);
    $("#captcha_key").attr("value", data.key);
  })
  .fail(function() {
    console.log("error refreshing captcha");
  });
};

$("#captcha_img").click(function(){
    refresh_captcha();
});
